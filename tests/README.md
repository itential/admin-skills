# Tests

These scripts exercise the skills' API calls against a **live** Itential platform — they are not run in CI.

| Script | What it checks | Run |
|---|---|---|
| `test-admin-skills.sh` | Every admin-platform and admin-config endpoint | `./tests/test-admin-skills.sh <platform-url> <client-id> <client-secret>` (add `--local` for username/password) |
| `test-create-integration.py` | Creating a codeless integration from an OpenAPI spec | edit `BASE` (defaults to `http://localhost:4000`), then `python3 tests/test-create-integration.py` |
| `test-integration-e2e.py` | Integration end to end: create, instance, workflow, run | edit `BASE`, then `python3 tests/test-integration-e2e.py` |

`observations.md` records platform behavior observed in these runs.
