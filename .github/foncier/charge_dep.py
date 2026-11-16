# Chargement « foncier entreprises » d'un département : grille d'aperçu (fon_grille) + fichier détaillé (Storage foncier/<dep>.json.gz)
import requests, json, os, re, io, csv, gzip, zipfile, time, math, sys
import ijson
from collections import defaultdict, Counter
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from shapely.ops import transform
from pyproj import Geod
DEP = os.environ['DEP'].strip().upper()
H = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
GEOD = Geod(ellps='WGS84')
SURF_MIN, BATI_MIN = 1000, 150
t0 = time.time()
def log(*a): print(f'[{DEP} {int(time.time()-t0)}s]', *a, flush=True)
def get(u, timeout=180, tries=6):
    for i in range(tries):
        try:
            r = requests.get(u, headers=H, timeout=timeout); r.raise_for_status(); return r
        except Exception as e:
            log('  nouvel essai', i, str(e)[:150]); time.sleep(10 * (i + 1))
    raise RuntimeError('échec ' + u[:200])
def area_m2(g):
    try: return abs(GEOD.geometry_area_perimeter(g)[0])
    except Exception: return 0
COM = json.load(open('/tmp/commun/communes.json'))
POSTES = json.load(open('/tmp/commun/postes.json'))

# Emprise du département (centres des communes)
pts = [v[2] for k, v in COM.items() if v[1] == DEP and v[2]]
if not pts: sys.exit('département inconnu ' + DEP)
la = [p[1] for p in pts]; lo = [p[0] for p in pts]
BBOX = (min(la) - 0.12, min(lo) - 0.15, max(la) + 0.12, max(lo) + 0.15)
log('emprise', BBOX, 'communes', len(pts))
WFS = 'https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json'
def wfs_tiles():
    # découpe en tuiles pour éviter les pagination très profondes
    n = 1 if (BBOX[2] - BBOX[0]) * (BBOX[3] - BBOX[1]) < 1.2 else 2
    dy, dx = (BBOX[2] - BBOX[0]) / n, (BBOX[3] - BBOX[1]) / n
    return [(BBOX[0] + i * dy, BBOX[1] + j * dx, BBOX[0] + (i + 1) * dy, BBOX[1] + (j + 1) * dx) for i in range(n) for j in range(n)]

# 1. Zones U / AU des PLU
zones, zinfo, seen = [], [], set()
for bb in wfs_tiles():
    start = 0
    while True:
        u = f"{WFS}&typeNames=wfs_du:zone_urba&count=1000&startIndex={start}&bbox={bb[0]},{bb[1]},{bb[2]},{bb[3]},urn:ogc:def:crs:EPSG::4326"
        fs = get(u).json().get('features', [])
        for f in fs:
            p = f['properties']; tz = (p.get('typezone') or '').upper(); gid = p.get('gid') or f.get('id')
            if gid in seen or not (tz.startswith('U') or tz.startswith('AU')): continue
            seen.add(gid)
            try: g = shape(f['geometry']).buffer(0)
            except Exception: continue
            lib = (p.get('libelle') or '').strip(); ll = (p.get('libelong') or '')
            act = bool(re.match(r'^\d*\s*(AU|U)\s*[-_]?\s*[XEIYZ]', lib.upper())) or bool(re.search(r'activit|industri|artisan|[ée]conomi|commerc|logisti', ll, re.I))
            zones.append(g); zinfo.append({'lib': lib, 'tz': tz, 'act': act, 'long': ll[:160]})
        if len(fs) < 1000: break
        start += 1000
log('zones U/AU', len(zones))
ztree = STRtree(zones) if zones else None
def zone_of(pt):
    if ztree is None: return None
    for i in ztree.query(pt):
        if zones[i].contains(pt): return zinfo[i]
    return None

# 2. Bâtiments d'activité (BD TOPO)
cql = "usage_1 IN ('Industriel','Agricole','Commercial et services') OR nature='Industriel, agricole ou commercial'"
bats, bseen = [], set()
for bb in wfs_tiles():
    start = 0
    while True:
        u = f"{WFS}&typeNames=BDTOPO_V3:batiment&count=5000&startIndex={start}&propertyName=cleabs,usage_1,nature,etat_de_l_objet,hauteur,geometrie&CQL_FILTER=" + requests.utils.quote(f"({cql}) AND BBOX(geometrie,{bb[0]},{bb[1]},{bb[2]},{bb[3]},'urn:ogc:def:crs:EPSG::4326')")
        fs = get(u, timeout=300).json().get('features', [])
        for f in fs:
            pr = f['properties']
            if pr.get('cleabs') in bseen or (pr.get('etat_de_l_objet') or '') not in ('En service', ''): continue
            bseen.add(pr.get('cleabs'))
            try: g = transform(lambda x, y, z=None: (x, y), shape(f['geometry']))
            except Exception: continue
            a = area_m2(g)
            if a < BATI_MIN: continue
            bats.append({'pt': g.centroid, 'a': a, 'u': pr.get('usage_1') or pr.get('nature')})
        if len(fs) < 5000: break
        start += 5000
    log('bâtiments retenus', len(bats))
