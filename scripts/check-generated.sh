#!/usr/bin/env bash
set -euo pipefail

# Validates skills and their bundled files. Runs the bundler, which fails if any
# skill-relative path a SKILL.md mentions doesn't exist inside that skill, then fails
# if skills/*/assets is out of date (commit the bundler's output in your PR).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "${ROOT_DIR}/scripts/bundle_skill_assets.py"

if [[ -n "$(git -C "${ROOT_DIR}" status --porcelain -- skills)" ]]; then
  echo "skills/*/assets is out of date -- run scripts/check-generated.sh locally and commit the result:" >&2
  git -C "${ROOT_DIR}" status --short -- skills >&2
  exit 1
fi

echo "Skills valid: every bundled-file reference resolves and skills/*/assets is up to date."
