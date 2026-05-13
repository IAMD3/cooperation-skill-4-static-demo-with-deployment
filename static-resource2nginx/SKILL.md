---
name: static-resource2nginx
description: Build a Vue 3 + Vite static project (typically one produced by static-demo4domain-expert) and deploy the built dist/ to a remote nginx server via SSH/SCP, into a per-project sub-directory under the nginx web root. Use when the user wants to ship a static demo to a server, deploy a Vue/Vite build to nginx, upload a dist folder over SSH, or says "deploy this demo", "push to nginx", "upload to server", "static-resource2nginx".
---

# static-resource2nginx

Build a Vite static project and deploy its `dist/` to a pre-configured nginx host. Multiple projects can coexist on one server, each under `/var/www/apps/<project-name>/`.

## Quick start

Strictly-ordered three phases — never skip phase 1:

1. **Verify config** — run `python3 scripts/check_config.py <project-dir>/server.config.json`. If the file is missing or any required field is blank, **STOP** and ask the user to fill it in using [templates/server.config.example.json](templates/server.config.example.json) as the starting point. Do not proceed.
2. **Build & upload** — run `python3 scripts/deploy.py <project-dir>`. The script builds with the correct `--base` flag, opens an SSH session, ensures the remote directory exists, uploads `dist/`, and prints the access URL.
3. **Report** — show the user the access URL printed by the script (form: `http://{host}/{project_name}/`) and the [REFERENCE.md](REFERENCE.md) note on deep-link routing.

## Assumed remote nginx config

The server already serves:

```
server {
    listen 80;
    server_name _;
    root /var/www/apps;
    location / { try_files $uri $uri/ /index.html; }
}
```

Each deployed project lands at `/var/www/apps/<project_name>/`, accessed at `http://<host>/<project_name>/`.

## Config file

Every project gets its own `server.config.json` (copy from [templates/server.config.example.json](templates/server.config.example.json)). Required fields: `server.host`, `server.username`, one of `server.password` / `server.private_key_path`, and `deploy.project_name`. See the template header for details.

**Never commit `server.config.json` to git.** Add it to `.gitignore` before deploying.

## Prerequisites

- Python 3.8+ on the user's machine (Windows or macOS)
- `pip install paramiko scp` (one-time; the deploy script will offer to run it if missing)
- `node` + `npm` in PATH (for the Vite build step)
- An SSH-reachable server with the nginx block above already running

## Multiple projects on one server

Each project's `server.config.json` sets a unique `deploy.project_name`. The deploy script creates `/var/www/apps/<project_name>/` if absent and overwrites only that sub-directory — other projects on the server are untouched.

## Troubleshooting & advanced

See [REFERENCE.md](REFERENCE.md) for: SPA deep-link routing limitations under sub-paths, key-based auth, sudo-less permissions setup, HTTPS upgrade notes, and common SSH/SCP errors.
