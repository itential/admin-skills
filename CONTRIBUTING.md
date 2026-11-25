# Contributing

Before your first pull request, sign the [Contributor License Agreement](CLA.md). Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md). Report security issues privately — see [SECURITY.md](SECURITY.md).

Pull requests into `main` must pass **Skills Valid**, **Manifest Versions**, **Custom folders empty**, **Security Rules**, **Workflow Security** and **CodeQL** (see `.github/workflows/`). **Branch Naming** also runs and reports, but doesn't block a merge.

## Branch names

`<type>/<description>` — type is one of `feature`, `fix`, `refactor`, `docs`, `chore`; description is lowercase letters, numbers and hyphens. Example: `feature/add-gateway-admin`.

The branch prefix sets the PR label, which groups the release notes: `feature/` → `feature`, `fix/` → `fix`, `refactor/` → `refactor`, `docs/` and `chore/` → left out of the release notes.

## Pull request titles

PRs are squash-merged, so the PR title becomes the commit on `main` and the line in the release notes. Write it as `<type>: <description>` — e.g. `fix: admin-config used the wrong role endpoint`.

## What to edit

- Skill content: `skills/<name>/SKILL.md`. Keep each skill self-contained — any file it references lives inside its own folder, referenced by a relative path (**Skills Valid** checks this, along with each skill's `name` and `description`).
- Never add files under `skills/*/custom/` here — that folder is for customers' own copies (**Custom folders empty** fails otherwise).
- Don't change versions in a normal PR. Releases are cut by a maintainer — see **Releasing** below.

Before pushing, run `python3 scripts/check-skills.py` — the same check CI runs.

## Security checks

The skills are instructions an AI follows with your credentials on your platform, so most security problems here are in Markdown, not code. **Security Rules** (`scripts/check-security-rules.py`) fails a PR whose skill text or scripts do what the rules don't allow: a token in a URL (`?token=`), instructions that have the agent read `.env`, a command the agent builds with a secret in it, a secret taken as a command-line argument or typed in front of a command, `curl … \| sh`, `npx -y`, or Configuration Manager remediation tasks. **Workflow Security** (zizmor) checks the GitHub Actions workflows, and **CodeQL** the scripts and workflows. OpenSSF Scorecard grades the repo weekly (the README badge), and Dependabot keeps the actions' commit-SHA pins current.

Run the rules before pushing: `python3 scripts/check-security-rules.py` (`--list` shows them). A sentence that *explains* a rule ("never use `?token=`") passes. If a match is genuinely safe, put `security-rules: allow <rule-id>` on that line and say why in the PR. When a security problem turns up that the rules missed, add a rule for it in the same PR as the fix. The rules are shared with builder-skills — keep the copies in step.

## Changelog

If your PR is user-facing (a new or changed skill, a fixed bug, a behavior change), add a bullet under `## Unreleased` in `CHANGELOG.md`, starting with `Added`, `Fixed`, `Changed` or `Removed`. Skip it for docs and chores.

## Releasing

Versions are bumped by hand, in their own PR, when a release is wanted:

```bash
git checkout -b chore/release-0-2-0
python3 scripts/bump_version.py --bump minor      # or patch / major — updates every manifest
# rename "## Unreleased" in CHANGELOG.md to "## 0.2.0" and add a new empty "## Unreleased"
git commit -am "chore: release v0.2.0"
```

After it merges, the draft release on GitHub is already named `v0.2.0` (Release Drafter reads the version from `plugin.json`) — review the notes and publish it. **Manifest Versions** fails any PR where the manifests disagree.
