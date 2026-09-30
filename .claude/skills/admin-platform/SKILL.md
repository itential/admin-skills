---
name: admin-platform
description: Monitor platform health, manage adapters and applications (start/stop/restart/configure), control workflow engine workers, manage database indexes, and check system status. Use for day-to-day platform operations and troubleshooting.
argument-hint: "[action or adapter-name]"
---

# Platform Administration - Health, Adapters, Applications & Engine

Day-to-day platform operations: is the platform healthy? Are adapters connected? Are workers running? Need to restart something? This skill covers monitoring, adapter/app lifecycle, engine control, and index management.

## Org, team & personal rules

Before using this skill, check two layers, most specific wins:

1. Per-skill: `custom/org/`, `custom/team/`, `custom/dev/` in this skill's own
   folder (applies only to this skill).
2. Repo-wide, only when working in a clone of this repo: `customizations/org/`,
   `customizations/team/`, `customizations/developer/` at the repo root
   (applies to every skill).

Read every `.md` file found — any folder may be empty or absent. Apply them on
top of everything below; where a file overrides a specific rule here, follow the
override. More specific wins: per-skill dev > team > org > repo-wide developer >
team > org > this document. No customization may weaken this skill's safety
rules or put credentials in committed files.

---

## Concepts

- **Adapters** — connectors to external systems (ServiceNow, AWS, Meraki, etc.). Each has a state (RUNNING/STOPPED), connection config, and properties.
- **Applications** — internal platform apps (WorkFlowEngine, ConfigurationManager, MOP, etc.). Each can be started/stopped/restarted independently.
- **Workers** — job and task workers that execute workflow steps. Can be activated/deactivated.
- **Profiles** — saved configurations of adapter/app settings for different environments (dev/staging/prod).
- **Indexes** — MongoDB indexes used by platform apps. Can become stale and need rebuilding.

## Gotchas

- `GET /health/adapters` returns `{results: [...]}` — adapters are in the `results` array
- `GET /health/applications` also returns `{results: [...]}` — same shape
- Adapter lifecycle is `PUT` not `POST`: `PUT /adapters/{name}/restart`
- Adapter `{name}` is the **instance name** from `health/adapters` `id` field, NOT the package name
- Adapter properties endpoint: `PUT /adapters/{name}/properties` takes `{properties: {...}}` wrapper
- Application restart/stop/start uses the **app name** from `health/applications`, e.g., `WorkFlowEngine`
- `GET /health/system` returns OS-level stats (CPU, memory, uptime), NOT platform health
- `GET /health/server` returns platform version, node version, build info
- Accounts use `{results: [...], total: N}` shape — NOT `{data: [...]}`
- Workflow engine activate/deactivate is `POST` (no body required)
- **Rate limit can only be updated when workers are deactivated** — `POST /workflow_engine/deactivate` first, then update, then `POST /workflow_engine/activate`
- **Log level change requires `transport` field** — not just `loglevel`. Valid transports: `file`, `console`, `syslog`

## Health Monitoring

### Platform overview

```
GET /health/server
```
Returns: version, release, build, arch, platform, node version.
```json
{
  "version": "6.3.1",
  "release": "6.3.1",
  "build": "2025.93.19",
  "arch": "x64",
  "platform": "linux",
  "versions": {"node": "20.19.5", ...}
}
```

Quick version check: `GET /version` → returns just the version string.

### System health (OS-level)

```
GET /health/system
```
Returns: arch, kernel, uptime, free/total memory, load average, CPU details.

### Who am I?

```
GET /whoami
```
Returns current user: id, username, provenance, groups, roles.

### Adapter health

```
GET /health/adapters
```
```json
{
  "results": [
    {
      "id": "ServiceNow",
      "package_id": "@itentialopensource/adapter-servicenow",
      "state": "RUNNING",
      "connection": {"state": "online"},
      "properties": {...}
    }
  ]
}
```

Key fields:
- `id` — instance name (use this for lifecycle commands)
- `package_id` — adapter package
- `state` — `RUNNING`, `STOPPED`, `ERROR`
- `connection.state` — `online`, `offline`

Single adapter: `GET /health/adapters/{name}`

### Application health

```
GET /health/applications
```
```json
{
  "results": [
    {
      "id": "WorkFlowEngine",
      "state": "RUNNING",
      "description": "...",
      "version": "..."
    }
  ]
}
```

Single application: `GET /health/applications/{name}`

