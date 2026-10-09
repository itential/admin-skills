# Contributing

Pull requests into `main` must pass **Skills Valid**, **Manifest Versions** and **Custom folders empty** (see `.github/workflows/`). **Branch Naming** also runs and reports, but doesn't block a merge.

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

## Releasing

Versions are bumped by hand, in their own PR, when a release is wanted:

```bash
git checkout -b chore/release-0-2-0
python3 scripts/bump_version.py --bump minor      # or patch / major — updates every manifest
git commit -am "chore: release v0.2.0"
```

After it merges, the draft release on GitHub is already named `v0.2.0` (Release Drafter reads the version from `plugin.json`) — review the notes and publish it. **Manifest Versions** fails any PR where the manifests disagree.
