# Découpe les fichiers détaillés par département (foncier/<dep>.json.gz) en tuiles de 0,25° (foncier/t/<dep>/<ty>_<tx>.json.gz)
# pour que le rapport ne charge que le secteur recherché.
import requests, json, gzip, os, sys, math, time
from collections import defaultdict
base = f"https://{os.environ['REF']}.supabase.co"
HS = {'apikey': os.environ['SR'], 'Authorization': 'Bearer ' + os.environ['SR']}
T = 0.25
def tiles(dep):
    r = requests.get(f'{base}/storage/v1/object/foncier/{dep}.json.gz', headers=HS, timeout=600)
    if r.status_code != 200: print(dep, 'absent', r.status_code, flush=True); return 0
    sites = json.loads(gzip.decompress(r.content))
    g = defaultdict(list)
    for s in sites: g[(math.floor(s['lat'] / T), math.floor(s['lon'] / T))].append(s)
    for (ty, tx), l in g.items():
        data = gzip.compress(json.dumps(l, ensure_ascii=False, separators=(',', ':')).encode())
        for t in range(4):
            rr = requests.post(f'{base}/storage/v1/object/foncier/t/{dep}/{ty}_{tx}.json.gz', headers={**HS, 'Content-Type': 'application/gzip', 'x-upsert': 'true'}, data=data, timeout=300)
            if rr.status_code < 300: break
            time.sleep(5)
        else: print(dep, 'échec tuile', ty, tx, rr.status_code, rr.text[:120], flush=True)
    print(dep, len(sites), 'sites', len(g), 'tuiles', flush=True)
    return len(g)
deps = requests.get(f'{base}/rest/v1/fon_deps?select=dep', headers=HS, timeout=60).json()
dj = json.load(open('.github/foncier/demande.json'))
only = dj.get('deps') or (os.environ.get('DEPS', '').split(',') if os.environ.get('DEPS') else None)
for d in sorted(x['dep'] for x in deps):
    if only and d not in only: continue
    try: tiles(d)
    except Exception as e: print(d, 'erreur', e, flush=True)
