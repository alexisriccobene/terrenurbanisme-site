# Recalcule le poste électrique le plus proche dans les fichiers détaillés déjà chargés, puis réécrit fichiers et tuiles
import requests, json, gzip, os, math, time, sys
from collections import defaultdict
H = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
base = f"https://{os.environ['REF']}.supabase.co"; HS = {'apikey': os.environ['SR'], 'Authorization': 'Bearer ' + os.environ['SR']}
q = '[out:json][timeout:600];area["ISO3166-1"="FR"][admin_level=2]->.a;(node["power"="substation"](area.a);way["power"="substation"](area.a););out center tags;'
P = []
for t in range(3):
    for u in ['https://overpass-api.de/api/interpreter', 'https://overpass.private.coffee/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']:
        try:
            el = requests.post(u, data={'data': q}, headers=H, timeout=700).json()['elements']
            for e in el:
                c = e.get('center') or e; tg = e.get('tags', {})
                if 'lat' not in c or 'lon' not in c: continue
                sub = tg.get('substation') or ''; v = tg.get('voltage') or ''
                if sub in ('minor_distribution', 'industrial', 'traction', 'converter'): continue
                if not (v or sub in ('transmission', 'distribution')): continue
                P.append([round(c['lat'], 5), round(c['lon'], 5), (tg.get('name') or tg.get('ref') or 'Poste électrique')[:60], v[:30], tg.get('operator', '')[:30]])
            if P: break
        except Exception as ex: print('overpass', u, str(ex)[:150], flush=True)
    if P: break
    time.sleep(60)
print('postes', len(P), flush=True)
print('exemples Corse', [p for p in P if 41.3 < p[0] < 43.1 and 8.5 < p[1] < 9.6][:6], flush=True)
if len(P) < 1000: sys.exit('postes insuffisants')
def hav(a, b, c, d):
    p = math.pi / 180; x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))
PG = defaultdict(list)
for p in P: PG[(math.floor(p[0] * 2), math.floor(p[1] * 2))].append(p)
def near(lat, lon):
    cy, cx = math.floor(lat * 2), math.floor(lon * 2)
    for rad in range(1, 12):
        best = None
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                for p in PG.get((cy + dy, cx + dx), ()):
                    d = hav(lat, lon, p[0], p[1])
                    if best is None or d < best[0]: best = (d, p)
        if best and best[0] <= rad * 0.5 * 111 * math.cos(math.radians(lat)): return best
    return best
def up(path, data):
    for t in range(4):
        rr = requests.post(f'{base}/storage/v1/object/foncier/{path}', headers={**HS, 'Content-Type': 'application/gzip', 'x-upsert': 'true'}, data=data, timeout=600)
        if rr.status_code < 300: return
        time.sleep(5)
    print('échec envoi', path, rr.status_code, flush=True)
deps = sorted(x['dep'] for x in requests.get(f'{base}/rest/v1/fon_deps?select=dep', headers=HS, timeout=60).json())
for dep in deps:
    r = requests.get(f'{base}/storage/v1/object/foncier/{dep}.json.gz', headers=HS, timeout=600)
    if r.status_code != 200: print(dep, 'absent', flush=True); continue
    L = json.loads(gzip.decompress(r.content)); ks = []
    for s in L:
        b = near(s['lat'], s['lon'])
        if b: s['poste_km'] = round(b[0], 2); s['poste_nom'] = b[1][2]; s['poste_tension'] = b[1][3]; s['poste_exploitant'] = b[1][4]; ks.append(b[0])
    up(f'{dep}.json.gz', gzip.compress(json.dumps(L, ensure_ascii=False, separators=(',', ':')).encode()))
    T = defaultdict(list)
    for s in L: T[(math.floor(s['lat'] / 0.25), math.floor(s['lon'] / 0.25))].append(s)
    for (ty, tx), l in T.items(): up(f't/{dep}/{ty}_{tx}.json.gz', gzip.compress(json.dumps(l, ensure_ascii=False, separators=(',', ':')).encode()))
    ks.sort(); print(dep, len(L), 'sites, distance médiane au poste', round(ks[len(ks) // 2], 1) if ks else None, 'km,', len(T), 'tuiles', flush=True)
