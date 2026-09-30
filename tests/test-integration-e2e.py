"""
End-to-end integration test:
1. Create Petstore adapter integration
2. Verify adapter starts and is healthy
3. Check roles/permissions
4. Create a workflow that calls the adapter
5. Run it
6. Clean up
"""
import json, requests, time, urllib.parse

BASE = "http://localhost:4000"

# Auth
r = requests.post(f"{BASE}/login", json={"username": "admin", "password": "admin"})
TOKEN = r.text.strip('"')
P = {"token": TOKEN}
H = {"Content-Type": "application/json"}

def api(method, path, body=None):
    url = f"{BASE}{path}"
    resp = getattr(requests, method.lower())(url, params=P, headers=H, json=body)
    try: return resp.json()
    except: return {"_raw": resp.text[:200], "_status": resp.status_code}

def wait_job(jid, label=""):
    for i in range(20):
        time.sleep(2)
        d = api("GET", f"/operations-manager/jobs/{jid}").get("data", {})
        if d.get("status") in ("complete", "error", "canceled"):
            print(f"  {label} => {d['status']}")
            return d
    print(f"  {label} => TIMEOUT"); return d

print("=" * 60)
print("INTEGRATION E2E TEST: Petstore Adapter")
print("=" * 60)
print(f"Auth OK (token: {TOKEN[:10]}...)\n")

# ============================================================
# STEP 1: Check existing integration model
# ============================================================
print("--- 1. Check integration model ---")
models = api("GET", "/integration-models")
petstore_model = None
for m in models.get("integrationModels", []):
    if "petstore" in m.get("model", "").lower():
        petstore_model = m
        print(f"  Found: {m['model']}")
        print(f"  Host: {m.get('properties',{}).get('server',{}).get('host','?')}")
        break

if not petstore_model:
    print("  No Petstore model found. Exiting.")
    exit(1)

# ============================================================
# STEP 2: Check if Petstore integration already exists
# ============================================================
print("\n--- 2. Check existing integrations ---")
integrations = api("GET", "/integrations")
petstore_int = None
for i in integrations.get("results", []):
    idata = i.get("data", {})
    if "petstore" in idata.get("model", "").lower() or "petstore" in idata.get("name", "").lower():
        petstore_int = idata
        print(f"  Found existing: {idata.get('name')}")
        break

# ============================================================
# STEP 3: Create or use Petstore integration
# ============================================================
if not petstore_int:
    print("\n--- 3. Create Petstore integration ---")
    create_result = api("POST", "/integrations", {
        "name": "test-petstore",
        "model": petstore_model["model"],
        "properties": {
            "id": "test-petstore",
            "type": petstore_model.get("versionId", ""),
            "properties": {
                "authentication": {
                    "api_key": {"value": "special-key"},
                    "petstore_auth": {"token": {"access_token": ""}}
                },
                "server": {
                    "protocol": "https",
                    "host": "petstore.swagger.io",
                    "base_path": "/v2"
                },
                "tls": {"enabled": False, "rejectUnauthorized": True}
            }
        }
    })
    print(f"  Result: {json.dumps(create_result)[:300]}")
    adapter_name = "test-petstore"
else:
    adapter_name = petstore_int.get("name", "zzz")
    print(f"\n--- 3. Using existing: {adapter_name} ---")

# ============================================================
# STEP 4: Check adapter health
# ============================================================
print(f"\n--- 4. Check adapter health: {adapter_name} ---")
time.sleep(3)  # Give adapter time to start
health = api("GET", "/health/adapters")
adapters = health.get("results", health if isinstance(health, list) else [])
for a in adapters:
    if a.get("id") == adapter_name or "petstore" in a.get("id", "").lower():
        print(f"  {a['id']}: state={a.get('state')} connection={a.get('connection',{}).get('state','?')}")
        adapter_name = a["id"]  # Use exact name
        break
else:
    print(f"  Adapter {adapter_name} not found in health. Checking all:")
    for a in adapters:
        print(f"    {a['id']}: {a.get('state')}")

# ============================================================
# STEP 5: Check what tasks are available from this adapter
# ============================================================
print(f"\n--- 5. Available tasks from adapter ---")
tasks = api("GET", "/workflow_builder/tasks/list")
if isinstance(tasks, list):
    pet_tasks = [t for t in tasks if adapter_name.lower() in t.get("app", "").lower() or "petstore" in t.get("app", "").lower()]
    print(f"  Total platform tasks: {len(tasks)}")
    print(f"  Petstore tasks: {len(pet_tasks)}")
    for t in pet_tasks[:10]:
        print(f"    {t['app']}.{t['name']:40s} {t.get('summary','')[:40]}")
    if len(pet_tasks) > 10:
        print(f"    ... +{len(pet_tasks)-10} more")
else:
    print(f"  Unexpected response: {json.dumps(tasks)[:200]}")

# Find the correct app name from apps/list
print(f"\n--- 5b. App name from apps/list ---")
apps = api("GET", "/automation-studio/apps/list")
if isinstance(apps, list):
    for a in apps:
        if "petstore" in a.get("name", "").lower() or adapter_name.lower() == a.get("name", "").lower():
            print(f"  apps/list name: {a['name']}  type: {a['type']}")

