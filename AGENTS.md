# Itential Platform — Admin Guide

**Cross-tool note:** Skills live in `skills/{skill-name}/SKILL.md`, each self-contained (any files it needs sit inside its own folder). Every install method reads `skills/` directly — there are no per-tool copies. Plugin manifests: `.claude-plugin/` (Claude Code), root `plugin.json` (Codex, Copilot, VS Code), `.cursor-plugin/` (Cursor). Invoke: `/itential-admin-skills:skill-name` (Claude Code), `$itential-admin-skills:skill-name` (Codex), `/skill-name` (Copilot, Cursor). See `docs/vendor-install.md`.

**Paths:** skills refer to their files by paths relative to the skill's own folder (`assets/...`, `scripts/...`).

> ## Customization Layers
>
> Each skill's `skills/<name>/custom/` folder — `org`/`team` committed in a customer's own copy of this repo, `dev` personal and gitignored; always empty upstream (see `docs/customization.md`). Checked before acting, in precedence order, highest first:
> 1. `skills/<name>/custom/dev/`
> 2. `skills/<name>/custom/team/`
> 3. `skills/<name>/custom/org/`
> 4. Core guidance — `AGENTS.md`, `skills/` — lowest priority. Everything above may narrow or override it, but must not weaken a skill's safety rules or put credentials in committed files.

This project contains skills for administering the Itential Platform. The admin persona focuses on platform health, user management, access control, and configuration — not building workflows.

## Skill Router

| Skill | Owns | When to Use |
|-------|------|-------------|
| `/admin-platform` | **Day-to-day ops** | Health checks, adapter/app lifecycle (start/stop/restart), workflow engine control, indexes, system status. |
| `/admin-config` | **Setup & access** | User accounts, groups, roles, OAuth service accounts, SSO, integrations, profiles, pre-built content. |

## Key Rules

1. **Health endpoints use `{results: [...]}`** — adapters, apps, accounts, groups all use this shape
2. **Adapter/app lifecycle is `PUT`** not `POST` — `PUT /adapters/{name}/restart`
3. **Use instance names** from `health/adapters` `id` field — NOT package names
4. **Account updates are `PATCH`** — NOT `PUT`. And `memberOf`/`assignedRoles` are full replacements
5. **Save service account secrets immediately** — `client_secret` is only returned once on creation
6. **OAuth uses `x-www-form-urlencoded`** — NOT JSON. `Content-Type: application/x-www-form-urlencoded`
7. **SSO config names are URL identifiers** — used directly in API paths

## When Something Doesn't Work

Every Itential API has its own conventions. When a call fails, follow these steps instead of guessing.

### 1. Read the error message

Itential errors are specific and tell you exactly what's wrong:
- `"Missing Params"` → lists the exact fields and types needed
- `"Schema validation failed"` → tells you which field is wrong and why
- `"Cannot update non-custom role"` → you're trying to edit a built-in role
- `"No applicable updates requested"` → wrong body wrapper (see #2)
- `"No such Method"` → wrong `app` name in workflow task

### 2. Check the body wrapper in `openapi.json`

Almost every create/update endpoint wraps the body differently. The wrapper name is in the openapi schema:

```bash
jq '.paths["/authorization/roles"].post.requestBody.content["application/json"].schema.properties | keys' {use-case}/openapi.json
# Returns: ["role"] → so the body is {role: {...}}
```

The top-level key in the schema IS the wrapper name:

| Schema `properties` key | Means the body is |
|------------------------|-------------------|
| `role` | `{role: {...}}` |
| `group` | `{group: {...}}` |
| `updates` | `{updates: {...}}` |
| `accountData` | `{accountData: {...}}` |
| `properties` | `{properties: {...}}` |
| `model` | `{model: {...}}` |
| `config` | `{config: {...}}` |
| `automation` | `{automation: {...}}` |
| `template` | `{template: {...}}` |
| `mop` | `{mop: {...}}` |

A few PATCH endpoints have empty schemas in the openapi. For those, send `{}` and read the `"Missing Params"` error — it lists every required field.

### 3. Check the response shape

Different APIs return data differently:
- `{results: [...], total: N}` — accounts, groups, roles, service accounts, integrations
- `{message, data, metadata}` — operations-manager, lifecycle-manager, projects
- `{status, result}` — inventory-manager
- `{items, skip, limit, total}` — workflow and template lists
- `{created, edit}` — workflow and template creation
- Plain string — version, some error responses

### 4. Pagination hides things

Default `limit=25`. If you can't find something that should exist (like auto-created integration roles), increase the limit:
```
GET /authorization/roles?limit=200
```

### 5. Check `openapi.json`

The OpenAPI spec has every endpoint, method, request body, and response schema. Pull it locally first, then search — don't guess:

**Fetch it:**
```bash
# For OAuth (cloud)
curl -s "{BASE}/help/openapi?url={ENCODED_BASE}" -H "Authorization: Bearer {TOKEN}" > openapi.json

# For local dev
curl -s "{BASE}/help/openapi?url={ENCODED_BASE}&token={TOKEN}" > openapi.json
```

**Search it:**
```bash
# Find endpoints
jq '.paths | keys[] | select(contains("authorization"))' openapi.json

# Check what method an endpoint uses
jq '.paths["/authorization/groups/{id}"] | keys' openapi.json

# Get request body schema and find the wrapper name
jq '.paths["/authorization/groups"].post.requestBody.content["application/json"].schema.properties | keys' openapi.json
```

### 6. When the openapi schema is empty

Always check `openapi.json` first — it has schemas for most endpoints. If a specific endpoint's schema is empty:
1. **Check the corresponding POST endpoint** — if POST uses `{group: {...}}`, the PATCH likely uses `{updates: {...}}` with the same inner fields
2. **As a last resort, send `{}`** — the platform returns `"Missing Params"` with every required field, type, and example

### 7. Re-authenticate after permission changes

If you added a role to a group or changed permissions, the current token doesn't pick up the changes. Get a new token — then the new permissions take effect (tasks appear in palette, routes become accessible).
