#!/usr/bin/env python3
"""
Laeb GitHubist viimase versiooni kohalikku faili.
Kasuta ALATI enne töö alustamist, et vältida versioonide ülekirjutamist.

Kasutus:
    python3 scripts/pull_app.py              → app2.html (vaikimisi)
    python3 scripts/pull_app.py app2.html
    python3 scripts/pull_app.py WORKLOG.md
    python3 scripts/pull_app.py data/exercises.json

GitHub token:
    1) Env muutuja:  export GITHUB_TOKEN=ghp_xxx
    2) Fail:         .github_token  (projekti juurkaustas)
"""

import os, sys, base64, json, ssl, socket, re
import urllib.request, urllib.error

REQUEST_TIMEOUT_S = 20

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode    = ssl.CERT_NONE

REPO_OWNER = "visuaalmootor"
REPO_NAME  = "Treener"
BRANCH     = "main"

# ── Argumendid ────────────────────────────────────────────────────────────────
FILE_PATH = sys.argv[1] if len(sys.argv) > 1 else "app2.html"

# ── Token ─────────────────────────────────────────────────────────────────────
token = os.environ.get("GITHUB_TOKEN", "").strip()
if not token:
    token_file = os.path.join(os.path.dirname(__file__), "..", ".github_token")
    if os.path.isfile(token_file):
        token = open(token_file).read().strip()

if not token:
    print("❌  GitHub token puudub.")
    print("    Lisa .github_token faili projekti juurkausta.")
    sys.exit(1)

headers = {
    "Authorization": f"token {token}",
    "Accept":        "application/vnd.github+json",
    "User-Agent":    "btb-treener-pull",
    "X-GitHub-Api-Version": "2022-11-28",
}

root      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
local_path = os.path.join(root, FILE_PATH)

# ── Loe kohalik versioon (kui olemas) ─────────────────────────────────────────
local_version = None
if os.path.isfile(local_path):
    try:
        local_content = open(local_path, encoding="utf-8").read()
        m = re.search(r"APP_VERSION\s*=\s*['\"]([^'\"]+)['\"]", local_content)
        if m:
            local_version = m.group(1)
    except Exception:
        pass

# ── Hangi GitHubist ───────────────────────────────────────────────────────────
print(f"📡  Hangin {FILE_PATH} GitHubist ({REPO_OWNER}/{REPO_NAME}@{BRANCH})...")
api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
req = urllib.request.Request(f"{api_url}?ref={BRANCH}", headers=headers)

try:
    with urllib.request.urlopen(req, context=_ssl_ctx, timeout=REQUEST_TIMEOUT_S) as resp:
        data = json.loads(resp.read())
except urllib.error.HTTPError as e:
    if e.code == 404:
        print(f"❌  {FILE_PATH} ei leitud repos.")
    else:
        print(f"❌  GitHub API viga: {e.code} {e.reason}")
    sys.exit(1)
except (socket.timeout, urllib.error.URLError) as e:
    print(f"❌  Võrguprobleem ({REQUEST_TIMEOUT_S}s timeout): {e}")
    sys.exit(1)

remote_bytes   = base64.b64decode(data["content"])
remote_content = remote_bytes.decode("utf-8")

# ── Loe remote versioon ───────────────────────────────────────────────────────
remote_version = None
m = re.search(r"APP_VERSION\s*=\s*['\"]([^'\"]+)['\"]", remote_content)
if m:
    remote_version = m.group(1)

# ── Võrdle ───────────────────────────────────────────────────────────────────
print(f"    GitHub:  v{remote_version or '?'}")
print(f"    Kohalik: v{local_version or '(puudub)'}")

if local_version and remote_version and local_version == remote_version:
    print(f"✅  Versioonid kattuvad (v{local_version}) — kohalik fail on ajakohane.")
    sys.exit(0)

if local_version and remote_version and local_version > remote_version:
    print(f"⚠️   Kohalik versioon ({local_version}) on UUEM kui GitHub ({remote_version}).")
    print(f"    Kas oled kindel, et tahad GitHubi versiooniga üle kirjutada?")
    ans = input("    Jätka? [j/ei] ").strip().lower()
    if ans not in ("j", "jah", "y", "yes"):
        print("    Tühistatud.")
        sys.exit(0)

# ── Kirjuta kohalikku faili ───────────────────────────────────────────────────
os.makedirs(os.path.dirname(local_path), exist_ok=True)
with open(local_path, "wb") as f:
    f.write(remote_bytes)

size_kb = len(remote_bytes) / 1024
print(f"✅  {FILE_PATH} uuendatud ({size_kb:.0f} KB)")
if remote_version:
    print(f"    Versioon: v{remote_version}")
print(f"    Commit SHA: {data['sha'][:10]}...")