# ============================================================
# STEP 6: Check roles
# ============================================================
print(f"\n--- 6. Check roles for adapter access ---")
roles = api("GET", "/authorization/roles")
for r in roles.get("results", []):
    methods = r.get("allowedMethods", [])
    # Check if this role has adapter methods
    adapter_methods = [m for m in methods if adapter_name in m.get("provenance", "")]
    if adapter_methods:
        print(f"  Role '{r['name']}' has {len(adapter_methods)} methods for {adapter_name}")

# Check current user's access
print(f"\n--- 6b. Current user ---")
whoami = api("GET", "/whoami")
print(f"  User: {whoami.get('username')}")
print(f"  Groups: {[g.get('name') for g in whoami.get('groups', [])]}")

# ============================================================
# STEP 7: Get task schema for a Petstore method
# ============================================================
if pet_tasks:
    print(f"\n--- 7. Get task schema ---")
    # Find getPetById or similar
    target_task = None
    for t in pet_tasks:
        if "getpet" in t["name"].lower() or "findpet" in t["name"].lower():
            target_task = t
            break
    if not target_task:
        target_task = pet_tasks[0]
    
    print(f"  Task: {target_task['app']}.{target_task['name']}")
    
    # Get schema
    schema = api("POST", "/automation-studio/multipleTaskDetails?dereferenceSchemas=true", {
        "inputsArray": [{"location": target_task["location"], "pckg": target_task.get("locationType", target_task["app"]), "method": target_task["name"]}]
    })
    if isinstance(schema, list) and schema:
        s = schema[0]
        inc = s.get("variables", {}).get("incoming", {})
        out = s.get("variables", {}).get("outgoing", {})
        print(f"  Incoming: {list(inc.keys())}")
        print(f"  Outgoing: {list(out.keys())}")
    else:
        print(f"  Schema response: {json.dumps(schema)[:200]}")

    # ============================================================
    # STEP 8: Create a simple workflow
    # ============================================================
    print(f"\n--- 8. Create workflow ---")
    
    # Use the correct app name from apps/list
    app_name = target_task.get("app", adapter_name)
    loc_type = target_task.get("locationType", app_name)
    
    wf = api("POST", "/automation-studio/automations", {"automation": {
        "name": "test_petstore_workflow", "type": "automation", "canvasVersion": 3, "encodingVersion": 1, "font_size": 12,
        "tasks": {
            "workflow_start": {"name": "workflow_start", "groups": [], "nodeLocation": {"x": 300, "y": 600}},
            "a1b2": {
                "name": target_task["name"], "canvasName": target_task["name"],
                "summary": target_task.get("summary", target_task["name"]),
                "description": target_task.get("description", ""),
                "location": target_task["location"], "locationType": loc_type,
                "app": app_name, "type": target_task.get("type", "automatic"),
                "displayName": target_task.get("displayName", app_name),
                "variables": {
                    "incoming": {k: f"$var.job.{k}" for k in inc.keys() if k != "adapter_id"},
                    "outgoing": {k: f"$var.job.{k}" for k in out.keys()},
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
        "inputSchema": {"type": "object", "properties": {k: {"type": "string"} for k in inc.keys() if k != "adapter_id"}},
        "outputSchema": {"type": "object", "properties": {k: {"type": "string"} for k in out.keys()}}
    }})
    
    if "created" in wf:
        wf_id = wf["created"]["_id"]
        wf_name = wf["created"]["name"]
        print(f"  Created: {wf_name} ({wf_id})")
    elif "error" in wf:
        print(f"  ERROR: {json.dumps(wf)[:300]}")
        wf_id = None
    else:
        print(f"  Response: {json.dumps(wf)[:300]}")
        wf_id = None

    # ============================================================
    # STEP 9: Run the workflow
    # ============================================================
    if wf_id:
        print(f"\n--- 9. Run workflow ---")
        # Build variables — use sample values from schema
        variables = {}
        for k, v in inc.items():
            if k == "adapter_id":
                continue
            if isinstance(v, dict):
                examples = v.get("schema", {}).get("examples", [])
                if examples:
                    variables[k] = examples[0]
                elif v.get("schema", {}).get("type") == "string":
                    variables[k] = "1"
                else:
                    variables[k] = "1"
            else:
                variables[k] = "1"
        
        # Add adapter_id
        if "adapter_id" in inc:
            variables["adapter_id"] = adapter_name
        
        print(f"  Variables: {json.dumps(variables)}")
        
        j = api("POST", "/operations-manager/jobs/start", {
            "workflow": wf_name,
            "options": {"type": "automation", "variables": variables}
        })
        
        if j.get("data"):
            d = wait_job(j["data"]["_id"], "petstore")
            if d.get("error"):
                print(f"  Errors:")
                for e in d["error"]:
                    if isinstance(e, dict):
                        print(f"    task={e.get('task','?')} msg={json.dumps(e.get('message',''))[:150]}")
                    else:
                        print(f"    {str(e)[:150]}")
            else:
                v = {k: v for k, v in d.get("variables", {}).items() if not k.startswith("_") and k != "initiator"}
                print(f"  Result variables: {json.dumps(v, indent=2)[:500]}")
        else:
            print(f"  Start failed: {j.get('message', json.dumps(j)[:200])}")

        # ============================================================
        # STEP 10: Cleanup
        # ============================================================
        print(f"\n--- 10. Cleanup ---")
        api("DELETE", f"/automation-studio/automations/{wf_id}")
        print(f"  Deleted workflow")

print(f"\n{'='*60}")
print("INTEGRATION E2E TEST COMPLETE")
print(f"{'='*60}")
