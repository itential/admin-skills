# Changelog

Versions correspond to the plugin manifest version (`plugin.json`) and the GitHub
release tag — what every tool's update installs.

## Unreleased

## 0.2.0

- Fixed request bodies in `admin-config` that the platform rejects: account, role and service-account updates use `{updates: {...}}`; role, group and SSO creation use `{role}`, `{group}` and `{config}` wrappers with their required fields; prebuilt import uses `{prebuilt, options}`; service accounts are deactivated through their account
- Fixed `admin-platform`'s log-level body (`{properties: {transport, level}}`), adapter health fields (`connection.state` is upper-case; properties come from `GET /adapters/{name}`), and noted that adapter changelogs and export return HTTP 500 on 6.5 with a working alternative
- Added banner, index-status and profile-list details to the skills
- Changed the license to GPL-3.0-or-later, matching Itential's other agent skills

## 0.1.4

- Added the `admin-platform` and `admin-config` skills for administering the Itential Platform
- Added native installs for Claude Code, Codex CLI, GitHub Copilot (CLI and VS Code) and Cursor, each reading the same `skills/` folder
- Added per-skill `custom/org`, `custom/team` and `custom/dev` folders for an organization's own rules, kept separate from Itential's content so updates never overwrite them
