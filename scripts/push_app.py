#!/usr/bin/env python3
"""
Pushib äpi faili GitHubi (visuaalmootor/Treener main branch).

Kasutus:
    python3 scripts/push_app.py                                → app.html, vaikimisi sõnum
    python3 scripts/push_app.py "commit sõnum"                 → app.html
    python3 scripts/push_app.py app2.html "commit sõnum"       → app2.html (v0.9.3+ redesign)
    python3 scripts/push_app.py service-worker.js "sõnum"      → service-worker.js
    python3 scripts/push_app.py "commit sõnum" app2.html       → järjekord vaba

Argument mis lõpeb ".html" või ".js" = failinimi; ülejäänud = commit sõnum.

GitHub token:
    1) Env muutuja:  export GITHUB_TOKEN=ghp_xxx
    2) Fail:         .github_token  (projekti juurkaustas)
"""

import os, sys, base64, json, ssl, socket, re
import urllib.request, urllib.error

# v0.9.7.4-järgne fix: urlopen() ei saanud kunagi timeout't, mistõttu võrgu-hängimise
# korral (nt VPN/firewall, mis paketid vaikselt ära viskab, mitte ei lükka tagasi)
# jäi skript IGAVESEKS kinni ilma veateateta. Nüüd 20s timeout + selge sõnum.
REQUEST_TIMEOUT_S = 20

# macOS Python 3.14 SSL fix — isiklikul tööriistal ohutu
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode    = ssl.CERT_NONE

# ── Konfiguratsioon ──────────────────────────────────────────────────────────
REPO_OWNER = "visuaalmootor"
REPO_NAME  = "Treener"
BRANCH     = "main"

# ── Argumendid: .html/.js-lõpuga arg = failinimi, ülejäänud = commit sõnum ──────
FILE_PATH  = "app.html"
_msg_parts = []
for arg in sys.argv[1:]:
    if arg.lower().endswith((".html", ".js", ".md", ".json", ".py")):
        FILE_PATH = arg
    else:
        _msg_parts.append(arg)

commit_msg = " ".join(_msg_parts) if _msg_parts else f"Uuenda {FILE_PATH}"

# ── Token ────────────────────────────────────────────────────────────────────
token = os.environ.get("GITHUB_TOKEN", "").strip()
if not token:
    token_file = os.path.join(os.path.dirname(__file__), "..", ".github_token")
    if os.path.isfile(token_file):
        token = open(token_file).read().strip()

if not token:
    print("❌  GitHub token puudub.")
    print("    Lisa token ühel viisil:")
    print("      export GITHUB_TOKEN=ghp_xxxxxxxxxxxx")
    print("      VÕI pane token faili .github_token (projekti juurkaustas)")
    sys.exit(1)

# ── Loe fail ─────────────────────────────────────────────────────────────────
root      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_path  = os.path.join(root, FILE_PATH)

if not os.path.isfile(app_path):
    print(f"❌  {app_path} ei leitud")
    sys.exit(1)

with open(app_path, "rb") as f:
    content_bytes = f.read()

print(f"📄  {FILE_PATH}  ({len(content_bytes)/1024:.0f} KB)")

# ── GitHub API ───────────────────────────────────────────────────────────────
headers = {
    "Authorization": f"token {token}",
    "Accept":        "application/vnd.github+json",
    "Content-Type":  "application/json",
    "User-Agent":    "btb-treener-push",
    "X-GitHub-Api-Version": "2022-11-28",
}
api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

# 1. Hangi praegune SHA + versioonikontroll (uue faili puhul SHA puudub — see on OK)
print("📡  Hangin praeguse SHA...")
sha = None
req = urllib.request.Request(f"{api_url}?ref={BRANCH}", headers=headers)
try:
    with urllib.request.urlopen(req, context=_ssl_ctx, timeout=REQUEST_TIMEOUT_S) as resp:
        current = json.loads(resp.read())
        sha = current["sha"]
        print(f"    SHA: {sha[:10]}...")

        # Versioonikontroll: hoiata kui GitHub on uuem kui kohalik
        remote_content = base64.b64decode(current["content"]).decode("utf-8", errors="replace")
        local_content  = content_bytes.decode("utf-8", errors="replace")
        def _ver(txt):
            m = re.search(r"APP_VERSION\s*=\s*['\"]([^'\"]+)['\"]", txt)
            return m.group(1) if m else None
        remote_ver = _ver(remote_content)
        local_ver  = _ver(local_content)
        if remote_ver and local_ver:
            print(f"    GitHub versioon: v{remote_ver}  |  Kohalik: v{local_ver}")
            if remote_ver > local_ver:
                print(f"\n⚠️  HOIATUS: GitHub on UUEM (v{remote_ver}) kui kohalik fail (v{local_ver})!")
                print(f"    Tõenäoliselt on teine chat teinud muutusi, mis lähevad kaduma.")
                print(f"    Soovitus: käivita esmalt  python3 scripts/pull_app.py  ja rakenda muutused uuesti.")
                ans = input("    Jätka ikkagi push'iga? [j/ei] ").strip().lower()
                if ans not in ("j", "jah", "y", "yes"):
                    print("    Push tühistatud. Käivita: python3 scripts/pull_app.py")
                    sys.exit(0)

except urllib.error.HTTPError as e:
    if e.code == 404:
        print(f"    Fail {FILE_PATH} pole veel repos — loon uue.")
    else:
        body = e.read().decode()
        print(f"❌  SHA hankimine ebaõnnestus: {e.code} {e.reason}")
        print(body[:400])
        sys.exit(1)
except (socket.timeout, urllib.error.URLError) as e:
    print(f"❌  Ei saanud ühendust api.github.com-iga ({REQUEST_TIMEOUT_S}s timeout: {e}).")
    print("    See on VÕRGUPROBLEEM, mitte skripti viga. Proovi järgmist:")
    print("      1) curl -v https://api.github.com   ← kas see üldse vastab?")
    print("      2) kontrolli, kas VPN/firewall on sisse lülitatud")
    print("      3) proovi teist võrku (nt mobiili hotspot)")
    sys.exit(1)

# 2. Push
print(f"🚀  Pushin ({commit_msg})...")
payload_dict = {
    "message": commit_msg,
    "content": base64.b64encode(content_bytes).decode(),
    "branch":  BRANCH,
}
if sha:
    payload_dict["sha"] = sha
payload = json.dumps(payload_dict).encode()

req = urllib.request.Request(api_url, data=payload, method="PUT", headers=headers)
try:
    with urllib.request.urlopen(req, context=_ssl_ctx, timeout=REQUEST_TIMEOUT_S) as resp:
        result     = json.loads(resp.read())
        commit_url = result["commit"]["html_url"]
        print(f"✅  Valmis!")
        print(f"    Commit: {commit_url}")
        print(f"    GitHub Pages uueneb ~30–60 sek jooksul")
        print(f"    URL: https://{REPO_OWNER.lower()}.github.io/{REPO_NAME}/{FILE_PATH}")
except (socket.timeout, urllib.error.URLError) as e:
    print(f"❌  Ei saanud ühendust api.github.com-iga ({REQUEST_TIMEOUT_S}s timeout: {e}).")
    print("    See on VÕRGUPROBLEEM, mitte skripti viga. Proovi uuesti hetke pärast.")
    sys.exit(1)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"❌  Push ebaõnnestus: {e.code} {e.reason}")
    print(body[:400])
    sys.exit(1)
