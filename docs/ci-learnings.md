# CI learnings (itential/admin-skills sandbox, 2026-09-30)

> **Update:** the per-tool copies (`.claude/skills`, `.agents/skills`, `.github/skills`) and the mirror pipeline were later removed — every installer reads `skills/` directly. Findings 4, 5 and 7 below describe that removed pipeline.

This repo was used to exercise the builder-skills CI design on a real org repo with branch protection — something a private personal repo can't do. Each finding links to the PR or run where it showed up.

## Settings this repo runs with

- **Branch protection on `main`:** require a pull request; required status checks **Branch Naming**, **Commit Messages**, **Custom folders empty**, **Generated Copies Untouched**, **Manifest Versions** (not "strict"); 0 required approvals (sandbox — builder-skills uses 1); "enforce for admins" off.
- **Actions → Workflow permissions:** read and write, and "Allow GitHub Actions to create and approve pull requests" on (both needed by the bot PRs).
- **Labels** created up front for the labeler and release drafter: `feature`, `fix`, `refactor`, `documentation`, `chore`, `skip-changelog`, `breaking-change`.

## What we learned

| # | Finding | Evidence | Impact / fix |
|---|---|---|---|
| 1 | The PR labeler doesn't run on the PR that adds it | #1 got no label | `pull_request_target` runs the workflow from `main`. Expected once; from the next PR on it works (#3, #11). |
| 2 | PRs opened by the bot token get **no checks at all** | #2, #4, #6, #12, #13: "no checks reported" | GitHub doesn't let `GITHUB_TOKEN` events trigger workflows. With required checks, every bot PR is **stuck**. |
| 3 | A human close + reopen unblocks a bot PR | #2 went from no checks → all 6 pass → mergeable | Workaround only. The real fix is a token that triggers workflows: a fine-grained PAT or (better, for an org) a GitHub App, stored as a secret — builder-skills' workflows already read `VERSION_BUMP_TOKEN`. |
| 4 | Every skill change produces **two** bot PRs | #11 → #12 (bump) + #13 (regenerated copies) | With finding 2, that's two manual nudges per change. A bot token that triggers checks (plus auto-merge on bot PRs) makes it hands-off. |
| 5 | The mirror pipeline crashed when **no skill has bundled assets** | [run on #3's merge](https://github.com/itential/admin-skills/actions/runs/36769371962): `fatal: pathspec ':(glob)skills/*/assets/**' did not match any files` | Fixed in #5. Affects builder-skills too (any copy where no skill has assets). |
| 6 | Version bump **failed** when an earlier bump PR was still open | Run after #5: branch `chore/bump-version-to-0-1-2` already existed → non-fast-forward | Fixed in #14: an existing bump branch already carries the next version, so the bump is a no-op. |
| 7 | Protection rejects the bot's direct push, and the fallback works | Mirror run after #5: `GH006: Protected branch update failed` → opened #6 | As designed. |
| 8 | Required checks block merging, but admins can override | E2–E5 (#7–#10): each failed exactly its target check and was BLOCKED; `gh pr merge` offered `--admin` | Turn on "enforce for admins" if the checks must bind everyone. |
| 9 | Release notes and plugin versions follow different numbers | Draft release **v0.1.0** while manifests became 0.1.1, 0.1.2… | Release Drafter versions by labels; Version Bump always adds a patch. Same in builder-skills. Pick one source of truth. |
| 10 | Fork PRs behave like branch PRs | #11 from `keepithuman/admin-skills`: all 6 checks ran, labeler labeled it | Works for org members. (First-time outside contributors may need a maintainer to approve workflow runs.) |

## Failure experiments (each should fail exactly one check)

| PR | Change | Failed check |
|---|---|---|
| #7 | hand-edit `.claude/skills/…` | Generated Copies Untouched |
| #8 | real file under `skills/*/custom/org/` | Custom folders empty |
| #9 | `plugin.json` version drift | Manifest Versions |
| #10 | branch `E5_Bad_Branch`, non-conventional commit | Branch Naming, Commit Messages |

## Installs from this repo (verified live)

| Harness | Result |
|---|---|
| Claude Code | `claude plugin validate .` passes; `--plugin-dir` loads 2 skills |
| Codex CLI | marketplace add + plugin add → v0.1.3; from an unrelated folder the skill is `itential-admin-skills:admin-platform` and opens from the install |
| Copilot CLI | marketplace add + install → 2 skills; skill is `admin-platform` |
| Cursor (`gh skill install --agent cursor --all`) | both skills installed into `.agents/skills/`, complete |

## Still open

- **Bot token (finding 2–4):** needs a PAT or GitHub App created by an org admin and stored as a repo/org secret; not something CI can create itself.
- **Version source of truth (finding 9).**
