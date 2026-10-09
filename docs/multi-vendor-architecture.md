# Multi-Vendor Agent Architecture

One folder of skills, read directly by every harness's installer — no per-tool copies, no post-merge bots.

```text
 skills/<name>/SKILL.md          ← the skill (Agent Skills format), self-contained
 skills/<name>/custom/           ← customer rules (empty here)
 skills/<name>/agents/           ← Codex display metadata
        │
        ├── Claude Code   .claude-plugin/plugin.json + marketplace.json   → reads skills/
        ├── Codex         plugin.json + .agents/plugins/marketplace.json  → reads skills/
        ├── Copilot / VS Code   plugin.json (Agent Plugins v1.0.0)        → reads skills/
        ├── Cursor        .cursor-plugin/  or  gh skill install           → reads skills/
        └── any tool      gh skill install / npx skills add               → copies skills/<name>/
```

## What people edit

| Path | Purpose |
|---|---|
| `skills/<name>/SKILL.md` | The skill. Any file it needs lives inside its own folder, referenced by a relative path. |
| `skills/<name>/agents/openai.yaml` | Codex display metadata for the skill |
| `skills/<name>/custom/{org,team,dev}/` | Customer customizations — always empty in Itential's repo |
| `AGENTS.md` | Repo guide read by every agent (`CLAUDE.md` imports it) |
| Manifests | `.claude-plugin/` (Claude Code), root `plugin.json` (Agent Plugins v1.0.0 — Codex, Copilot, VS Code; Codex display under `extensions["com.openai"]`), `.cursor-plugin/` (Cursor), `.agents/plugins/marketplace.json` (Codex marketplace). Every marketplace entry points at `"./"` / `"."` so an org's copy installs itself. |

Shared files: if several skills ever need the same file, keep it in a shared library folder and let `scripts/bundle_skill_assets.py` copy it into each skill's `assets/` (run `scripts/check-generated.sh` and commit the result). None needed today.

## CI

PR checks (required on `main`):

| Check | Fails when |
|---|---|
| Branch Naming | branch isn't `feature|fix|refactor|docs|chore/<kebab-case>` |
| Commit Messages | a commit isn't conventional (`feat: …`, `fix: …`), or is a merge commit |
| Skills Valid (`scripts/check-generated.sh`) | a skill references a file that isn't in its folder, or bundled `assets/` are out of date |
| Manifest Versions (`scripts/bump_version.py --check`) | the plugin manifests disagree on version |
| Custom folders empty (`scripts/check-custom-empty.sh`) | a PR adds real content under `skills/*/custom/` |

On `main`: **Release Drafter** keeps a draft of the next release's notes (only in `itential/admin-skills`). There are no bots that open PRs. Versions are bumped by hand when releasing — see `CONTRIBUTING.md` → Releasing.

## Install & invoke

| Harness | Install | Invoke |
|---|---|---|
| Claude Code | `/plugin install itential-admin-skills@itential-admin-skills` | `/itential-admin-skills:admin-platform` |
| Codex CLI | `codex plugin add itential-admin-skills@itential-admin-skills` | `$itential-admin-skills:admin-platform` |
| GitHub Copilot CLI | `copilot plugin install itential-admin-skills@itential-admin-skills` | `/admin-platform` |
| Copilot in VS Code | **Chat: Install Plugin From Source** | `/admin-platform` |
| Cursor | `gh skill install … --agent cursor --all` | `/admin-platform` |

Exact commands, including working from a clone: `docs/vendor-install.md`. Customization: `docs/customization.md`.
