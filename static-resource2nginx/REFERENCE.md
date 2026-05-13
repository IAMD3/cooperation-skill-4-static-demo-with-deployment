# static-resource2nginx — Reference

## All config fields

The example template ships with only the four required fields. Every other field has a sensible default and can be added when you need it.

| Field | Default | Purpose |
| --- | --- | --- |
| `server.host` | *(required)* | Server IP or hostname. |
| `server.username` | *(required)* | SSH login user. |
| `server.password` | *(required, or use key)* | SSH password. Mutually exclusive with `private_key_path`. |
| `server.port` | `22` | SSH port. |
| `server.private_key_path` | `""` | Absolute path to a private key. Wins over `password` if both are set. |
| `server.private_key_passphrase` | `""` | Passphrase for the private key, if any. |
| `deploy.project_name` | *(required)* | Sub-directory name under `remote_root`. Also becomes the URL path. |
| `deploy.remote_root` | `/var/www/apps` | Nginx web root on the server. |
| `deploy.use_sudo` | `false` | Prefix remote `mkdir`/`rm`/`chmod` with `sudo`. Requires passwordless sudo. |
| `deploy.scheme` | `http` | Used only for the printed access URL — switch to `https` after you install a cert. |
| `build.skip_npm_install` | `false` | Skip `npm install` (useful for CI where deps are pre-installed). |
| `build.build_command` | `""` | Override the default `vite build` command. The skill still appends `--base=/<project_name>/`. |

**Security note:** `server.config.json` contains credentials. Add it to `.gitignore` before your first commit.

## Deep-link SPA routing under a sub-path

The pre-configured nginx block uses a single global fallback:

```
location / { try_files $uri $uri/ /index.html; }
```

When the project is served from `/myapp/`, a deep link like `/myapp/users/42` will:

1. Try `/var/www/apps/myapp/users/42` — miss.
2. Try `/var/www/apps/myapp/users/42/` — miss.
3. Fall back to `/var/www/apps/index.html` — **wrong index.html**, the project will not load.

Direct asset paths (`/myapp/`, `/myapp/index.html`, `/myapp/assets/foo.js`) work fine, so the landing page and its bundles load correctly. The break only affects refreshes / shared links on non-root routes.

**Workarounds (pick one):**

- **Hash routing** in Vue Router (`createWebHashHistory`). URLs look like `/myapp/#/users/42`. Works with the existing nginx block. Cheapest fix.
- **Per-project nginx location block** (requires root on the server):
  ```
  location /myapp/ { try_files $uri $uri/ /myapp/index.html; }
  ```
  Add one block per deployed project, reload nginx. Most correct fix.
- **Single-project-per-host** — drop `project_name` from the URL by setting `deploy.project_name` to `""` (the deploy script will upload directly to `/var/www/apps/`). Only works for one project per server.

## Authentication options

`server.password` and `server.private_key_path` are mutually exclusive. The deploy script prefers the private key when both are set.

- **Password auth** — simplest, but the server's `sshd_config` must have `PasswordAuthentication yes`.
- **Key auth** — set `server.private_key_path` to an absolute path (e.g. `/Users/you/.ssh/id_ed25519` or `C:\\Users\\you\\.ssh\\id_ed25519`). If the key is passphrase-protected, set `server.private_key_passphrase`.

## Remote permissions

The SSH user must be able to write to `deploy.remote_root` (default `/var/www/apps`). One-time setup on the server (run as root):

```
mkdir -p /var/www/apps
chown -R <ssh-user>:<ssh-user> /var/www/apps
chmod 755 /var/www/apps
```

If the SSH user cannot own the directory, use `deploy.use_sudo: true` in the config — the script will prefix `mkdir`/`rm`/`mv` with `sudo` (requires passwordless sudo for those commands).

## HTTPS

The assumed nginx block listens on port 80 only. For HTTPS:

1. Issue a cert (`certbot --nginx -d your.domain`).
2. Update the URL the skill prints to use `https://`.

The deploy flow itself does not change.

## Vite `base` and why it matters

The script invokes `npx vite build --base=/<project_name>/` so all asset URLs inside `index.html` are prefixed correctly. If you build manually without `--base`, asset requests will hit `/assets/foo.js` instead of `/myapp/assets/foo.js` and 404 against the wrong project's directory.

## Common errors

| Symptom | Cause | Fix |
| --- | --- | --- |
| `paramiko.ssh_exception.AuthenticationException` | Wrong password / key / username | Verify `server.config.json` |
| `Permission denied` on remote `mkdir` | SSH user lacks write to `/var/www/apps` | See "Remote permissions" above |
| 403 in browser | nginx user can't read uploaded files | `chmod -R 755` the project dir on the server |
| Blank page, 404s on `/assets/...` | Build done without `--base` | Re-run `deploy.py` — it sets `--base` for you |
| `Connection refused` | Firewall, wrong port, or sshd not running | Check `server.port` and server firewall |

## What the deploy script does, step by step

1. Loads `server.config.json` from the project directory.
2. Validates required fields (same checks as `check_config.py`).
3. Runs `npm install` if `node_modules/` is missing.
4. Runs `npx vite build --base=/<project_name>/` (or `/` if `project_name` is empty).
5. Opens an SSH connection (paramiko).
6. Ensures `<remote_root>/<project_name>/` exists (creates if missing).
7. Wipes the **contents** of that directory (not the directory itself) to avoid stale assets.
8. Uploads every file from local `dist/` via SCP, preserving subdirectories.
9. Prints `http://<host>/<project_name>/`.

The script is idempotent — re-running replaces the project's directory contents only. Other projects under `remote_root` are not touched.