btree = STRtree([b['pt'] for b in bats]) if bats else None

# 3. Parcelles des personnes morales (DGFiP 2026)
dn = int(DEP[:2]) if DEP[:2].isdigit() else 20
att = 'fichiers_des_parcelles_dpts_1_a_30_situation_2026zip' if dn <= 30 else 'fichier_des_parcelles_31_a_60_situation_2026zip' if dn <= 60 else 'fichiers_des_parcelles_dpts_61_a_976_situation_2026zip'
zp = '/tmp/pm.zip'
if not os.path.exists(zp):
    with requests.get('https://data.economie.gouv.fr/api/v2/catalog/datasets/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/attachments/' + att, headers=H, stream=True, timeout=1800) as r:
        r.raise_for_status()
        with open(zp, 'wb') as f:
            for c in r.iter_content(1 << 20): f.write(c)
z = zipfile.ZipFile(zp)
pref = DEP if len(DEP) == 2 else DEP[:2]
pm = {}
for i in z.infolist():
    if not re.search(r'PM_\d+_NB_' + pref + r'\d?\.csv$', i.filename, re.I): continue
    with z.open(i) as f:
        rd = csv.reader(io.TextIOWrapper(f, encoding='latin-1'), delimiter=';'); next(rd)
        for r in rd:
            try:
                if len(DEP) == 3 and (r[0] + r[1]) != DEP: continue
                idu = r[0] + r[2].zfill(3) + ((r[4] or '').strip() or '000').zfill(3) + r[5].strip().rjust(2, '0') + r[6].strip().zfill(4)
                if len(DEP) == 3: idu = DEP + r[2].zfill(3)[-2:] + idu[5:]
                siren = r[19].strip(); sv = siren if re.fullmatch(r'\d{9}', siren) else None
                if idu in pm and pm[idu]['siren'] and not sv: continue
                pm[idu] = {'siren': sv, 'grp': r[20].strip(), 'forme': r[22].strip(), 'den': r[23].strip()}
            except Exception: pass
log('parcelles de personnes morales', len(pm))
ARMEE = re.compile(r'ARMEE|DEFENSE|MILITAIRE|GENDARMERIE', re.I)

# 4. Cadastre
sites = {}
cp = '/tmp/cad.gz'
for t in range(4):
    try:
        with requests.get(f'https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/departements/{DEP}/cadastre-{DEP}-parcelles.json.gz', headers=H, stream=True, timeout=1800) as r:
            r.raise_for_status()
            with open(cp, 'wb') as f:
                for c in r.iter_content(1 << 20): f.write(c)
        break
    except Exception as e: log('cadastre', e); time.sleep(60)
n = 0
with gzip.open(cp, 'rb') as f:
    for feat in ijson.items(f, 'features.item', use_float=True):
        n += 1
        pr = feat['properties']; cont = int(pr.get('contenance') or 0)
        if cont < 300: continue
        try: g = shape(feat['geometry'])
        except Exception: continue
        idu = pr['id']; info = pm.get(idu)
        bsum, us = 0, set()
        if btree is not None:
            for k in btree.query(g):
                if g.contains(bats[k]['pt']): bsum += bats[k]['a']; us.add(bats[k]['u'])
        pt = g.representative_point(); zn = zone_of(pt)
        armee = bool(info and ARMEE.search(info['den'] or ''))
        if not ((bsum >= BATI_MIN) or (zn and cont >= SURF_MIN) or (armee and cont >= SURF_MIN)): continue
        sites[idu] = {'id': idu, 'kind': 'batiment' if bsum >= BATI_MIN else 'terrain', 'insee': pr.get('commune'), 'section': pr.get('section'), 'numero': pr.get('numero'),
                      'surface': cont, 'bati': int(bsum) or None, 'lat': round(pt.y, 6), 'lon': round(pt.x, 6),
                      'zone': zn['lib'] if zn else None, 'typezone': zn['tz'] if zn else None, 'zone_long': zn['long'] if zn else None, 'activite': bool(zn and zn['act']),
                      'siren': info['siren'] if info else None, 'proprio': info['den'] if info else None, 'forme': info['forme'] if info else None, 'groupe': info['grp'] if info else None,
                      'usages': sorted(u for u in us if u) or None, 'armee': armee or None}
