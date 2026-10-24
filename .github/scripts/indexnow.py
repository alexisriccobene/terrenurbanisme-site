import json, re, time, urllib.request, sys
SITE = "https://terrenurbanisme.com"
KEY = "ce0fe1cd39aa756b11fa74f4813ce64e"
# Attendre que Netlify publie la nouvelle version (la clé doit être en ligne)
for i in range(30):
    try:
        if urllib.request.urlopen(f"{SITE}/{KEY}.txt", timeout=20).read().decode().strip() == KEY: break
    except Exception: pass
    time.sleep(30)
else:
    sys.exit("clé IndexNow introuvable en ligne")
urls = re.findall(r"<loc>([^<]+)</loc>", open("sitemap.xml", encoding="utf-8").read())
for i in range(0, len(urls), 9000):
    body = json.dumps({"host": "terrenurbanisme.com", "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt", "urlList": urls[i:i+9000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    r = urllib.request.urlopen(req, timeout=60)
    print("IndexNow", i, len(urls[i:i+9000]), "->", r.status)
