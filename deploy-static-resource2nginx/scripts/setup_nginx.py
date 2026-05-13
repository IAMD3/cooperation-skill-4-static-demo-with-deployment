#!/usr/bin/env python3
"""Install the canonical nginx site config on the remote host.

Usage:
    python3 setup_nginx.py <project-dir>           # interactive, asks before changing
    python3 setup_nginx.py <project-dir> --yes     # non-interactive (CI / scripted)

What it does, in order:
    1. Detects nginx layout (Debian/Ubuntu sites-enabled vs. RHEL conf.d).
    2. Ensures <remote_root> exists and is writable by the SSH user.
    3. Backs up existing default-site config to <path>.bak.<timestamp>.
    4. Writes the canonical server block (listen 80, root <remote_root>, SPA fallback).
    5. Runs `nginx -t`. If invalid, restores the backup and exits non-zero.
    6. Reloads nginx (`systemctl reload nginx`, fallback `nginx -s reload`).

Requires either the SSH user to be root, or passwordless sudo for nginx-related
commands. The script will use `sudo -n` automatically when needed.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bootstrap; _bootstrap.ensure_venv()
from _lib import ensure_deps, fail, load_config, open_ssh, quote, remote_exec


CANONICAL_BLOCK_TEMPLATE = """server {{
    listen 80 default_server;
    listen [::]:80 default_server;

    root {root};
    index index.html index.htm index.nginx-debian.html;

    server_name _;

    location / {{
        try_files $uri $uri/ /index.html;
    }}
}}
"""


def needs_sudo(client) -> bool:
    """Return True if the SSH user is not root and needs sudo for nginx ops."""
    rc, out, _ = remote_exec(client, "id -u", check=False, quiet=True)
    return not (rc == 0 and out.strip() == "0")


def check_sudo_ok(client) -> None:
    rc, _, err = remote_exec(client, "sudo -n true", check=False, quiet=True)
    if rc != 0:
        fail(
            "This script needs root or passwordless sudo on the remote host. "
            "Either log in as root, or grant the SSH user passwordless sudo for: "
            "nginx, tee, mkdir, chown, rm, ln, systemctl. "
            f"sudo error: {err.strip()}"
        )


def detect_layout(client, use_sudo: bool) -> dict:
    """Decide where to put the site config.

    Returns dict with keys: site_path (where to write), enable_symlink (or None),
    default_to_disable (existing default symlink to remove, or None), reload_cmd.
    """
    rc, _, _ = remote_exec(client, "test -d /etc/nginx/sites-enabled", use_sudo=use_sudo, check=False, quiet=True)
    has_sites_enabled = rc == 0

    if has_sites_enabled:
        return {
            "site_path": "/etc/nginx/sites-available/static-apps",
            "enable_symlink": "/etc/nginx/sites-enabled/static-apps",
            "default_to_disable": "/etc/nginx/sites-enabled/default",
        }
    return {
        "site_path": "/etc/nginx/conf.d/static-apps.conf",
        "enable_symlink": None,
        "default_to_disable": "/etc/nginx/conf.d/default.conf",
    }


def confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        print(f"{prompt} [auto-yes]")
        return True
    answer = input(f"{prompt} [y/N] ").strip().lower()
    return answer in ("y", "yes")


def backup(client, use_sudo: bool, path: str) -> str | None:
    """If `path` exists, copy it to <path>.bak.<timestamp>. Returns the backup path or None."""
    rc, _, _ = remote_exec(client, f"test -e {quote(path)}", use_sudo=use_sudo, check=False, quiet=True)
    if rc != 0:
        return None
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup_path = f"{path}.bak.{stamp}"
    remote_exec(client, f"cp -a {quote(path)} {quote(backup_path)}", use_sudo=use_sudo)
    return backup_path


def restore(client, use_sudo: bool, original: str, backup_path: str) -> None:
    remote_exec(client, f"mv -f {quote(backup_path)} {quote(original)}", use_sudo=use_sudo, check=False)


def write_remote_file(client, use_sudo: bool, path: str, content: str) -> None:
    """Write `content` to `path` on the remote, atomically via a temp file."""
    tmp = f"/tmp/static-apps.{int(time.time())}.{os.getpid()}"
    sftp = client.open_sftp()
    try:
        with sftp.open(tmp, "w") as f:
            f.write(content)
        sftp.chmod(tmp, 0o644)
    finally:
        sftp.close()
    remote_exec(client, f"mv {quote(tmp)} {quote(path)}", use_sudo=use_sudo)
    remote_exec(client, f"chown root:root {quote(path)} && chmod 644 {quote(path)}", use_sudo=use_sudo)


def ensure_remote_root(client, use_sudo: bool, ssh_user: str, root_dir: str) -> None:
    remote_exec(client, f"mkdir -p {quote(root_dir)}", use_sudo=use_sudo)
    remote_exec(client, f"chown -R {quote(ssh_user)}:{quote(ssh_user)} {quote(root_dir)}", use_sudo=use_sudo)
    remote_exec(client, f"chmod 755 {quote(root_dir)}", use_sudo=use_sudo)


def reload_nginx(client, use_sudo: bool) -> None:
    rc, _, _ = remote_exec(client, "systemctl reload nginx", use_sudo=use_sudo, check=False)
    if rc == 0:
        return
    rc, _, err = remote_exec(client, "nginx -s reload", use_sudo=use_sudo, check=False)
    if rc != 0:
        fail(f"Could not reload nginx via systemctl or `nginx -s reload`: {err.strip()}")


def install_nginx_if_missing(client, use_sudo: bool, assume_yes: bool) -> None:
    rc, _, _ = remote_exec(client, "command -v nginx", check=False, quiet=True)
    if rc == 0:
        return
    if not confirm("nginx is not installed on the remote. Install it now (apt or yum)?", assume_yes):
        fail("nginx is required. Install it manually, then re-run this script.")

    # Try apt (Debian/Ubuntu) then yum/dnf (RHEL/CentOS/Fedora).
    rc, _, _ = remote_exec(client, "command -v apt-get", check=False, quiet=True)
    if rc == 0:
        remote_exec(client, "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y nginx", use_sudo=use_sudo)
        return
    rc, _, _ = remote_exec(client, "command -v dnf", check=False, quiet=True)
    if rc == 0:
        remote_exec(client, "dnf install -y nginx", use_sudo=use_sudo)
        return
    rc, _, _ = remote_exec(client, "command -v yum", check=False, quiet=True)
    if rc == 0:
        remote_exec(client, "yum install -y nginx", use_sudo=use_sudo)
        return
    fail("Could not find apt-get, dnf, or yum. Install nginx manually, then re-run.")


def main(argv: list[str]) -> int:
    assume_yes = "--yes" in argv or "-y" in argv
    args = [a for a in argv[1:] if a not in ("--yes", "-y")]
    if len(args) != 1:
        print("usage: setup_nginx.py <project-dir> [--yes]", file=sys.stderr)
        return 2

    ensure_deps()

    project_dir = Path(args[0]).resolve()
    if not project_dir.is_dir():
        fail(f"Not a directory: {project_dir}")

    cfg = load_config(project_dir)
    server = cfg["server"]
    deploy = cfg["deploy"]
    ssh_user = server["username"]
    root_dir = deploy["remote_root"]

    client = open_ssh(server)
    try:
        use_sudo = needs_sudo(client)
        if use_sudo:
            check_sudo_ok(client)

        install_nginx_if_missing(client, use_sudo, assume_yes)

        layout = detect_layout(client, use_sudo)
        config_content = CANONICAL_BLOCK_TEMPLATE.format(root=root_dir)

        print()
        print("=== Plan ===")
        print(f"  Ensure remote root      : {root_dir}  (owner -> {ssh_user})")
        if layout["default_to_disable"]:
            print(f"  Disable conflicting site : {layout['default_to_disable']}  (backed up first)")
        print(f"  Write site config        : {layout['site_path']}")
        if layout["enable_symlink"]:
            print(f"  Enable via symlink       : {layout['enable_symlink']}")
        print(f"  Validate                 : nginx -t")
        print(f"  Reload                   : systemctl reload nginx (fallback: nginx -s reload)")
        print()
        print("--- nginx server block to install ---")
        print(config_content)
        if not confirm("Proceed?", assume_yes):
            print("Aborted by user. No changes were made.")
            return 1

        ensure_remote_root(client, use_sudo, ssh_user, root_dir)

        # Back up anything we are about to displace.
        default_backup = None
        if layout["default_to_disable"]:
            default_backup = backup(client, use_sudo, layout["default_to_disable"])
        site_backup = backup(client, use_sudo, layout["site_path"])
        symlink_backup = None
        if layout["enable_symlink"]:
            symlink_backup = backup(client, use_sudo, layout["enable_symlink"])

        # Disable the existing default site (Debian uses a symlink; RHEL uses the file itself).
        if layout["default_to_disable"]:
            remote_exec(client, f"rm -f {quote(layout['default_to_disable'])}", use_sudo=use_sudo, check=False)

        # Write the new site config and enable it.
        write_remote_file(client, use_sudo, layout["site_path"], config_content)
        if layout["enable_symlink"]:
            remote_exec(client, f"ln -sf {quote(layout['site_path'])} {quote(layout['enable_symlink'])}", use_sudo=use_sudo)

        # Validate.
        rc, _, err = remote_exec(client, "nginx -t", use_sudo=use_sudo, check=False)
        if rc != 0:
            print(f"nginx -t FAILED:\n{err}", file=sys.stderr)
            print("Rolling back ...", file=sys.stderr)
            if site_backup:
                restore(client, use_sudo, layout["site_path"], site_backup)
            else:
                remote_exec(client, f"rm -f {quote(layout['site_path'])}", use_sudo=use_sudo, check=False)
            if layout["enable_symlink"]:
                if symlink_backup:
                    restore(client, use_sudo, layout["enable_symlink"], symlink_backup)
                else:
                    remote_exec(client, f"rm -f {quote(layout['enable_symlink'])}", use_sudo=use_sudo, check=False)
            if default_backup:
                restore(client, use_sudo, layout["default_to_disable"], default_backup)
            fail("nginx config validation failed; rolled back. See stderr above for details.")

        reload_nginx(client, use_sudo)

        print()
        print("=" * 60)
        print("nginx is now configured for deploy-static-resource2nginx.")
        print(f"  Web root  : {root_dir}")
        print(f"  Site file : {layout['site_path']}")
        if default_backup:
            print(f"  Old default backed up at: {default_backup}")
        print("You can now run `python3 scripts/deploy.py <project-dir>`.")
        print("=" * 60)
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
