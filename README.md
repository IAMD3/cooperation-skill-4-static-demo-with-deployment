# Cooperation Skills

**Language / 语言:** English | [中文](./README.zh-CN.md)

> Built as **Claude Code skills** (the `SKILL.md` convention). The prompts and scripts are plain Markdown + Python, so they work just as well in other coding agents — **Cursor, Windsurf, Cline, Aider, Cody**, etc. — by pointing the agent at `SKILL.md` as a rule / context file (see [Install](#install-one-time)).

## The use case

> A salesperson — or any **domain expert** who knows the product but doesn't code — needs a working demo page to show a client tomorrow.

These two skills hand them the full pipeline:

1. **Generate.** They sit with Claude, get interviewed about the product in their own words, and walk away with a polished, runnable Vue 3 + Vite site built from their answers — no design brief, no developer time.
2. **Host.** One command later, the site is live at `http://<their-server>/<demo-name>/`. They paste the link into an email and the client opens it on any device.
3. **Hand off.** The generated project ships with real source code plus a `README.md` and `CONTEXT.md` that capture the salesperson's pitch, terminology, and intent. A developer who opens the repo next week can understand the demo without re-interviewing anyone, and turn it into a real feature.

The same server can host as many demos as the team needs — each one isolated under its own URL path — so a salesperson can build out a whole portfolio over time without involving infra.

## The two skills

| Skill | What it does |
| --- | --- |
| [`static-demo4domain-expert`](./static-demo4domain-expert) | Interviews a salesperson, then scaffolds a polished, runnable Vue 3 + Vite demo from their answers — including `README.md` and `CONTEXT.md` so developers can pick up the project later. |
| [`deploy-static-resource2nginx`](./deploy-static-resource2nginx) | Builds that Vue project and uploads it to a remote nginx server. Each demo lives at `http://<server>/<project-name>/`. |

You use them in order: **build → deploy**. Total time: about 15 minutes for the first demo, under 1 minute for subsequent re-deploys.

---

## Install (one time)

**Claude Code** — copy both folders into your skills directory:

```bash
cp -R static-demo4domain-expert     ~/.claude/skills/
cp -R deploy-static-resource2nginx  ~/.claude/skills/
```

**Other agents** (Cursor, Windsurf, Cline, Aider, Cody, …) — clone the repo somewhere and point your agent at each skill's `SKILL.md` as a rule / context / system-prompt file. The agent then runs the same `scripts/*.py` from that folder. Examples:

- **Cursor** — drop `SKILL.md` content into `.cursor/rules/*.mdc` (or attach the file via "Add Context")
- **Windsurf** — add the folder to your workspace and reference `SKILL.md` in `.windsurfrules`
- **Cline / Aider** — pass `SKILL.md` as a system prompt or `/read` it at session start

For the deploy step you also need Python 3.8+ (works on macOS and Windows). The required libraries (`paramiko`, `scp`) install themselves into a local venv the first time you run the skill — you don't have to `pip install` anything.

That's the entire toolchain.

---

## Step 1 — Build the demo

In Claude Code, type:

```
/static-demo4domain-expert
```

The skill will:

1. Ask which language to use (English / 中文 / etc.).
2. Walk you through 5 short batches of grilling-style questions about your product, audience, and pitch.
3. Confirm a numbered summary with you.
4. Scaffold a Vue 3 + Vite + Tailwind project in a directory of your choice, run `npm install`, and print the dev-server command.

You end up with a folder like `~/demos/acme-demo/` that runs locally with `npm run dev`.

---

## Step 2 — Deploy the demo

In the same project directory, create one file: **`server.config.json`**. The minimum config is just four fields:

```json
{
  "server": {
    "host": "your-server.example.com",
    "username": "ubuntu",
    "password": "your-ssh-password"
  },
  "deploy": {
    "project_name": "acme-demo"
  }
}
```

That's it. All other fields (port, sudo, HTTPS, custom build command, SSH key path) are optional and documented in [`deploy-static-resource2nginx/templates/server.config.example.json`](./deploy-static-resource2nginx/templates/server.config.example.json).

Then in Claude Code, type:

```
/deploy-static-resource2nginx
```

The skill will:

1. Verify `server.config.json` exists and is complete — if not, it stops and tells you what's missing.
2. Verify the remote nginx config (read-only). If it doesn't match, it pauses and offers to run `setup_nginx.py` for you — see "Server prerequisites" below.
3. Build the project with the correct `--base=/acme-demo/` flag.
4. SSH in, create `/var/www/apps/acme-demo/`, upload `dist/`.
5. Print the live URL: `http://your-server.example.com/acme-demo/`.

Open the URL — your demo is live.

---

## Server prerequisites (one time per server)

You don't have to configure nginx by hand. On the first deploy to a new server, the skill SSHes in and checks the nginx config; if it doesn't match the expected layout, it offers to run **`setup_nginx.py`**, which will:

- Install nginx via `apt` or `yum` if it isn't already.
- Write the canonical site config (listed below) to `/etc/nginx/sites-available/static-apps` (Debian/Ubuntu) or `/etc/nginx/conf.d/static-apps.conf` (RHEL/CentOS).
- Back up any existing default site, disable it, validate with `nginx -t`, and reload nginx.
- If validation fails, every change is rolled back automatically.

The block it installs:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    root /var/www/apps;
    index index.html index.htm index.nginx-debian.html;
    server_name _;
    location / { try_files $uri $uri/ /index.html; }
}
```

`setup_nginx.py` needs either root SSH access or passwordless sudo on the server (one time). For day-to-day deploys, the SSH user only needs write access to `/var/www/apps`, which `setup_nginx.py` arranges for you.

---

## Hosting multiple demos on one server

Just give each demo a different `deploy.project_name` in its own `server.config.json`. They land side-by-side under `/var/www/apps/` and never overwrite each other:

```
http://your-server.example.com/acme-demo/
http://your-server.example.com/contoso-pitch/
http://your-server.example.com/q3-launch/
```

Re-running deploy on an existing project replaces only that project's directory — the other demos are untouched.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `server.config.json incomplete` | Fill in the four required fields shown above. |
| `AuthenticationException` | Wrong host/username/password — double-check. |
| `Permission denied` on remote mkdir | Run the `chown` command from "Server prerequisites". |
| Blank page after deploy | You opened `http://host/acme-demo` without the trailing slash. Add the slash. |
| Refresh on a deep route (e.g. `/acme-demo/about`) shows wrong page | Known nginx-config limitation — see [`deploy-static-resource2nginx/REFERENCE.md`](./deploy-static-resource2nginx/REFERENCE.md#deep-link-spa-routing-under-a-sub-path) for three workarounds. |

For everything else, the two skills' own `REFERENCE.md` files have full detail.

---

## TL;DR

```text
/static-demo4domain-expert         # interview + scaffold demo
# add server.config.json with 4 fields
/deploy-static-resource2nginx             # build + upload, get URL
```