os.remove(cp); del pm
log('parcelles lues', n, 'sites', len(sites))

# 5. BODACC : procédures collectives et radiations depuis 2017 (export complet)
def bodacc(fam, sel):
    out = []
    for yr in range(2017, 2027):
        w = f'numerodepartement="{DEP}" and familleavis="{fam}" and dateparution>="{yr}-01-01" and dateparution<="{yr}-12-31"'
        u = 'https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/exports/json?select=' + sel + '&where=' + requests.utils.quote(w)
        try: out += get(u, timeout=900).json()
        except Exception as e: log('bodacc', fam, yr, str(e)[:100])
    return out
proc = {}
for a in bodacc('collective', 'registre,dateparution,jugement,tribunal,url_complete'):
    for s in (a.get('registre') or []):
        s = s.replace(' ', '')
        if not re.fullmatch(r'\d{9}', s): continue
        d = a.get('dateparution') or ''
        if s in proc and proc[s]['d'] >= d: continue
        try: j = json.loads(a.get('jugement') or '{}')
        except Exception: j = {}
        proc[s] = {'d': d, 'nat': (j.get('nature') or 'Procédure collective')[:200], 'trib': a.get('tribunal'), 'url': a.get('url_complete')}
rad = {}
for a in bodacc('radiation', 'registre,dateparution'):
    for s in (a.get('registre') or []):
        s = s.replace(' ', '')
        if re.fullmatch(r'\d{9}', s): rad[s] = max(rad.get(s, ''), a.get('dateparution') or '')
for s in sites.values():
    if s['siren']:
        if s['siren'] in rad: s['etat'] = 'C'; s['fermeture'] = rad[s['siren']]
        pc = proc.get(s['siren'])
        if pc: s['proc_nature'], s['proc_date'], s['proc_tribunal'], s['proc_url'] = pc['nat'], pc['d'], pc['trib'], pc['url']
log('BODACC procédures', len(proc), 'radiations', len(rad), 'sites concernés', sum(1 for s in sites.values() if s.get('proc_nature') or s.get('etat')))

# 6. Friches
nf = 0
rd = csv.DictReader(io.StringIO(open('/tmp/commun/friches.csv', encoding='utf-8').read()), delimiter=';'); hdr = rd.fieldnames
for r in rd:
    insee = r.get('comm_insee') or ''
    if COM.get(insee, [None, None])[1] != DEP and not (len(DEP) == 2 and insee.startswith(DEP) and insee not in COM): continue
    lat = lon = None
    for k in hdr:
        m = re.search(r'POINT\s*\(\s*(-?[\d.]+)\s+(-?[\d.]+)', r.get(k) or '')
        if m: lon, lat = float(m.group(1)), float(m.group(2)); break
    if lat is None:
        for a, b in (('latitude', 'longitude'), ('lat', 'lon'), ('y', 'x')):
            try: lat, lon = float(r[a]), float(r[b]); break
            except Exception: pass
    if lat is None: continue
    surf = None
    for k in ('unite_fonciere_surface', 'site_surface', 'surface'):
        try: surf = int(float(r.get(k))); break
        except Exception: pass
    try: bs = int(float(r.get('bati_surface')))
    except Exception: bs = None
    fid = 'friche-' + r[hdr[0]]
    sites[fid] = {'id': fid, 'kind': 'friche', 'insee': insee, 'surface': surf, 'bati': bs, 'lat': round(lat, 6), 'lon': round(lon, 6), 'proprio': r.get('proprio_nom') or None,
                  'nom': r.get('site_nom'), 'type': r.get('site_type'), 'statut': r.get('site_statut'), 'ancienne_activite': r.get('activite_libelle'), 'url': r.get('site_url'), 'pollution': r.get('sol_pollution_existe')}
    nf += 1
log('friches', nf)

# 7. Poste électrique le plus proche
ptree = STRtree([Point(p[1], p[0]) for p in POSTES])
def hav(a, b, c, d):
    p = math.pi / 180; x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))
