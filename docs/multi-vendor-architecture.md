# Multi-Vendor Agent Architecture

Same architecture as [itential/builder-skills](https://github.com/itential/builder-skills): skills written once, installed complete in every harness.

```text
 skills/<name>/SKILL.md          (shared library: none yet — add helpers/,
 skills/<name>/custom/            spec-files/ or environments/ when a skill needs
 skills/<name>/agents/            reference files, and they get bundled)
        │
        └────────► skills/<name>/assets/        (generated, when a skill references library files)
                         │  CI copies each complete skill folder
                         ▼
     .claude/skills/     .agents/skills/        .github/skills/   (generated)
      Claude Code       Codex, Cursor,          GitHub Copilot
                        gh skill installs
```

## What people edit

| Path | Purpose |
|---|---|
| `skills/<name>/SKILL.md` | The skill itself (Agent Skills format) |
| `skills/<name>/agents/openai.yaml` | Codex display metadata for the skill |
| `skills/<name>/custom/{org,team,dev}/` | Customer customizations — empty in Itential's repo |
| `AGENTS.md` | Repo guide read by every agent (`CLAUDE.md` imports it) |
| `scripts/bundle-map.json` | Whole-directory bundles a skill needs (none today) |
| `customizations/{org,team,developer}/` | Repo-wide layer for a team's own clone |
| Manifests | `.claude-plugin/` (Claude Code), root `plugin.json` (Agent Plugins v1.0.0 — Codex, Copilot, VS Code; Codex display under `extensions["com.openai"]`), `.cursor-plugin/` (Cursor), `.agents/plugins/marketplace.json` (Codex marketplace) |

## What is generated — never edit by hand

| Path | Built from |
|---|---|
| `skills/<name>/assets/` | Shared-library files the skill references (none today) |
| `.claude/skills/`, `.agents/skills/`, `.github/skills/` | Real copies of each complete `skills/<name>/` folder |

Skills never point outside their own folder: only Claude Code substitutes `${CLAUDE_PLUGIN_ROOT}`, and `gh skill install` copies only skill folders. `scripts/bundle_skill_assets.py` enforces it — it fails if a skill-relative path in a `SKILL.md` doesn't exist inside that skill.

## Workflow and CI

Edit `skills/` and push. `.github/workflows/generate-mirrors.yml` bundles and regenerates the copies on pushes to `main` — pushing directly, or opening a `chore: regenerate vendor mirrors` PR when `main` is protected. Its own commit only touches generated paths, which the trigger excludes, so it can't loop. Preview locally: `scripts/check-generated.sh`.

| Check (PR) | Script | Fails when |
|---|---|---|
| Branch Naming | `pr-compliance.yml` | branch isn't `feature|fix|refactor|docs|chore/<kebab-case>` |
| Commit Messages | `pr-compliance.yml` | a commit isn't conventional (`feat: …`, `fix: …`), or is a merge commit |
| Generated Copies Untouched | `scripts/check-mirror-edits.sh` | a PR hand-edits generated files |
| Manifest Versions | `scripts/bump_version.py --check` | the plugin manifests disagree on version |
| Custom folders empty | `scripts/check-custom-empty.sh` | a PR adds real content under `skills/*/custom/` |

On `main`: **Version Bump** opens a patch-bump PR after every merge; **Release Drafter** keeps a draft release. Both run only in `itential/admin-skills`, not in customer copies.

## Install & invoke

| Harness | Install | Invoke |
|---|---|---|
| Claude Code | `/plugin install itential-admin-skills@itential-admin-skills` | `/itential-admin-skills:admin-platform` |
| Codex CLI | `codex plugin add itential-admin-skills@itential-admin-skills` | `$itential-admin-skills:admin-platform` |
| GitHub Copilot CLI | `copilot plugin install itential-admin-skills@itential-admin-skills` | `/admin-platform` |
| Copilot in VS Code | **Chat: Install Plugin From Source** | `/admin-platform` |
| Cursor | `gh skill install … --agent cursor --all` | `/admin-platform` |

Exact commands: `docs/vendor-install.md`. Customization: `docs/customization.md`.
<!-- E5 -->
