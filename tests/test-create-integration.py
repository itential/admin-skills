"""
End-to-end test: Create an integration from an OpenAPI spec,
create an adapter instance, verify it works, build and run a workflow.

Uses JSONPlaceholder (https://jsonplaceholder.typicode.com) — free, no auth.
"""
import json, requests, time

BASE = "http://localhost:4000"
r = requests.post(f"{BASE}/login", json={"username": "admin", "password": "admin"})
TOKEN = r.text.strip('"')
P = {"token": TOKEN}
H = {"Content-Type": "application/json"}

def api(method, path, body=None):
    resp = getattr(requests, method.lower())(f"{BASE}{path}", params=P, headers=H, json=body)
    try: return resp.json()
    except: return {"_raw": resp.text[:300], "_status": resp.status_code}

def wait_job(jid, label=""):
    for i in range(20):
        time.sleep(2)
        d = api("GET", f"/operations-manager/jobs/{jid}").get("data",{})
        if d.get("status") in ("complete","error","canceled"):
            print(f"  {label} => {d['status']}")
            return d
    print(f"  {label} => TIMEOUT"); return d

print("=" * 60)
print("CREATE INTEGRATION FROM OPENAPI SPEC")
print("API: JSONPlaceholder (jsonplaceholder.typicode.com)")
print("=" * 60)
print(f"Auth OK\n")

# ============================================================
# STEP 1: Build an OpenAPI 3.0 spec for JSONPlaceholder
# ============================================================
print("--- 1. Build OpenAPI spec ---")
openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "JSONPlaceholder",
        "description": "Free fake API for testing and prototyping",
        "version": "1.0.0"
    },
    "servers": [
        {"url": "https://jsonplaceholder.typicode.com"}
    ],
    "paths": {
        "/posts": {
            "get": {
                "operationId": "getPosts",
                "summary": "Get all posts",
                "responses": {
                    "200": {
                        "description": "List of posts",
                        "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Post"}}}}
                    }
                }
            },
            "post": {
                "operationId": "createPost",
                "summary": "Create a post",
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/NewPost"}}}
                },
                "responses": {
                    "201": {"description": "Created post", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Post"}}}}
                }
            }
        },
        "/posts/{id}": {
            "get": {
                "operationId": "getPostById",
                "summary": "Get a post by ID",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "A post", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Post"}}}}
                }
            }
        },
        "/users": {
            "get": {
                "operationId": "getUsers",
                "summary": "Get all users",
                "responses": {
                    "200": {"description": "List of users", "content": {"application/json": {"schema": {"type": "array"}}}}
                }
            }
        },
        "/users/{id}": {
            "get": {
                "operationId": "getUserById",
                "summary": "Get a user by ID",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "A user", "content": {"application/json": {"schema": {"type": "object"}}}}
                }
            }
        }
    },
    "components": {
        "schemas": {
            "Post": {
                "type": "object",
                "properties": {
                    "userId": {"type": "integer"},
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "body": {"type": "string"}
                }
            },
            "NewPost": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                    "userId": {"type": "integer"}
                },
                "required": ["title", "body", "userId"]
            }
        }
    }
}
print(f"  Spec: {openapi_spec['info']['title']} v{openapi_spec['info']['version']}")
print(f"  Endpoints: {len(openapi_spec['paths'])}")

# ============================================================
# STEP 2: Create integration model from OpenAPI spec
# ============================================================
print("\n--- 2. Create integration model ---")
model_result = api("POST", "/integration-models", {"model": openapi_spec})
print(f"  Result: {json.dumps(model_result)[:400]}")

# Check what was created
print("\n--- 2b. Verify model ---")
models = api("GET", "/integration-models")
for m in models.get("integrationModels", []):
    if "jsonplaceholder" in m.get("model", "").lower() or "jsonplaceholder" in m.get("versionId", "").lower():
        print(f"  Model: {m['model']}")
        print(f"  VersionId: {m['versionId']}")
        print(f"  Host: {m.get('properties',{}).get('server',{}).get('host','?')}")
        model_name = m["model"]
        break
else:
    print("  Model not found. Listing all:")
    for m in models.get("integrationModels", []):
        print(f"    {m['model']}")
    model_name = None

if not model_name:
    print("\n  Model creation may have failed. Trying to proceed with what we have...")
    # List all models to find it
    for m in models.get("integrationModels", []):
        model_name = m["model"]
    if not model_name:
        print("  No models available. Exiting.")
        exit(1)

# ============================================================
# STEP 3: Create integration instance (adapter)
# ============================================================
print(f"\n--- 3. Create integration instance ---")
ADAPTER_NAME = "jsonplaceholder"
int_result = api("POST", "/integrations", {
    "name": ADAPTER_NAME,
    "model": model_name,
    "properties": {
        "id": ADAPTER_NAME,
        "type": model_name.split("_")[-1] if "_" in model_name else model_name,
        "properties": {
            "server": {
                "protocol": "https",
                "host": "jsonplaceholder.typicode.com",
                "base_path": ""
            },
            "authentication": {},
            "tls": {"enabled": False, "rejectUnauthorized": True}
        }
    }
})
print(f"  Result: {json.dumps(int_result)[:400]}")

# Wait for adapter to start
print("\n--- 3b. Wait for adapter ---")
for i in range(10):
    time.sleep(3)
    health = api("GET", "/health/adapters")
    adapters = health.get("results", health if isinstance(health, list) else [])
    for a in adapters:
        if a.get("id") == ADAPTER_NAME:
            print(f"  {a['id']}: state={a.get('state')} connection={a.get('connection',{}).get('state','?')}")
            if a.get("state") == "RUNNING":
                break
    else:
        continue
    break

