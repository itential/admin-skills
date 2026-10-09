# Itential — Admin Skills

AI agent skills for **administering the Itential Platform**: platform health, adapter and application lifecycle, workflow-engine control, users, groups, roles, service accounts, SSO, integrations and pre-built content. Works in Claude Code, Codex CLI, GitHub Copilot (CLI and VS Code) and Cursor.

| Skill | Use it for |
|---|---|
| `admin-platform` | Day-to-day operations: health checks, start/stop/restart adapters and apps, workflow-engine workers, database indexes, system status |
| `admin-config` | Setup and access: user accounts, groups, roles, OAuth service accounts, SSO, codeless integrations, profiles, pre-built content |

---

## Getting Started

### 1. Install for your tool

| Tool | Install |
|------|---------|
| **Claude Code** | `/plugin marketplace add itential/admin-skills` then `/plugin install itential-admin-skills@itential-admin-skills` (same install covers the VS Code extension) |
| **Codex CLI** | `codex plugin marketplace add itential/admin-skills` then `codex plugin add itential-admin-skills@itential-admin-skills` (same install covers the VS Code extension) |
| **GitHub Copilot in VS Code** | Command Palette → **Chat: Install Plugin From Source** → `itential/admin-skills` |
| **GitHub Copilot CLI** | `copilot plugin marketplace add itential/admin-skills` then `copilot plugin install itential-admin-skills@itential-admin-skills` |
| **Cursor** | `gh skill install itential/admin-skills --agent cursor --all` in your project (or clone the repo and open it) |

How to check it worked, run skills, and update — per tool: [`docs/vendor-install.md`](docs/vendor-install.md).

> **Your org wants its own rules** (naming, change policy, approved roles)? Set up your org's copy first and install from that instead — [`docs/customization.md`](docs/customization.md).

### 2. Connect to your platform

Make a folder to work in, with a `.env` holding your platform credentials:

```bash
mkdir my-platform && cd my-platform
cat > .env <<'EOF'
PLATFORM_URL=https://your-instance.itential.io
AUTH_METHOD=oauth
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
EOF
```

On a local/dev platform with a username and password, use `AUTH_METHOD=password` with `USERNAME=` and `PASSWORD=` instead.

### 3. Verify it's working

Open your tool in that folder and ask:

> "Check the health of my Itential platform."

The agent should start the **admin-platform** skill and report adapters, applications and their states — rather than guessing endpoints. You can also start it directly: `/itential-admin-skills:admin-platform` (Claude Code), `$itential-admin-skills:admin-platform` (Codex), `/admin-platform` (Copilot, Cursor).

### Staying up to date

**Watch → Custom → Releases** on this repo to hear about new versions, then update with your tool's command in [`docs/vendor-install.md`](docs/vendor-install.md). Claude Code updates on its own.

---

## Customization

Don't edit a skill's `SKILL.md` (updates would overwrite it). Each skill has a `custom/` folder for your org's rules:

```
skills/<skill-name>/
├── SKILL.md          ← Itential's — never edit
└── custom/
    ├── org/          ← company-wide rules
    ├── team/         ← your team's rules
    └── dev/          ← personal settings (not committed)
```

An admin makes a private copy of this repo, the team commits markdown rules under the right skill's `custom/` folder, and everyone installs from the org's copy — the rules come with every install. Step by step: [`docs/customization.md`](docs/customization.md).

---

## Docs

- [`docs/vendor-install.md`](docs/vendor-install.md) — install, run, update per tool
- [`docs/customization.md`](docs/customization.md) — add your org's rules and keep them across updates
- [`docs/multi-vendor-architecture.md`](docs/multi-vendor-architecture.md) — how every harness installs from `skills/`, and the CI checks
- [`AGENTS.md`](AGENTS.md) — the guide every agent reads first
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — branch and commit conventions

## License

[AGPL-3.0](LICENSE)
