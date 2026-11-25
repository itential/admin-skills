#!/usr/bin/env python3
"""Save a new service account's credentials straight to a .env file, without printing the secret.

Pipe the response of creating a service account (POST /oauth/serviceAccounts) or regenerating
its secret (PATCH /oauth/serviceAccounts/{client_id}/regenerate) into this script. It writes
<dir>/.env (mode 600) with PLATFORM_URL, CLIENT_ID and CLIENT_SECRET, and prints only the
client ID and where the file is. Test the account afterwards with the auth helper:
`python3 auth.py <dir>`.

    curl -s -K .auth.curl -X POST ... "<platform>/oauth/serviceAccounts" | python3 save_service_account.py <dir>
    curl -s -K .auth.curl -X PATCH "<platform>/oauth/serviceAccounts/<id>/regenerate" \\
        | python3 save_service_account.py <dir> --client-id <id>

PLATFORM_URL comes from ./.auth.json (the auth helper's file), or --platform-url.
Exit codes: 0 saved, 1 the response has no client secret (an error from the platform), 2 bad input.
Standard library only.
"""
import argparse
import json
import os
import sys


def find(obj, key):
    """First value for `key` anywhere in a JSON document."""
    if isinstance(obj, dict):
        if obj.get(key):
            return obj[key]
        for v in obj.values():
            found = find(v, key)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = find(v, key)
            if found:
                return found
    return None


def main():
    ap = argparse.ArgumentParser(description="Save a new service account's credentials without printing the secret.")
    ap.add_argument("dir", help="folder to write .env into (created if missing)")
    ap.add_argument("--client-id", help="client ID, when the response doesn't include it (regenerate)")
    ap.add_argument("--platform-url", help="platform URL (default: platform_url in ./.auth.json)")
    args = ap.parse_args()

    raw = sys.stdin.read()
    try:
        doc = json.loads(raw)
    except ValueError:
        print("error: the response isn't JSON — the call probably failed. Re-run it without this script to see the error, "
              "but don't print a successful response: it contains the secret.")
        sys.exit(1)
    secret = find(doc, "client_secret")
    client_id = find(doc, "client_id") or args.client_id
    if not secret:
        message = find(doc, "message") or find(doc, "error") or "no client_secret in the response"
        print(f"error: {str(message)[:200]}")
        sys.exit(1)
    if not client_id:
        print("error: the response has no client_id; pass it with --client-id")
        sys.exit(2)
    url = args.platform_url
    if not url and os.path.isfile(".auth.json"):
        url = json.load(open(".auth.json")).get("platform_url")
    if not url:
        print("error: no platform URL; run from the folder with .auth.json or pass --platform-url")
        sys.exit(2)

    os.makedirs(args.dir, exist_ok=True)
    path = os.path.join(args.dir, ".env")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(f"PLATFORM_URL={url.rstrip('/')}\nCLIENT_ID={client_id}\nCLIENT_SECRET={secret}\n")
    os.chmod(path, 0o600)
    print(f"ok: saved service account {client_id} to {path} (secret not shown). Test it: python3 auth.py {args.dir}")


if __name__ == "__main__":
    main()
