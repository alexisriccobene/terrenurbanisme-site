"""Copie dans le stockage TerrenUrbanisme les règlements PDF des zonages communaux (lecture fiable et rapide)."""
import os, requests, hashlib
base = f"https://{os.environ['REF']}.supabase.co"; K = os.environ['SR']
H = {'apikey': K, 'Authorization': 'Bearer ' + K}
rows = requests.get(f'{base}/rest/v1/zonage_local?select=id,insee,urlfic&copie=is.null', headers=H, timeout=60).json()
done = {}
for r in rows:
    u = r['urlfic']
    if not u: continue
    if u not in done:
        try:
            b = requests.get(u, headers={'User-Agent': 'Mozilla/5.0'}, timeout=120).content
            if not b.startswith(b'%PDF'): print('pas un PDF', u); done[u] = None; continue
            name = f"{r['insee']}/{hashlib.md5(u.encode()).hexdigest()[:10]}-{u.rsplit('/', 1)[-1]}"
            x = requests.post(f'{base}/storage/v1/object/plu/{name}', headers={**H, 'Content-Type': 'application/pdf', 'x-upsert': 'true'}, data=b, timeout=120)
            print(x.status_code, name, len(b)); done[u] = f'{base}/storage/v1/object/public/plu/{name}' if x.status_code < 300 else None
        except Exception as e: print('erreur', u, e); done[u] = None
    if done[u]:
        requests.patch(f"{base}/rest/v1/zonage_local?id=eq.{r['id']}", headers={**H, 'Content-Type': 'application/json'}, json={'copie': done[u]}, timeout=60)
print('ok', len(done))
