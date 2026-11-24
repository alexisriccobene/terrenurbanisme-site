"""Envoie dans le stockage (plu/<insee>/reg_<ZONE>.pdf) les chapitres de règlement découpés, pris sur la branche plu-src."""
import os, json, requests
base = f"https://{os.environ['REF']}.supabase.co"; K = os.environ['SR']
H = {'apikey': K, 'Authorization': 'Bearer ' + K}
D = json.load(open('.github/plu-demande.json'))
for ins in D['insee']:
    raw = f"https://raw.githubusercontent.com/alexisriccobene/terrenurbanisme-site/plu-src/{ins}/reg"
    ch = requests.get(raw + '/chapitres.json', timeout=60).json()
    for c in ch:
        b = requests.get(f"{raw}/reg_{c['zone']}.pdf", timeout=120).content
        assert b.startswith(b'%PDF'), c
        r = requests.post(f"{base}/storage/v1/object/plu/{ins}/reg_{c['zone']}.pdf", headers={**H, 'Content-Type': 'application/pdf', 'x-upsert': 'true'}, data=b, timeout=120)
        print(ins, c['zone'], r.status_code, len(b))
