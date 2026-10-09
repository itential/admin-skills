# Changelog

Versions correspond to the plugin manifest version (`plugin.json`) and the GitHub
release tag — what every tool's update installs.

## Unreleased

- Changed the license to GPL-3.0-or-later, matching Itential's other agent skills

## 0.1.4

- Added the `admin-platform` and `admin-config` skills for administering the Itential Platform
- Added native installs for Claude Code, Codex CLI, GitHub Copilot (CLI and VS Code) and Cursor, each reading the same `skills/` folder
- Added per-skill `custom/org`, `custom/team` and `custom/dev` folders for an organization's own rules, kept separate from Itential's content so updates never overwrite them
