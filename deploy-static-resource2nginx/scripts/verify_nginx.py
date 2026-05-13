#!/usr/bin/env python3
"""Verify the remote server's nginx serves the directory layout this skill expects.

Usage:
    python3 verify_nginx.py <project-dir>

Reads <project-dir>/server.config.json for SSH credentials. Checks:
    1. nginx binary is installed on the remote host.
    2. There exists at least one server block with:
         - listen 80 (or default port 80)
         - root <deploy.remote_root>   (default /var/www/apps)
         - try_files $uri $uri/ /index.html   (SPA fallback)

Exit codes:
    0 — verified OK, deploy can proceed
    1 — nginx is not installed, or nginx -T failed
    2 — nginx installed but config doesn't match — run setup_nginx.py
    3 — bad arguments / cannot load config

Designed to be both runnable directly (CLI) and importable (deploy.py calls
`verify(client, expected_root)`).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap; _bootstrap.ensure_venv()
from _lib import ensure_deps, fail, load_config, open_ssh, remote_exec


def dump_nginx_config(client) -> str | None:
    """Try several strategies to obtain the full merged nginx config text.

    Returns the config text, or None if nginx is not reachable / not installed.
    """
    rc, _, _ = remote_exec(client, "command -v nginx", check=False, quiet=True)
    if rc != 0:
        return None

    for cmd, use_sudo in [
        ("nginx -T 2>/dev/null", False),
        ("sudo -n nginx -T 2>/dev/null", False),
        ("cat /etc/nginx/nginx.conf /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*.conf 2>/dev/null", False),
        ("sudo -n sh -c 'cat /etc/nginx/nginx.conf /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*.conf 2>/dev/null'", False),
    ]:
        rc, out, _ = remote_exec(client, cmd, use_sudo=use_sudo, check=False, quiet=True)
        if rc == 0 and out.strip():
            return out
    return None


def iter_server_blocks(text: str):
    """Yield the body of each top-level `server { ... }` block."""
    i, n = 0, len(text)
    while i < n:
        idx = text.find("server", i)
        if idx == -1:
            return
        # 'server' must be a keyword: preceded by whitespace/start/};
        if idx > 0 and text[idx - 1] not in " \t\n;}":
            i = idx + 1
            continue
        j = idx + len("server")
        while j < n and text[j] in " \t\n":
            j += 1
        if j >= n or text[j] != "{":
            i = idx + 1
            continue
        depth = 1
        k = j + 1
        while k < n and depth > 0:
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            k += 1
        yield text[j + 1 : k - 1]
        i = k


def block_matches(body: str, expected_root: str) -> tuple[bool, list[str]]:
    """Return (matches, list-of-missing-requirements) for a server-block body."""
    missing = []

    # listen 80 — accept "listen 80", "listen [::]:80", default if no listen at all
    has_listen_directive = any(
        line.strip().startswith("listen ") or line.strip() == "listen;"
        for line in body.splitlines()
    )
    listens_80 = any(
        "listen" in line and ("80" in line.split("#")[0]) and "443" not in line.split("#")[0]
        for line in body.splitlines()
        if line.strip().startswith("listen")
    )
    if has_listen_directive and not listens_80:
        missing.append("listen 80")

    if expected_root not in body:
        missing.append(f"root {expected_root}")

    if "try_files" not in body or "/index.html" not in body or "$uri" not in body:
        missing.append("try_files $uri $uri/ /index.html (SPA fallback)")

    return (not missing, missing)


def verify(client, expected_root: str = "/var/www/apps") -> tuple[int, str]:
    """Check the remote nginx config. Returns (exit_code, message)."""
    config_text = dump_nginx_config(client)
    if config_text is None:
        return 1, (
            "nginx is not installed (or `nginx -T` produced no output even with sudo). "
            "Install nginx on the server, then run setup_nginx.py."
        )

    blocks = list(iter_server_blocks(config_text))
    if not blocks:
        return 2, "nginx is installed but no `server { ... }` blocks were found. Run setup_nginx.py."

    best_match_missing: list[str] | None = None
    for body in blocks:
        ok, missing = block_matches(body, expected_root)
        if ok:
            return 0, f"OK: a server block matches (root {expected_root}, listen 80, SPA fallback present)."
        if best_match_missing is None or len(missing) < len(best_match_missing):
            best_match_missing = missing

    detail = "; ".join(best_match_missing or ["unknown"])
    return 2, (
        f"No server block matches the expected layout. Closest block is missing: {detail}. "
        f"Run `python3 scripts/setup_nginx.py <project-dir>` to install the canonical config."
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_nginx.py <project-dir>", file=sys.stderr)
        return 3
    ensure_deps()

    project_dir = Path(argv[1]).resolve()
    if not project_dir.is_dir():
        fail(f"Not a directory: {project_dir}", code=3)

    cfg = load_config(project_dir)
    expected_root = cfg["deploy"]["remote_root"]

    client = open_ssh(cfg["server"])
    try:
        code, message = verify(client, expected_root)
    finally:
        client.close()

    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
