#!/bin/bash
# Admin Skills Validation Test
# Tests all admin-platform and admin-config endpoints on a live platform
#
# Usage:
#   ./test-admin-skills.sh <platform-url> <client-id> <client-secret>
#   ./test-admin-skills.sh https://platform-6.0-dev.se.itential.io client123 secret456
#
# For local dev:
#   ./test-admin-skills.sh http://localhost:4000 admin admin --local

set -e

BASE="${1:?Usage: ./test-admin-skills.sh <platform-url> <client-id> <client-secret>}"
CLIENT_ID="${2:?Missing client ID or username}"
CLIENT_SECRET="${3:?Missing client secret or password}"
AUTH_MODE="${4:-oauth}"

# Auth
if [ "$AUTH_MODE" = "--local" ]; then
  TOKEN=$(curl -s -X POST "$BASE/login" -H 'Content-Type: application/json' -d "{\"username\":\"$CLIENT_ID\",\"password\":\"$CLIENT_SECRET\"}")
  AUTH_HEADER=""
  TOKEN_PARAM="?token=$TOKEN"
else
  TOKEN=$(curl -s "$BASE/oauth/token" -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "client_id=$CLIENT_ID" \
    --data-urlencode "client_secret=$CLIENT_SECRET" \
    --data-urlencode 'grant_type=client_credentials' | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))")
  AUTH_HEADER="Authorization: Bearer $TOKEN"
  TOKEN_PARAM=""
fi

if [ -z "$TOKEN" ]; then echo "ERROR: Auth failed"; exit 1; fi
echo "Authenticated"
echo ""

# Helper
api() {
  local method=$1 path=$2
  if [ -n "$AUTH_HEADER" ]; then
    curl -s -X "$method" "$BASE$path" -H "$AUTH_HEADER" -H "Content-Type: application/json" ${3:+-d "$3"}
  else
    curl -s -X "$method" "$BASE$path$TOKEN_PARAM" -H "Content-Type: application/json" ${3:+-d "$3"}
  fi
}

PASS=0
FAIL=0

check() {
  local name=$1 result=$2
  if [ -n "$result" ] && [ "$result" != "null" ] && [ "$result" != "" ]; then
    echo "  PASS: $name"
    PASS=$((PASS+1))
  else
    echo "  FAIL: $name"
    FAIL=$((FAIL+1))
  fi
}

echo "=========================================="
echo "ADMIN-PLATFORM TESTS"
echo "=========================================="

# 1. Version
echo ""
echo "--- Health ---"
V=$(api GET /version | python3 -c "import json,sys; print(json.load(sys.stdin))" 2>/dev/null)
check "GET /version" "$V"
echo "    Version: $V"

# 2. Server health
S=$(api GET /health/server | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('version',''))" 2>/dev/null)
check "GET /health/server" "$S"

# 3. System health
M=$(api GET /health/system | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('totalmem',0))" 2>/dev/null)
check "GET /health/system" "$M"

# 4. Whoami
W=$(api GET /whoami | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('username',''))" 2>/dev/null)
check "GET /whoami" "$W"
echo "    User: $W"

# 5. Adapter health
echo ""
echo "--- Adapters ---"
AC=$(api GET /health/adapters | python3 -c "
import json,sys; d=json.load(sys.stdin)
adapters = d.get('results', d if isinstance(d,list) else [])
running = sum(1 for a in adapters if a.get('state')=='RUNNING')
stopped = sum(1 for a in adapters if a.get('state')!='RUNNING')
print(f'{running}')
" 2>/dev/null)
check "GET /health/adapters" "$AC"
echo "    Running adapters: $AC"

# 6. Application health
AP=$(api GET /health/applications | python3 -c "
import json,sys; d=json.load(sys.stdin)
apps = d.get('results', d if isinstance(d,list) else [])
print(len(apps))
" 2>/dev/null)
check "GET /health/applications" "$AP"
echo "    Applications: $AP"

# 7. Workers
echo ""
echo "--- Engine ---"
JW=$(api GET /workflow_engine/workers/status | python3 -c "import json,sys; print(json.load(sys.stdin).get('jobWorker',{}).get('running',''))" 2>/dev/null)
check "GET /workflow_engine/workers/status" "$JW"

# 8. Rate limit
RL=$(api GET /workflow_engine/workers/rate_limit | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('rateLimit',''))" 2>/dev/null)
check "GET /workflow_engine/workers/rate_limit" "$RL"

# 9. Indexes
echo ""
echo "--- Indexes ---"
IX=$(api GET /indexes | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d))" 2>/dev/null)
check "GET /indexes" "$IX"
echo "    Collections: $IX"

echo ""
echo "=========================================="
echo "ADMIN-CONFIG TESTS"
echo "=========================================="

# 10. Accounts
echo ""
echo "--- Auth ---"
AT=$(api GET /authorization/accounts | python3 -c "import json,sys; print(json.load(sys.stdin).get('total',''))" 2>/dev/null)
check "GET /authorization/accounts" "$AT"
echo "    Accounts: $AT"

# 11. Groups
GT=$(api GET /authorization/groups | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('results',[])))" 2>/dev/null)
check "GET /authorization/groups" "$GT"
echo "    Groups: $GT"

# 12. Roles
RT=$(api GET /authorization/roles | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('results',[])))" 2>/dev/null)
check "GET /authorization/roles" "$RT"
echo "    Roles: $RT"

# 13. Service accounts
echo ""
echo "--- OAuth ---"
SA=$(api GET /oauth/serviceAccounts | python3 -c "import json,sys; print(json.load(sys.stdin).get('total',''))" 2>/dev/null)
check "GET /oauth/serviceAccounts" "$SA"
echo "    Service accounts: $SA"

# 14. SSO
echo ""
echo "--- SSO ---"
SS=$(api GET /sso/configs | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('results',[])))" 2>/dev/null)
check "GET /sso/configs" "$SS"
SE=$(api GET /sso/enabled | python3 -c "import json,sys; print(json.load(sys.stdin))" 2>/dev/null)
check "GET /sso/enabled" "$SE"
echo "    SSO configs: $SS, enabled: $SE"

echo ""
echo "=========================================="
echo "RESULTS: $PASS passed, $FAIL failed"
echo "=========================================="