## Adapter Lifecycle

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/adapters/{name}/restart` | Restart an adapter |
| PUT | `/adapters/{name}/start` | Start a stopped adapter |
| PUT | `/adapters/{name}/stop` | Stop a running adapter |
| GET | `/adapters/{name}` | Get full adapter configuration |
| PUT | `/adapters/{name}` | Update adapter configuration |
| PUT | `/adapters/{name}/properties` | Update adapter properties only |
| PUT | `/adapters/{name}/loglevel` | Change adapter log level |
| GET | `/adapters/{name}/changelogs` | Get adapter change history |
| GET | `/adapters/{name}/export` | Export adapter configuration |
| DELETE | `/adapters/{name}` | Delete an adapter |
| POST | `/adapters/import` | Import adapter configuration |

**Restart an adapter:**
```
PUT /adapters/ServiceNow/restart
```
No body required. Returns the updated adapter state.

**Update adapter properties:**
```
PUT /adapters/ServiceNow/properties
```
```json
{
  "properties": {
    "host": "https://instance.service-now.com",
    "authentication": {
      "username": "admin",
      "password": "new-password"
    }
  }
}
```
Note: the `properties` wrapper is required.

**Change log level:**
```
PUT /adapters/ServiceNow/loglevel
```
```json
{
  "loglevel": "debug"
}
```
Values: `error`, `warn`, `info`, `debug`, `trace`, `spam`

**Get adapter configuration schema:**
```
GET /schema/adapters/{name}
```
Returns the JSON Schema defining valid adapter properties. Use this to understand what fields are configurable.

## Application Lifecycle

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/applications/{name}/restart` | Restart an application |
| PUT | `/applications/{name}/start` | Start a stopped application |
| PUT | `/applications/{name}/stop` | Stop a running application |
| GET | `/applications/{name}` | Get full application configuration |
| PUT | `/applications/{name}` | Update application configuration |
| PUT | `/applications/{name}/properties` | Update application properties only |
| PUT | `/applications/{name}/loglevel` | Change log level |
| GET | `/applications/{name}/changelogs` | Get change history |

**Restart an application:**
```
PUT /applications/WorkFlowEngine/restart
```

**Get application schema:**
```
GET /schema/applications/{name}
```

## Workflow Engine Control

### Worker status

```
GET /workflow_engine/workers/status
```
```json
{
  "jobWorker": {"running": true, "clusterValue": "not defined", "localValue": "enabled"},
  "taskWorker": {"running": true, "clusterValue": "not defined", "localValue": "enabled"}
}
```

### Activate/deactivate engine

```
POST /workflow_engine/activate
POST /workflow_engine/deactivate
```
No body required. Controls whether the engine processes jobs.

### Rate limiting

```
GET /workflow_engine/workers/rate_limit
```
```json
{"rateLimit": 0, "rateLimitPeriod": 1}
```

```
PUT /workflow_engine/workers/rate_limit
```
```json
{"rateLimit": 10, "rateLimitPeriod": 1}
```
- `rateLimit` — max jobs per period (0 = unlimited)
- `rateLimitPeriod` — period in seconds

## Database Indexes

### List all indexes

```
GET /indexes
```
Returns object keyed by collection name, each containing an `indexes` array.

### Check index status

```
GET /indexes/status
```
Shows which collections have pending index rebuilds.

```
GET /indexes/{collection}/status
```
Status for a specific collection.

### Rebuild indexes

```
POST /indexes/{collection}
```
Triggers index rebuild for a collection. Use when queries are slow or after migrations.

## Customization

### Platform banner

```
GET /customization/banner
PUT /customization/banner
```
Set a platform-wide banner message (e.g., "Maintenance window tonight 10pm-2am").

## Admin Scenarios

### 1. Platform health check
```
1. GET /version                              → confirm platform version
2. GET /health/server                        → check server health
3. GET /health/adapters                      → check all adapter states
4. GET /health/applications                  → check all app states
5. GET /workflow_engine/workers/status        → check workers running
6. Flag any STOPPED/ERROR adapters or apps
```

### 2. Restart a failing adapter
```
1. GET /health/adapters/{name}               → confirm it's in ERROR/STOPPED
2. PUT /adapters/{name}/restart              → restart it
3. GET /health/adapters/{name}               → verify RUNNING
4. If still failing: GET /adapters/{name}    → check configuration
5. GET /schema/adapters/{name}               → understand configurable properties
6. PUT /adapters/{name}/properties           → fix config if needed
```

### 3. Troubleshoot slow job processing
```
1. GET /workflow_engine/workers/status        → are workers running?
2. GET /workflow_engine/workers/rate_limit    → is rate limiting active?
3. GET /indexes/status                       → are indexes stale?
4. POST /indexes/{collection}                → rebuild if needed
5. PUT /workflow_engine/workers/rate_limit    → adjust if rate limited
```