# ============================================================
# STEP 4: Check available tasks
# ============================================================
print(f"\n--- 4. Check tasks ---")
tasks = api("GET", "/workflow_builder/tasks/list")
if isinstance(tasks, list):
    my_tasks = [t for t in tasks if ADAPTER_NAME in t.get("app", "").lower()]
    print(f"  Tasks for {ADAPTER_NAME}: {len(my_tasks)}")
    for t in my_tasks[:10]:
        print(f"    {t['name']:40s} {t.get('summary','')[:40]}")
    
    # Get the correct app name from apps/list
    apps = api("GET", "/automation-studio/apps/list")
    app_name = None
    if isinstance(apps, list):
        for a in apps:
            if ADAPTER_NAME in a.get("name", "").lower():
                app_name = a["name"]
                print(f"\n  apps/list name: {app_name}")
                break

# ============================================================
# STEP 5: Get task schema for getPostById
# ============================================================
if my_tasks:
    print(f"\n--- 5. Task schema ---")
    target = None
    for t in my_tasks:
        if "getpost" in t["name"].lower() and "id" in t["name"].lower():
            target = t; break
    if not target:
        target = my_tasks[0]
    
    loc_type = app_name or target.get("locationType", target["app"])
    schema = api("POST", "/automation-studio/multipleTaskDetails?dereferenceSchemas=true", {
        "inputsArray": [{"location": target["location"], "pckg": loc_type, "method": target["name"]}]
    })
    if isinstance(schema, list) and schema:
        s = schema[0]
        inc = s.get("variables",{}).get("incoming",{})
        out = s.get("variables",{}).get("outgoing",{})
        print(f"  Task: {s['app']}.{s['name']}")
        print(f"  Incoming: {list(inc.keys())}")
        print(f"  Outgoing: {list(out.keys())}")
    else:
        print(f"  Schema: {json.dumps(schema)[:200]}")
        inc = {"id": {}}
        out = {"response": {}}

    # ============================================================
    # STEP 6: Create workflow
    # ============================================================
    print(f"\n--- 6. Create workflow ---")
    wf = api("POST", "/automation-studio/automations", {"automation": {
        "name": "test_jsonplaceholder_getpost", "type": "automation",
        "canvasVersion": 3, "encodingVersion": 1, "font_size": 12,
        "tasks": {
            "workflow_start": {"name": "workflow_start", "groups": [], "nodeLocation": {"x": 300, "y": 600}},
            "a1b2": {
                "name": target["name"], "canvasName": target["name"],
                "summary": target.get("summary", target["name"]), "description": "",
                "location": "Adapter", "locationType": loc_type,
                "app": loc_type, "type": "automatic", "displayName": ADAPTER_NAME,
                "variables": {
                    "incoming": {k: f"$var.job.{k}" for k in inc if k != "adapter_id"},
                    "outgoing": {k: f"$var.job.{k}" for k in out},
                    "error": "", "decorators": []
                },
                "groups": [], "actor": "Pronghorn", "scheduled": False,
                "nodeLocation": {"x": 600, "y": 600}
            },
            "workflow_end": {"name": "workflow_end", "groups": [], "nodeLocation": {"x": 900, "y": 600}}
        },
        "transitions": {
            "workflow_start": {"a1b2": {"type": "standard", "state": "success"}},
            "a1b2": {"workflow_end": {"type": "standard", "state": "success"}},
            "workflow_end": {}
        },
        "groups": [],
        "inputSchema": {"type": "object", "properties": {k: {"type": "string"} for k in inc if k != "adapter_id"}, "required": list(inc.keys() - {"adapter_id"})},
        "outputSchema": {"type": "object", "properties": {k: {"type": "object"} for k in out}}
    }})
    
    if "created" in wf:
        wf_name = wf["created"]["name"]
        wf_id = wf["created"]["_id"]
        print(f"  Created: {wf_name}")
    else:
        print(f"  Failed: {json.dumps(wf)[:300]}")
        wf_id = None

    # ============================================================
    # STEP 7: Run workflow
    # ============================================================
    if wf_id:
        print(f"\n--- 7. Run workflow ---")
        variables = {k: "1" for k in inc if k != "adapter_id"}
        variables["adapter_id"] = ADAPTER_NAME
        print(f"  Variables: {variables}")
        
        j = api("POST", "/operations-manager/jobs/start", {
            "workflow": wf_name,
            "options": {"type": "automation", "variables": variables}
        })
        
        if j.get("data"):
            d = wait_job(j["data"]["_id"], "getpost")
            if d.get("error"):
                for e in d["error"]:
                    msg = e.get("message","")
                    if isinstance(msg, dict): msg = msg.get("displayString", msg.get("IAPerror",{}).get("displayString", json.dumps(msg)[:150]))
                    print(f"  Error: task={e.get('task','?')} msg={str(msg)[:150]}")
            else:
                v = {k:v for k,v in d.get("variables",{}).items() if k in out}
                print(f"  Output: {json.dumps(v, indent=2)[:500]}")
        else:
            print(f"  Start failed: {j.get('message', json.dumps(j)[:200])}")

        # Cleanup workflow
        print(f"\n--- 8. Cleanup ---")
        api("DELETE", f"/automation-studio/automations/{wf_id}")
        print(f"  Deleted workflow")

# Keep the integration and adapter for inspection
print(f"\n{'='*60}")
print(f"INTEGRATION: {ADAPTER_NAME}")
print(f"Model: {model_name}")
print(f"Left on platform for inspection (not deleted)")
print(f"{'='*60}")
