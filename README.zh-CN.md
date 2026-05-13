# 协作技能 (Cooperation Skills)

**语言 / Language:** [English](./README.md) | 中文

> 按 **Claude Code 技能**（`SKILL.md` 约定）格式编写。底层是纯 Markdown + Python，所以在其它编码 Agent 里也一样能跑 —— **Cursor、Windsurf、Cline、Aider、Cody** 等都行，只要把 `SKILL.md` 作为规则 / 上下文文件喂给 Agent（详见[安装](#一次性安装)）。

## 适用场景

> 一名销售人员 —— 或者任何**懂产品但不写代码的领域专家** —— 明天要给客户展示一个可以打开看的 Demo 页面。

这两个技能把整条流水线交到他们手里：

1. **生成。** 他们和 Claude 对话，被针对产品本身追问一轮，最终用自己说出来的话产出一个精致、可运行的 Vue 3 + Vite 网站 —— 不用写需求文档，不用占用开发资源。
2. **托管。** 一条命令之后，网站就上线在 `http://<他们的服务器>/<demo名称>/`。把链接贴进邮件，客户在任何设备上都能打开。
3. **交接。** 生成出来的项目自带真实的源代码，还附带 `README.md` 和 `CONTEXT.md`，记录了销售的卖点、术语和意图。下周开发同事打开这个仓库，不需要再重新访谈，就能理解 Demo，并把它演化成真正的功能。

同一台服务器可以托管任意多个 Demo —— 每个 Demo 在自己独立的 URL 路径下 —— 所以销售人员可以慢慢攒出自己的一整套 Demo 库，全程不用麻烦运维。

## 两个技能

| 技能 | 作用 |
| --- | --- |
| [`static-demo4domain-expert`](./static-demo4domain-expert) | 通过追问式访谈采访销售人员，根据回答生成一个精致、可直接运行的 Vue 3 + Vite Demo 项目，并附带 `README.md` 与 `CONTEXT.md`，方便开发人员后续接手。 |
| [`deploy-static-resource2nginx`](./deploy-static-resource2nginx) | 构建上一步生成的 Vue 项目，并把它上传到一台已配置好 nginx 的远程服务器。每个 Demo 部署在 `http://<服务器>/<项目名>/`。 |

使用顺序：**生成 → 部署**。第一次完整跑完大约 15 分钟，之后每次重新部署不到 1 分钟。

---

## 一次性安装

**Claude Code** —— 把这两个文件夹复制到你的技能目录：

```bash
cp -R static-demo4domain-expert     ~/.claude/skills/
cp -R deploy-static-resource2nginx  ~/.claude/skills/
```

**其它 Agent**（Cursor、Windsurf、Cline、Aider、Cody …）—— 把仓库 clone 到任意位置，然后把每个技能下的 `SKILL.md` 当作规则 / 上下文 / 系统提示词喂给 Agent。之后 Agent 会从同一个目录里调用 `scripts/*.py`。示例：

- **Cursor** —— 把 `SKILL.md` 内容放进 `.cursor/rules/*.mdc`（或者通过 "Add Context" 直接附加该文件）
- **Windsurf** —— 把目录加入工作区，在 `.windsurfrules` 中引用 `SKILL.md`
- **Cline / Aider** —— 把 `SKILL.md` 作为系统提示词，或在会话开始时 `/read` 它

部署步骤还需要 Python 3.8+（macOS 和 Windows 都可用）。所需的两个库（`paramiko`、`scp`）会在你第一次运行技能时自动安装到技能目录下的本地 venv 中 —— 你不用手动 `pip install`。

整个工具链就这些。

---

## 第 1 步 —— 生成 Demo

在 Claude Code 中输入：

```
/static-demo4domain-expert
```

这个技能会：

1. 询问你使用哪种语言（English / 中文 / 等）。
2. 用追问式的提问方式，分 5 个小批次询问你的产品、目标受众和卖点。
3. 把整理后的编号摘要给你确认。
4. 在你指定的目录中生成 Vue 3 + Vite + Tailwind 项目，自动执行 `npm install`，并打印本地启动命令。

最终你会得到一个像 `~/demos/acme-demo/` 的项目目录，本地用 `npm run dev` 就能运行。

---

## 第 2 步 —— 部署 Demo

在同一个项目目录下，创建一个文件：**`server.config.json`**。最少只需要四个字段：

```json
{
  "server": {
    "host": "your-server.example.com",
    "username": "ubuntu",
    "password": "你的SSH密码"
  },
  "deploy": {
    "project_name": "acme-demo"
  }
}
```

仅此而已。其它字段（端口、sudo、HTTPS、自定义构建命令、SSH 密钥路径）都是可选的，详细说明见 [`deploy-static-resource2nginx/templates/server.config.example.json`](./deploy-static-resource2nginx/templates/server.config.example.json) 和 [`deploy-static-resource2nginx/REFERENCE.md`](./deploy-static-resource2nginx/REFERENCE.md)。

然后在 Claude Code 中输入：

```
/deploy-static-resource2nginx
```

这个技能会：

1. 检查 `server.config.json` 是否存在且完整 —— 缺字段就停下来告诉你缺什么。
2. 检查远程 nginx 配置（只读）。如果配置不匹配，会暂停并询问你是否运行 `setup_nginx.py` —— 详见下方"服务器准备工作"。
3. 用正确的 `--base=/acme-demo/` 参数构建项目。
4. 通过 SSH 登录服务器，创建 `/var/www/apps/acme-demo/`，上传 `dist/`。
5. 打印线上访问地址：`http://your-server.example.com/acme-demo/`。

打开链接 —— Demo 就上线了。

---

## 服务器准备工作（每台服务器只做一次）

你不需要手动配置 nginx。第一次往新服务器部署时，技能会通过 SSH 登录检查 nginx 配置；如果不匹配预期布局，它会询问你是否运行 **`setup_nginx.py`**，这个脚本会：

- 如果 nginx 还没装，用 `apt` 或 `yum` 自动安装。
- 把下面这段标准站点配置写入 `/etc/nginx/sites-available/static-apps`（Debian/Ubuntu）或 `/etc/nginx/conf.d/static-apps.conf`（RHEL/CentOS）。
- 备份并停用原有的默认站点，运行 `nginx -t` 校验配置，再重载 nginx。
- 如果校验失败，所有改动都会自动回滚。

它写入的配置块：

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

`setup_nginx.py` 只需要一次性的服务器 root 权限或免密 sudo。日常部署时，SSH 用户只需要对 `/var/www/apps` 有写权限 —— 这个权限 `setup_nginx.py` 会替你配置好。

---

## 在同一台服务器上托管多个 Demo

只要给每个 Demo 在各自的 `server.config.json` 里写不同的 `deploy.project_name` 即可。它们会并排放在 `/var/www/apps/` 下，互不覆盖：

```
http://your-server.example.com/acme-demo/
http://your-server.example.com/contoso-pitch/
http://your-server.example.com/q3-launch/
```

重新部署某个 Demo 只会替换它自己的目录，其它 Demo 完全不受影响。

---

## 常见问题

| 现象 | 解决办法 |
| --- | --- |
| `server.config.json incomplete` | 把上面那四个必填字段填完整。 |
| `AuthenticationException` | 主机地址、用户名或密码错误，仔细核对。 |
| 远程 `mkdir` 提示 `Permission denied` | 执行上面"服务器准备工作"里的 `chown` 命令。 |
| 部署后页面空白 | 你访问的是 `http://host/acme-demo`，没有最后那个斜杠。加上 `/` 再访问。 |
| 在子路径上刷新（如 `/acme-demo/about`）显示错误内容 | nginx 配置的已知限制 —— 详细解决方案见 [`deploy-static-resource2nginx/REFERENCE.md`](./deploy-static-resource2nginx/REFERENCE.md#deep-link-spa-routing-under-a-sub-path)，提供三种修复方式。 |

其它问题查看两个技能各自的 `REFERENCE.md`，里面有完整说明。

---

## 极简流程

```text
/static-demo4domain-expert         # 访谈 + 生成 Demo
# 添加 server.config.json，填四个字段
/deploy-static-resource2nginx             # 构建 + 上传，拿到访问链接
```
