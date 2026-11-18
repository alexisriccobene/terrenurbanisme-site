# Monuments historiques (base Mérimée, ministère de la Culture) -> table monuments (référence, nom, commune, protection, coordonnées)
import csv, io, json, os, re, sys, urllib.request
csv.field_size_limit(10**9)
URL = 'https://ministere-culture.s3.sbg.io.cloud.ovh.net/POP/merimee.csv'
raw = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'TerrenUrbanisme'}), timeout=600).read()
print('taille', len(raw))
txt = raw.decode('utf-8-sig', 'replace')
first = txt[:4000].split('\n')[0]
sep = ';' if first.count(';') > first.count(',') else ','
rd = csv.DictReader(io.StringIO(txt), delimiter=sep)
H = rd.fieldnames; print('colonnes', H[:80])
def col(*names):
    for n in names:
        for h in H:
            if h.strip().lower() == n.lower(): return h
    return None
cREF = col('REF', 'reference', 'Référence'); cNOM = col('TICO', 'Titre courant', 'appellation_courante', 'TITR'); cCOM = col('COM', 'Commune forme index', 'commune'); cINS = col('INSEE', 'Cog insee lors de la protection', 'code_insee')
cPRO = col('PROT', 'Typologie de la protection', 'protection', 'DPRO'); cDPRO = col('DPRO', 'Date et typologie de la protection'); cCOO = col('POP_COORDONNEES', 'coordonnees_au_format_wgs84', 'Coordonnées au format WGS84', 'COORM', 'coordonnees')
print('choix', cREF, cNOM, cCOM, cINS, cPRO, cDPRO, cCOO)
rows, n = [], 0
for r in rd:
    n += 1
    ref = (r.get(cREF) or '').strip()
    if not ref.startswith('PA'): continue
    co = (r.get(cCOO) or '').strip(); lat = lon = None
    try:
        j = json.loads(co)
        if isinstance(j, dict): lat, lon = float(j.get('lat')), float(j.get('lon'))
    except Exception:
        m = re.findall(r'-?\d+\.\d+', co)
        if len(m) >= 2: a, b = float(m[0]), float(m[1]); lat, lon = (a, b) if abs(a) > abs(b) or a > 38 else (b, a)
    if lat is None or not (-25 < lon < 60 and -25 < lat < 52) or (lat == 0 and lon == 0): continue
    pro = ' '.join([(r.get(cPRO) or ''), (r.get(cDPRO) or '')]).lower()
    prot = 'classé' if 'class' in pro else 'inscrit' if 'inscr' in pro else ''
    rows.append({'ref': ref, 'nom': (r.get(cNOM) or '').strip()[:200], 'commune': (r.get(cCOM) or '').strip()[:80], 'insee': (r.get(cINS) or '').strip()[:5], 'protection': prot, 'lon': round(lon, 6), 'lat': round(lat, 6)})
print('lignes', n, 'monuments géolocalisés', len(rows))
print('exemples', rows[:3])
SR = os.environ['SR']; B = 'https://' + os.environ['REF'] + '.supabase.co/rest/v1/monuments'
H2 = {'apikey': SR, 'Authorization': 'Bearer ' + SR, 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates,return=minimal'}
seen = {}
for r in rows: seen[r['ref']] = r
rows = list(seen.values())
for i in range(0, len(rows), 2000):
    urllib.request.urlopen(urllib.request.Request(B, json.dumps(rows[i:i + 2000]).encode(), H2, method='POST'), timeout=120).read()
print('chargés', len(rows))
