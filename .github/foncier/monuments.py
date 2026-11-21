# Monuments historiques (base Mérimée, ministère de la Culture) -> table monuments (référence, nom, commune, protection, coordonnées)
import csv, io, json, os, re, sys, urllib.request
csv.field_size_limit(10**9)
URL = 'https://ministere-culture.s3.sbg.io.cloud.ovh.net/POP/merimee.csv'
raw = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'TerrenUrbanisme'}), timeout=600).read()
print('taille', len(raw))
txt = raw.decode('utf-8-sig', 'replace')
first = txt[:4000].split('\n')[0]
sep = max(['|', ';', ','], key=lambda c: first.count(c))
rd = csv.DictReader(io.StringIO(txt), delimiter=sep)
H = rd.fieldnames; print('colonnes', H)
def col(*names):
    for n in names:
        for h in H:
            if h.strip().lower() == n.lower(): return h
    for n in names:
        for h in H:
            if n.lower() in h.strip().lower(): return h
    return None
cREF = col('Reference', 'REF'); cNOM = col('Titre_editorial_de_la_notice', 'Appellation_courante', 'Titre_courant', 'TICO'); cCOM = col('Commune_forme_editoriale', 'Commune_forme_index', 'COM'); cINS = col('Cog_insee_lors_de_la_protection', 'Cog_insee', 'INSEE')
cPRO = col('Typologie_de_la_protection', 'Nature_de_la_protection'); cDPRO = col('Date_et_typologie_de_la_protection'); cCOO = col('coordonnees_au_format_WGS84', 'Coordonnees_au_format_WGS84', 'WGS84', 'coordonnees')
print('choix', cREF, cNOM, cCOM, cINS, cPRO, cDPRO, cCOO)
rows, n = [], 0
for r in rd:
    n += 1
    ref = str(r.get(cREF) or '').strip()
    if not ref.startswith('PA'): continue
    co = str(r.get(cCOO) or '').strip(); lat = lon = None
    try:
        j = json.loads(co)
        if isinstance(j, dict): lat, lon = float(j.get('lat')), float(j.get('lon'))
    except Exception:
        m = re.findall(r'-?\d+\.\d+', co)
        if len(m) >= 2: a, b = float(m[0]), float(m[1]); lat, lon = (a, b) if abs(a) > abs(b) or a > 38 else (b, a)
    if lat is None or not (-25 < lon < 60 and -25 < lat < 52) or (lat == 0 and lon == 0): continue
    pro = ' '.join([str(r.get(cPRO) or ''), str(r.get(cDPRO) or '')]).lower()
    prot = 'classé' if 'class' in pro else 'inscrit' if 'inscr' in pro else ''
    rows.append({'ref': ref, 'nom': str(r.get(cNOM) or '').strip()[:200], 'commune': str(r.get(cCOM) or '').strip()[:80], 'insee': str(r.get(cINS) or '').strip()[:5], 'protection': prot, 'lon': round(lon, 6), 'lat': round(lat, 6)})
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
