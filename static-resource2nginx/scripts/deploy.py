#!/usr/bin/env python3
"""Build a Vite project and deploy its dist/ to a remote nginx host over SSH.

Usage:
    python3 deploy.py <project-dir>

Reads <project-dir>/server.config.json. See templates/server.config.example.json.
Cross-platform: works on Windows and macOS with Python 3.8+.

Dependencies: paramiko, scp
    pip install paramiko scp
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def fail(msg: str, code: int = 1) -> "NoReturn":  # type: ignore[name-defined]
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_deps() -> None:
    try:
        import paramiko  # noqa: F401
        import scp  # noqa: F401
    except ImportError:
        print("Missing dependencies. Install with:")
        print("    pip install paramiko scp")
        sys.exit(1)


def load_config(project_dir: Path) -> dict:
    cfg_path = project_dir / "server.config.json"
    if not cfg_path.exists():
        fail(
            f"{cfg_path} not found. Copy templates/server.config.example.json to "
            f"this path and fill it in before deploying."
        )
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in {cfg_path}: {e}")

    server = data.get("server", {})
    deploy = data.get("deploy", {})

    missing = []
    if not (server.get("host") or "").strip():
        missing.append("server.host")
    if not (server.get("username") or "").strip():
        missing.append("server.username")
    if not (server.get("password") or "").strip() and not (server.get("private_key_path") or "").strip():
        missing.append("server.password OR server.private_key_path")
    if "project_name" not in deploy:
        missing.append("deploy.project_name")
    if missing:
        fail("server.config.json incomplete. Missing: " + ", ".join(missing))

    deploy.setdefault("remote_root", "/var/www/apps")
    deploy.setdefault("use_sudo", False)
    deploy.setdefault("scheme", "http")
    server.setdefault("port", 22)
    return data


def find_npm() -> str:
    """Return an absolute path to npm, accounting for Windows .cmd shims."""
    candidate = shutil.which("npm")
    if candidate:
        return candidate
    if os.name == "nt":
        for ext in (".cmd", ".bat", ".exe"):
            candidate = shutil.which("npm" + ext)
            if candidate:
                return candidate
    fail("npm not found in PATH. Install Node.js and retry.")
    return ""  # unreachable


def run(cmd: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(shlex.quote(c) for c in cmd)}  (cwd={cwd})")
    # shell=False; on Windows shutil.which resolves the .cmd shim path.
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode != 0:
        fail(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}")


def build_project(project_dir: Path, project_name: str, build_cfg: dict) -> Path:
    npm = find_npm()
    if not build_cfg.get("skip_npm_install") and not (project_dir / "node_modules").exists():
        run([npm, "install"], project_dir)

    base = f"/{project_name}/" if project_name else "/"
    custom = (build_cfg.get("build_command") or "").strip()
    if custom:
        cmd = custom.split() + [f"--base={base}"]
    else:
        cmd = [npm, "exec", "--", "vite", "build", f"--base={base}"]
    run(cmd, project_dir)

    dist = project_dir / "dist"
    if not dist.exists():
        fail(f"Build finished but {dist} was not produced.")
    return dist


def open_ssh(server: dict):
    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    key_path = (server.get("private_key_path") or "").strip()
    passphrase = (server.get("private_key_passphrase") or "").strip() or None
    if key_path:
        print(f"Connecting to {server['host']}:{server['port']} via key auth ({key_path}) ...")
        client.connect(
            hostname=server["host"],
            port=int(server["port"]),
            username=server["username"],
            key_filename=key_path,
            passphrase=passphrase,
            timeout=30,
            allow_agent=False,
            look_for_keys=False,
        )
    else:
        print(f"Connecting to {server['host']}:{server['port']} via password auth ...")
        client.connect(
            hostname=server["host"],
            port=int(server["port"]),
            username=server["username"],
            password=server["password"],
            timeout=30,
            allow_agent=False,
            look_for_keys=False,
        )
    return client


def remote_exec(client, cmd: str, *, use_sudo: bool = False) -> str:
    full = f"sudo {cmd}" if use_sudo else cmd
    print(f"remote$ {full}")
    stdin, stdout, stderr = client.exec_command(full)
    rc = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if rc != 0:
        fail(f"Remote command failed (exit {rc}): {full}\nstderr: {err.strip()}")
    return out


def posix_join(*parts: str) -> str:
    """Join paths using forward slashes (remote is POSIX, regardless of local OS)."""
    cleaned = [p.strip("/") for p in parts if p]
    leading = "/" if parts and parts[0].startswith("/") else ""
    return leading + "/".join(cleaned)


def deploy_dist(client, dist_dir: Path, remote_dir: str, use_sudo: bool) -> None:
    from scp import SCPClient

    # Validate remote_dir is non-trivial — refuse to wipe / or /var/www/apps itself.
    if remote_dir.rstrip("/") in ("", "/", "/var", "/var/www", "/var/www/apps"):
        fail(f"Refusing to deploy directly to '{remote_dir}'. Set deploy.project_name to a non-empty value.")

    # Ensure remote dir exists, then clear its contents.
    remote_exec(client, f"mkdir -p {shlex.quote(remote_dir)}", use_sudo=use_sudo)
    remote_exec(client, f"sh -c {shlex.quote(f'rm -rf {shlex.quote(remote_dir)}/* {shlex.quote(remote_dir)}/.[!.]*' )} || true", use_sudo=use_sudo)

    print(f"Uploading {dist_dir} → {remote_dir} ...")
    with SCPClient(client.get_transport()) as scp_client:
        # Upload every entry inside dist/, not dist itself.
        for entry in sorted(dist_dir.iterdir()):
            scp_client.put(str(entry), remote_path=remote_dir, recursive=True, preserve_times=True)

    # Make sure nginx (typically www-data) can read everything.
    remote_exec(client, f"chmod -R a+rX {shlex.quote(remote_dir)}", use_sudo=use_sudo)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: deploy.py <project-dir>", file=sys.stderr)
        return 2

    ensure_deps()

    project_dir = Path(argv[1]).resolve()
    if not project_dir.is_dir():
        fail(f"Not a directory: {project_dir}")
    if not (project_dir / "package.json").exists():
        fail(f"No package.json in {project_dir} — is this a Vite project?")

    cfg = load_config(project_dir)
    server = cfg["server"]
    deploy = cfg["deploy"]
    project_name = deploy["project_name"].strip().strip("/")

    dist = build_project(project_dir, project_name, cfg.get("build", {}))

    remote_dir = posix_join(deploy["remote_root"], project_name) if project_name else deploy["remote_root"]
    client = open_ssh(server)
    try:
        deploy_dist(client, dist, remote_dir, use_sudo=bool(deploy.get("use_sudo")))
    finally:
        client.close()

    scheme = deploy.get("scheme", "http")
    host = server["host"]
    path = f"/{project_name}/" if project_name else "/"
    url = f"{scheme}://{host}{path}"
    print()
    print("=" * 60)
    print(f"DEPLOYED: {project_name or '(root)'}")
    print(f"  Remote: {remote_dir}")
    print(f"  Access: {url}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
