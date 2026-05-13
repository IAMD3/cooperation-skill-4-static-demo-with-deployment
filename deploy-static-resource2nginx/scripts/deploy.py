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

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap; _bootstrap.ensure_venv()
from _lib import ensure_deps, fail, load_config, open_ssh, quote, remote_exec
import verify_nginx


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


def posix_join(*parts: str) -> str:
    """Join paths using forward slashes (remote is POSIX, regardless of local OS)."""
    cleaned = [p.strip("/") for p in parts if p]
    leading = "/" if parts and parts[0].startswith("/") else ""
    return leading + "/".join(cleaned)


def deploy_dist(client, dist_dir: Path, remote_dir: str, use_sudo: bool) -> None:
    from scp import SCPClient

    if remote_dir.rstrip("/") in ("", "/", "/var", "/var/www", "/var/www/apps"):
        fail(f"Refusing to deploy directly to '{remote_dir}'. Set deploy.project_name to a non-empty value.")

    remote_exec(client, f"mkdir -p {quote(remote_dir)}", use_sudo=use_sudo)
    wipe_cmd = f"rm -rf {quote(remote_dir)}/* {quote(remote_dir)}/.[!.]*"
    remote_exec(client, f"sh -c {quote(wipe_cmd)} || true", use_sudo=use_sudo, check=False)

    print(f"Uploading {dist_dir} → {remote_dir} ...")
    with SCPClient(client.get_transport()) as scp_client:
        for entry in sorted(dist_dir.iterdir()):
            scp_client.put(str(entry), remote_path=remote_dir, recursive=True, preserve_times=True)

    remote_exec(client, f"chmod -R a+rX {quote(remote_dir)}", use_sudo=use_sudo)


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
    remote_root = deploy["remote_root"]

    # Pre-flight: verify remote nginx unless explicitly skipped.
    if not deploy.get("skip_nginx_verify"):
        print("Pre-flight: verifying remote nginx config ...")
        client = open_ssh(server)
        try:
            code, message = verify_nginx.verify(client, remote_root)
        finally:
            client.close()
        print(message)
        if code != 0:
            print()
            print("Pre-flight failed. Either:")
            print(f"  - Run `python3 scripts/setup_nginx.py {project_dir}` to install the canonical nginx config, OR")
            print("  - Set `deploy.skip_nginx_verify: true` in server.config.json if you know what you're doing.")
            return code

    dist = build_project(project_dir, project_name, cfg.get("build", {}))

    remote_dir = posix_join(remote_root, project_name) if project_name else remote_root
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