for s in sites.values():
    k = ptree.nearest(Point(s['lon'], s['lat'])); p = POSTES[int(k)]
    s['poste_km'] = round(hav(s['lat'], s['lon'], p[0], p[1]), 2); s['poste_nom'] = p[2]; s['poste_tension'] = p[3]; s['poste_exploitant'] = p[4]
    s['commune'] = s.get('commune') or COM.get(s['insee'] or '', [None])[0]
    s['dep'] = DEP

# 8. Grille d'aperçu + fichier détaillé
def cls(v, th):
    i = 0
    for j, t in enumerate(th):
        if (v or 0) >= t: i = j
    return i
S_TH, B_TH = [0, 1000, 2000, 5000, 10000, 20000, 50000], [0, 150, 500, 1000, 2000, 5000]
g = defaultdict(lambda: [0] * 7)
for s in sites.values():
    k = (round(round(s['lat'] / 0.02) * 0.02, 2), round(round(s['lon'] / 0.02) * 0.02, 2), cls(s['surface'], S_TH), cls(s['bati'], B_TH))
    c = g[k]; c[0] += 1
    if s['kind'] == 'terrain' and not s.get('bati'): c[1] += 1
    if s.get('activite'): c[2] += 1
    if s.get('bati'): c[3] += 1
    if s.get('siren'): c[4] += 1
    if s.get('proc_nature') or s.get('etat') == 'C': c[5] += 1
    if s['kind'] == 'friche': c[6] += 1
rows = [{'dep': DEP, 'clat': k[0], 'clon': k[1], 'si': k[2], 'bi': k[3], 'n': c[0], 'terr': c[1], 'act': c[2], 'bat': c[3], 'soc': c[4], 'dif': c[5], 'fri': c[6]} for k, c in g.items()]
base = f"https://{os.environ['REF']}.supabase.co"
HS = {'apikey': os.environ['SR'], 'Authorization': 'Bearer ' + os.environ['SR']}
data = gzip.compress(json.dumps([{k: v for k, v in s.items() if v not in (None, False, '')} for s in sites.values()], ensure_ascii=False, separators=(',', ':')).encode())
for t in range(4):
    rr = requests.post(f'{base}/storage/v1/object/foncier/{DEP}.json.gz', headers={**HS, 'Content-Type': 'application/gzip', 'x-upsert': 'true'}, data=data, timeout=600)
    if rr.status_code < 300: break
    log('stockage', rr.status_code, rr.text[:200]); time.sleep(20)
else: sys.exit('stockage impossible')
log('fichier détaillé', round(len(data) / 1e6, 1), 'Mo')
# Tuiles de 0,25° : le rapport ne charge que le secteur recherché
TT = defaultdict(list)
for s in sites.values(): TT[(math.floor(s['lat'] / 0.25), math.floor(s['lon'] / 0.25))].append({k: v for k, v in s.items() if v not in (None, False, '')})
for (ty, tx), l in TT.items():
    tb = gzip.compress(json.dumps(l, ensure_ascii=False, separators=(',', ':')).encode())
    for t in range(4):
        rr = requests.post(f'{base}/storage/v1/object/foncier/t/{DEP}/{ty}_{tx}.json.gz', headers={**HS, 'Content-Type': 'application/gzip', 'x-upsert': 'true'}, data=tb, timeout=300)
        if rr.status_code < 300: break
        time.sleep(10)
log('tuiles', len(TT))
J = {**HS, 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates,return=minimal'}
requests.delete(f'{base}/rest/v1/fon_grille?dep=eq.{DEP}', headers=HS, timeout=300).raise_for_status()
for i in range(0, len(rows), 2000):
    for t in range(4):
        rr = requests.post(f'{base}/rest/v1/fon_grille', headers=J, data=json.dumps(rows[i:i + 2000]), timeout=300)
        if rr.status_code < 300: break
        log('grille', rr.status_code, rr.text[:200]); time.sleep(20)
    else: sys.exit('envoi grille impossible')
st = {'kinds': Counter(s['kind'] for s in sites.values()), 'activite': sum(1 for s in sites.values() if s.get('activite')), 'societes': sum(1 for s in sites.values() if s.get('siren')),
      'difficulte': sum(1 for s in sites.values() if s.get('proc_nature') or s.get('etat') == 'C'), 'armee': sum(1 for s in sites.values() if s.get('armee')), 'zones': len(zones), 'batiments_bdtopo': len(bats), 'duree_s': int(time.time() - t0)}
requests.post(f'{base}/rest/v1/fon_deps', headers=J, data=json.dumps({'dep': DEP, 'nb': len(sites), 'stats': st, 'maj': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}), timeout=60)
log('terminé', len(sites), 'sites', len(rows), 'cellules', st)
