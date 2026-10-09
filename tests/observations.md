# Integration E2E Test Observations

## Date: 2026-03-04

## Findings

### Integration Model vs Adapter (Code-based vs Codeless)

| | Code-based Adapter | Codeless Integration |
|---|---|---|
| Created from | npm package | OpenAPI spec upload |
| Shows in | `/health/adapters` | `/integrations` only |
| `virtual` field | false/absent | `true` |
| Tasks appear in | tasks/list with `app = instance_name` | Same |
| Direct REST routes | Auto-registered | Need auth role enablement |
| Config | adapter properties | integration properties |

### The Flow (confirmed on local)

```
1. POST /integration-models {model: <OpenAPI spec>}
   → Creates model: @itential/adapter_JSONPlaceholder:1.0.0
   → Model has versionId: "JSONPlaceholder:1.0.0"

2. POST /integrations {properties: {name, type:"Adapter", properties:{id, type: versionId}, virtual:true}}
   → Creates instance: jsonplaceholder-api
   → Platform auto-generates tasks from OpenAPI paths
   → Tasks appear in tasks/list with app=instance_name, locationType=versionId

3. Configure connection:
   PUT /integrations/{name}/properties {properties: {server:{host,protocol,base_path}, auth, tls}}

4. Enable routes in auth:
   - Create custom role with allowedMethods for the integration methods
   - Cannot update built-in "admin" roles ("Cannot update non-custom role")
   - Assign role to user account
   - Re-auth to pick up new permissions

5. Use in workflows:
   - Works through workflow engine even without direct route auth
   - app field: apps/list name (e.g., "JSONPlaceholder:1.0.0")
   - adapter_id: instance name (e.g., "jsonplaceholder-api")
   - locationType: versionId (e.g., "JSONPlaceholder:1.0.0")
```

### What Was Confirmed Working

1. ✅ Created OpenAPI spec for JSONPlaceholder (4 endpoints, 5 operations)
2. ✅ Uploaded as integration model → `@itential/adapter_JSONPlaceholder:1.0.0`
3. ✅ Created integration instance → `jsonplaceholder-api`
4. ✅ Tasks appeared in palette: getPosts, createPost, getPostById, getUsers, getUserById
5. ✅ apps/list shows: `JSONPlaceholder:1.0.0` (Adapter type)
6. ✅ Workflow created with `app: "JSONPlaceholder:1.0.0"`, `adapter_id: "jsonplaceholder-api"` → NOT a draft (valid)
7. ✅ Workflow RAN and got HTTP 200 from jsonplaceholder.typicode.com
8. ✅ Response shape: `{ok, url, status, statusText, headers, data}` (raw HTTP response)

### What's Different from Code-based Adapters

- Integration instances do NOT show in `/health/adapters`
- The "paths[0] argument must be of type string" error on `/adapters/{name}/start` — integrations don't use the adapter start/stop lifecycle
- Direct REST routes (`POST /{instance}/method`) return 404 — routes need auth role configuration
- Cannot update built-in roles — must create custom roles with `provenance: "Custom"`

### Response Shape for Integration Calls

When called through a workflow, the integration returns raw HTTP response:
```json
{
  "ok": true,
  "url": "https://jsonplaceholder.typicode.com/posts",
  "status": 200,
  "statusText": "OK",
  "headers": {...},
  "data": [...]  ← the actual API data is here
}
```

### Auth Settings (Partially Tested)

- Need custom role with `allowedMethods` listing each method + provenance (instance name)
- Built-in admin roles return "Cannot update non-custom role"
- Role format: `{"name": "getPosts", "provenance": "jsonplaceholder-api"}`
- After creating role, assign to account, re-auth to pick up permissions

### Confirmed Full Flow (Dog API — tested on local)

```
1. POST /integration-models {model: <OpenAPI 3.0 spec>}
   → Model auto-created: @itential/adapter_Dog API:1.0.0
   → Roles auto-created with provenance = "Dog API:1.0.0"
   → Each HTTP method group gets a role (admin, get, post, etc.)

2. POST /integrations {properties: {name:"dog-api", type:"Adapter", properties:{id:"dog-api", type:"Dog API:1.0.0"}, virtual:true}}
   → Instance created with connection config from model

3. GET /authorization/roles?limit=200
   → Find auto-created role: {_id:"69a8716b...", name:"admin", provenance:"Dog API:1.0.0", allowedMethods:[...]}

4. PATCH /authorization/groups/{groupId} {updates: {assignedRoles: [...existing, {roleId: "69a8716b..."}]}}
   → Group PATCH requires {updates: {...}} wrapper
   → assignedRoles is full replacement — include ALL existing + new

5. Re-authenticate (GET new token)
   → Tasks appear in palette: listAllBreeds, getBreedImages, getRandomBreedImage, getRandomImage

6. Create workflow with:
   - app: "Dog API:1.0.0" (from apps/list, the versionId)
   - adapter_id: "dog-api" (instance name)
   - locationType: "Dog API:1.0.0"

7. POST /operations-manager/jobs/start
   → Workflow runs, gets 108 dog breeds + random husky image URL
```

### API Wrappers Discovered
- Create role: `{role: {...}}` wrapper
- Create group: `{group: {...}}` wrapper
- Update group: `{updates: {...}}` wrapper
- Create integration: `{properties: {...}}` wrapper
- Update integration properties: `{properties: {...}}` wrapper

### Still TODO

- [ ] Complete direct REST route testing (need auth role for routes)
- [ ] Test with auth-required API (API key, Bearer token)
- [ ] Document the full flow in admin-config skill
- [ ] Test on cloud platform (should be smoother)
- [ ] Create helper template for integration model creation

### Key Gotchas to Document

1. Integration `POST /integrations` body must wrap in `{properties: {...}}` — the UI does `axios.post('/integrations', {properties: data})`
2. The `type` field must be `"Adapter"` and `virtual` must be `true`
3. `properties.type` is the `versionId` from the model (e.g., "JSONPlaceholder:1.0.0")
4. `properties.id` must match the instance `name`
5. Integration instances don't show in `/health/adapters` — check `/integrations` instead
6. Workflow tasks use `app` from `apps/list` (the model versionId), NOT the instance name
7. `adapter_id` in workflow tasks is the instance name
8. Direct REST routes need auth role enablement — workflows work without it
9. Built-in roles cannot be updated — create custom roles
10. Response is raw HTTP (with headers, status) — use query task to extract `.data` for the actual payload
