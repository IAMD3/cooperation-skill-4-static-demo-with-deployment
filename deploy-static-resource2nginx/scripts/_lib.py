"""Shared helpers for the deploy-static-resource2nginx scripts.

All three scripts (deploy.py, verify_nginx.py, setup_nginx.py) read the same
server.config.json and open SSH the same way. This module owns those pieces.
"""
from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import NoReturn


def fail(msg: str, code: int = 1) -> NoReturn:
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
    deploy.setdefault("skip_nginx_verify", False)
    server.setdefault("port", 22)
    return data


def open_ssh(server: dict):
    """Open an SSH connection using the credentials in the server section of config."""
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


def remote_exec(client, cmd: str, *, use_sudo: bool = False, check: bool = True, quiet: bool = False) -> tuple[int, str, str]:
    """Run a command on the remote host. Returns (exit_code, stdout, stderr).

    If check=True (default), exits the script on non-zero return.
    """
    full = f"sudo {cmd}" if use_sudo else cmd
    if not quiet:
        print(f"remote$ {full}")
    stdin, stdout, stderr = client.exec_command(full)
    rc = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if check and rc != 0:
        fail(f"Remote command failed (exit {rc}): {full}\nstderr: {err.strip()}")
    return rc, out, err


def quote(value: str) -> str:
    """Shell-quote a string for safe interpolation into remote shell commands."""
    return shlex.quote(value)
