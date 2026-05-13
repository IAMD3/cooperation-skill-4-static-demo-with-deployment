---
name: deploy-static-resource2nginx
description: Build a Vue 3 + Vite static project (typically one produced by static-demo4domain-expert) and deploy the built dist/ to a remote nginx server via SSH/SCP, into a per-project sub-directory under the nginx web root. Verifies the remote nginx config first, and can install a canonical config if none exists. Use when the user wants to ship a static demo to a server, deploy a Vue/Vite build to nginx, upload a dist folder over SSH, set up nginx for static hosting, or says "deploy this demo", "push to nginx", "upload to server", "deploy-static-resource2nginx".
---

# deploy-static-resource2nginx

Build a Vite static project and deploy its `dist/` to a pre-configured nginx host. Multiple projects can coexist on one server, each under `/var/www/apps/<project-name>/`.

## Quick start

Strictly-ordered four phases — never skip phase 1 or 2:

1. **Verify local config** — run `python3 scripts/check_config.py <project-dir>/server.config.json`. If the file is missing or any required field is blank, **STOP** and ask the user to fill it in using [templates/server.config.example.json](templates/server.config.example.json) as the starting point.

2. **Verify remote nginx** — run `python3 scripts/verify_nginx.py <project-dir>`. This SSHes in and checks that nginx is installed and a server block exists with `listen 80`, `root <remote_root>`, and the SPA `try_files` fallback. Three outcomes:
   - **Exit 0** — config matches, proceed to phase 3.
   - **Exit 2** — nginx is installed but config doesn't match. Ask the user "Install the canonical nginx config now? It will back up your existing default site first." If yes, run `python3 scripts/setup_nginx.py <project-dir>`. After it completes, re-run verify_nginx, then proceed.
   - **Exit 1** — nginx isn't installed. Run `python3 scripts/setup_nginx.py <project-dir>` (it will offer to install nginx via apt/yum).

3. **Build & upload** — run `python3 scripts/deploy.py <project-dir>`. The script repeats the verify step as a pre-flight, then builds with the correct `--base` flag, uploads `dist/`, and prints the access URL.

4. **Report** — show the user the access URL printed by the script (form: `http://{host}/{project_name}/`) and the [REFERENCE.md](REFERENCE.md) note on deep-link routing.

## Assumed remote nginx config

`setup_nginx.py` installs (or verify_nginx.py checks for) this block:

```
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    root /var/www/apps;
    index index.html index.htm index.nginx-debian.html;
    server_name _;
    location / { try_files $uri $uri/ /index.html; }
}
```

Each deployed project lands at `/var/www/apps/<project_name>/`, accessed at `http://<host>/<project_name>/`.

## Config file

Every project gets its own `server.config.json` (copy from [templates/server.config.example.json](templates/server.config.example.json)). Required fields: `server.host`, `server.username`, one of `server.password` / `server.private_key_path`, and `deploy.project_name`. All other fields have defaults — see [REFERENCE.md](REFERENCE.md) "All config fields".

**Never commit `server.config.json` to git.**

## Credential handling in prompts

When talking to the user about the config, **never echo actual credential values**:

- `server.password`
- `server.private_key_passphrase`
- contents of any file pointed to by `server.private_key_path`

Rules:
- When asking the user to fill in or confirm credentials, refer to fields by **name only** (e.g. "fill in `server.password`"). Do not read the value back, even as a "did you mean X?" check.
- When summarizing or quoting the config in chat, redact secret fields as `"***"`. Never paste the raw JSON containing them.
- If a script error happens to surface a password (e.g. in a traceback), strip it before quoting the output back.
- This applies in every channel: chat replies, plan summaries, commit messages, PR descriptions. Non-secret fields (`host`, `username`, `port`, `project_name`, paths) are fine to echo.

## Prerequisites

- Python 3.8+ on the user's machine (Windows or macOS). If `python3` is not found, ask the user to install it from [python.org](https://www.python.org/downloads/) and re-run.
- `node` + `npm` in PATH (for the Vite build step). Already present if the user generated the project with `static-demo4domain-expert`.
- An SSH-reachable server. If nginx isn't installed or configured, `setup_nginx.py` handles it (requires root or passwordless sudo for that one-time setup).

**Python libraries (paramiko, scp) install themselves.** The first time any script runs, `_bootstrap.py` creates a local `.venv` inside the skill dir and `pip install`s the two libs into it. Subsequent runs re-exec instantly under that venv. The user never types `pip install`.

## Multiple projects on one server

Each project's `server.config.json` sets a unique `deploy.project_name`. Deploy creates `/var/www/apps/<project_name>/` if absent and overwrites only that sub-directory — other projects on the server are untouched.

## Troubleshooting & advanced

See [REFERENCE.md](REFERENCE.md) for: the script reference, SPA deep-link routing limitations under sub-paths, key-based auth, sudo-less permissions setup, HTTPS upgrade notes, and common SSH/SCP errors.
