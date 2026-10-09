# Customizing the Skills for Your Org

Every skill is owned and updated by Itential — don't edit a skill's `SKILL.md`, your changes would be overwritten by the next update. Instead, each skill has a `custom/` folder for your org's rules. The skill reads that folder every time it runs, and applies your rules on top of its own.

You write plain markdown files and commit them to your org's copy of this repo. Every install from that copy includes them — nothing to generate, nobody runs a script.

## At a glance

| Who | When | What |
|---|---|---|
| One admin | Once | [Set up your org's copy](#1-set-up-your-orgs-copy-once) |
| Anyone adding a rule | Whenever | [Add a rule](#2-add-a-rule) — write a file, push, check |
| Everyone on the team | Once | [Install from your copy](#3-everyone-installs-from-your-copy) |
| One admin | When Itential releases | [Take Itential's updates](#5-take-itentials-updates) |

---

## 1. Set up your org's copy (once)

Make a **private** copy — not GitHub's Fork button, because a fork of a public repo can't be made private:

```bash
gh repo create acme/admin-skills --private
git clone --bare https://github.com/itential/admin-skills.git
cd admin-skills.git && git push --mirror https://github.com/acme/admin-skills.git
cd .. && rm -rf admin-skills.git
```

(Or use GitHub's **Import repository** page with `https://github.com/itential/admin-skills`.)

Itential's own maintenance workflows (release notes, PR checks) switch themselves off in your copy, so there's nothing to configure.

---

## 2. Add a rule

### Decide where it goes

**Which skill?** Put the file in the folder of the skill that should follow it — `skills/admin-config/custom/…` for users, groups, roles, service accounts and SSO; `skills/admin-platform/custom/…` for health checks, adapters, applications and the workflow engine. If a rule applies to both, put a copy in each.

**Which layer?** Match it to who needs to agree:

| If the rule is… | Put it in | Example |
|---|---|---|
| Company policy — wrong for any team to do differently | `org/` | "Never delete a built-in role or group" |
| A convention your team agreed on | `team/` | "Our service accounts are named `svc-netops-<purpose>`" |
| Just yours — your sandbox, your test device, an experiment | `dev/` — see [Personal settings](#personal-settings-dev) | "My sandbox platform is `https://dev.example.itential.io`" |

### Write it

One or more `.md` files per folder, any names. Use `## ADD:` for a new rule. To replace one of the skill's own rules, use `## OVERRIDE:` and say what you're replacing and why, so it stays reviewable:

```markdown
## ADD: service account naming
Service accounts must be named svc-acme-<purpose>.

## OVERRIDE: adapter restarts
Original rule: restart an offline adapter directly.
Replacement: open a change ticket before restarting any production adapter —
our change policy requires it, even for a restart.
```

### Push it and check

```bash
git clone https://github.com/acme/admin-skills.git && cd admin-skills   # first time only
# create skills/admin-config/custom/org/naming.md
git add skills/admin-config/custom/org/naming.md
git commit -m "org: service account naming"
git push
```

The GitHub web editor works just as well. That's the rule delivered: the next install or update from your copy includes it.

---

## 3. Everyone installs from your copy

Team members follow [`vendor-install.md`](vendor-install.md) for their tool, using `acme/admin-skills` in place of `itential/admin-skills`. Already installed Itential's version? See [Switching to your own copy](vendor-install.md#switching-to-your-own-copy).

After a new rule is added, people pick it up with their tool's normal update (or `git pull` if they work from a clone).

---

## 4. Check the agent is using it

Run the skill and ask it directly — for example, start `/admin-config` and ask *"Which customization files are you applying?"* It should list your file. If it doesn't, see [Troubleshooting](#troubleshooting).

---

## 5. Take Itential's updates

When Itential publishes a release (**Watch → Custom → Releases** on `itential/admin-skills` to get notified), pull it into your copy the way your team normally syncs from upstream — for example:

```bash
git remote add upstream https://github.com/itential/admin-skills.git   # once
git pull upstream main
git push
```

That's it: your `custom/` files come through untouched. They can't conflict — Itential never puts anything in `custom/` folders (a check in Itential's repo blocks it). Then let the team know to update their installs.

---

## Personal settings (`dev/`)

`dev/` files are personal, so they're **gitignored** — they never get committed to your org's copy by accident. Where to keep them depends on how you work:

- **Working from a clone:** put them in `skills/<name>/custom/dev/` and load the skills from your clone (see the "Working from a clone" notes in [`vendor-install.md`](vendor-install.md)) — your tool picks them up from there.
- **Installed as a plugin:** there's no local copy to put them in. Use your tool's own personal instructions instead — e.g. `~/.claude/CLAUDE.md` (Claude Code) or `~/.codex/AGENTS.md` (Codex).

Keep `dev/` for facts about your environment and short-lived experiments. If you find yourself permanently overriding a team rule there, raise it with the team instead — that's what `team/` is for.

---

## Reference

### Folder layout

```
skills/<skill-name>/
├── SKILL.md          ← Itential's — never edit
└── custom/
    ├── org/          ← company-wide, committed
    ├── team/         ← your team, committed
    └── dev/          ← personal, gitignored
```

Always edit under `skills/<name>/custom/`. If a skill has an `assets/` folder, it's generated — edits there get overwritten.

### Which rule wins

More specific wins: `dev` over `team` over `org` over the skill's own defaults. Rules that don't conflict all apply together. Two files in the same layer shouldn't contradict each other — if they do, fix the files.

The repo also has a repo-wide `customizations/` folder, used by Itential's internal team; see `AGENTS.md` → Customization Layers for how it combines with the per-skill folders.

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent doesn't mention your file | File not under `skills/<name>/custom/`, or your install is older than the rule | Check the path, then update your install (or `git pull`) |
| A teammate sees your `dev/` rule | It was committed with `git add -f` | `git rm --cached` it and push |
