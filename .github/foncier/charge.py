# Chargement de la base « foncier entreprises » pour la Corse (2A, 2B) dans Supabase (table fon_sites)
import requests, json, os, re, io, csv, gzip, zipfile, time, math, sys
import ijson
from shapely.geometry import shape, Point, mapping
from shapely.strtree import STRtree
from shapely.ops import transform
from pyproj import Geod
H = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
GEOD = Geod(ellps='WGS84')
BBOX = (41.33, 8.53, 43.03, 9.57)  # lat_min, lon_min, lat_max, lon_max
DEPS = ['2A', '2B']
SURF_MIN = 1000      # m² minimum pour un terrain en zone constructible
BATI_MIN = 150       # m² minimum d'emprise pour un bâtiment d'activité
t0 = time.time()
def log(*a): print(f'[{int(time.time()-t0)}s]', *a, flush=True)
def get(u, **k):
    for i in range(5):
        try:
            r = requests.get(u, headers=H, timeout=k.get('timeout', 120)); r.raise_for_status(); return r
        except Exception as e:
            log('  nouvel essai', i, str(e)[:150]); time.sleep(5 * (i + 1))
    raise RuntimeError('échec ' + u)
def area_m2(g):
    try: return abs(GEOD.geometry_area_perimeter(g)[0])
    except Exception: return 0
def hav(a, b, c, d):
    p = math.pi / 180; x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))

# 1. Zones des PLU (U et AU) — Géoportail de l'urbanisme
WFS = 'https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json'
zones, zinfo = [], []
start = 0
while True:
    u = f"{WFS}&typeNames=wfs_du:zone_urba&count=1000&startIndex={start}&bbox={BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]},urn:ogc:def:crs:EPSG::4326"
    fc = get(u, timeout=180).json(); fs = fc.get('features', [])
    for f in fs:
        p = f['properties']; tz = (p.get('typezone') or '').upper()
        if not (tz.startswith('U') or tz.startswith('AU')): continue
        try: g = shape(f['geometry']).buffer(0)
        except Exception: continue
        lib = (p.get('libelle') or '').strip(); ll = (p.get('libelong') or '')
        act = bool(re.match(r'^\d*\s*(AU|U)\s*[-_]?\s*[XEIYZ]', lib.upper())) or bool(re.search(r'activit|industri|artisan|[ée]conomi|commerc|logisti', ll, re.I))
        zones.append(g); zinfo.append({'lib': lib, 'tz': tz, 'act': act, 'du': p.get('partition'), 'long': ll[:160]})
    if start == 0 and fs: log('exemple zone', json.dumps(fs[0]['properties'], ensure_ascii=False)[:400])
    log('zones lues', start + len(fs), 'U/AU retenues', len(zones))
    if len(fs) < 1000: break
    start += 1000
ztree = STRtree(zones)
def zone_of(pt):
    for i in ztree.query(pt):
        if zones[i].contains(pt): return zinfo[i]
    return None

# 2. Bâtiments d'activité (BD TOPO IGN)
cql = "usage_1 IN ('Industriel','Agricole','Commercial et services') OR nature='Industriel, agricole ou commercial'"
bats = []
start = 0
while True:
    u = f"{WFS}&typeNames=BDTOPO_V3:batiment&count=5000&startIndex={start}&CQL_FILTER=" + requests.utils.quote(f"({cql}) AND BBOX(geometrie,{BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]},'urn:ogc:def:crs:EPSG::4326')")
    fs = get(u, timeout=240).json().get('features', [])
    for f in fs:
        if (f['properties'].get('etat_de_l_objet') or '') not in ('En service', ''): continue
        try: g = shape(f['geometry'])
        except Exception: continue
        g2 = transform(lambda x, y, z=None: (x, y), g)
        a = area_m2(g2)
        if a < BATI_MIN: continue
        c = g2.centroid
        bats.append({'pt': c, 'a': a, 'u': f['properties'].get('usage_1'), 'n': f['properties'].get('nature'), 'h': f['properties'].get('hauteur')})
    log('bâtiments lus', start + len(fs), 'retenus', len(bats))
    if len(fs) < 5000: break
    start += 5000
btree = STRtree([b['pt'] for b in bats])

# 3. Parcelles des personnes morales (DGFiP, situation 2026)
pm = {}
z = zipfile.ZipFile(io.BytesIO(get('https://data.economie.gouv.fr/api/v2/catalog/datasets/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/attachments/fichiers_des_parcelles_dpts_1_a_30_situation_2026zip', timeout=600).content))
for i in z.infolist():
    m = re.search(r'PM_\d+_NB_(2A|2B)0\.csv$', i.filename)
    if not m: continue
    with z.open(i) as f:
        rd = csv.reader(io.TextIOWrapper(f, encoding='latin-1'), delimiter=';'); next(rd)
        for r in rd:
            try:
                dep, com, pre, sec, num = r[0], r[2], (r[4] or '').strip() or '000', r[5].strip(), r[6].strip()
                idu = dep + com.zfill(3) + pre.zfill(3) + sec.rjust(2, '0') + num.zfill(4)
                siren, grp, forme, den = r[19].strip(), r[20].strip(), r[22].strip(), r[23].strip()
                if idu in pm and pm[idu].get('siren') and not re.fullmatch(r'\d{9}', siren): continue
                pm[idu] = {'siren': siren if re.fullmatch(r'\d{9}', siren) else None, 'grp': grp, 'forme': forme, 'den': den}
            except Exception: pass
log('parcelles de personnes morales', len(pm))
ARMEE = re.compile(r'ARMEE|DEFENSE|MILITAIRE|GENDARMERIE', re.I)

# 4. Parcelles du cadastre : terrains en zone U/AU et parcelles portant un bâtiment d'activité
sites = {}
for dep in DEPS:
    p = f'/tmp/c{dep}.gz'
    with requests.get(f'https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/departements/{dep}/cadastre-{dep}-parcelles.json.gz', headers=H, stream=True, timeout=1200) as r:
        r.raise_for_status()
        with open(p, 'wb') as f:
            for c in r.iter_content(1 << 20): f.write(c)
    n = 0
    with gzip.open(p, 'rb') as f:
        for feat in ijson.items(f, 'features.item', use_float=True):
            n += 1
            pr = feat['properties']; cont = int(pr.get('contenance') or 0)
            if cont < 300: continue
            try: g = shape(feat['geometry'])
            except Exception: continue
            idu = pr['id']; info = pm.get(idu)
            bsum, busages = 0, set()
            for k in btree.query(g):
                if g.contains(bats[k]['pt']): bsum += bats[k]['a']; busages.add(bats[k]['u'] or bats[k]['n'])
            pt = g.representative_point()
            zn = zone_of(pt)
            armee = bool(info and ARMEE.search(info['den'] or ''))
            keep = (bsum >= BATI_MIN) or (zn and cont >= SURF_MIN) or (armee and cont >= SURF_MIN)
            if not keep: continue
            gs = g.simplify(0.00002, preserve_topology=True)
            sites[idu] = {
                'id': idu, 'kind': 'batiment' if bsum >= BATI_MIN else 'terrain', 'dep': dep, 'insee': pr.get('commune'),
                'idu': idu, 'section': pr.get('section'), 'numero': pr.get('numero'), 'surface': cont, 'bati': int(bsum) or None,
                'lat': round(pt.y, 6), 'lon': round(pt.x, 6),
                'zone': zn['lib'] if zn else None, 'typezone': zn['tz'] if zn else None, 'activite': bool(zn and zn['act']),
                'siren': info['siren'] if info else None, 'proprio': (info['den'] if info else None), 'forme': info['forme'] if info else None,
                'infos': {'usages': sorted(u for u in busages if u), 'groupe': info['grp'] if info else None, 'armee': armee or None, 'zone_long': zn['long'] if zn else None},
                'geom': json.loads(json.dumps(mapping(gs), default=float).replace('.0,', ',')) if gs.is_valid else None,
            }
    log(dep, 'parcelles lues', n, 'sites retenus', len(sites))
    os.remove(p)
del pm

# 5. Procédures collectives (BODACC) en Corse depuis 2017
proc = {}
for dep in DEPS:
    for yr in range(2017, 2027):
        off = 0
        while True:
            w = f'numerodepartement="{dep}" and familleavis="collective" and dateparution>="{yr}-01-01" and dateparution<="{yr}-12-31"'
            u = 'https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records?limit=100&offset=' + str(off) + '&order_by=dateparution%20desc&where=' + requests.utils.quote(w)
            res = get(u).json().get('results', [])
            for a in res:
                for s in (a.get('registre') or []):
                    s = s.replace(' ', '')
                    if not re.fullmatch(r'\d{9}', s): continue
                    try: j = json.loads(a.get('jugement') or '{}')
                    except Exception: j = {}
                    d = a.get('dateparution')
                    if s not in proc or d > proc[s]['d']: proc[s] = {'d': d, 'nat': (j.get('nature') or a.get('familleavis_lib'))[:200], 'trib': a.get('tribunal'), 'url': a.get('url_complete')}
            if len(res) < 100 or off >= 9900: break
            off += 100
    log('BODACC', dep, 'entreprises concernées', len(proc))

# 6. État des entreprises propriétaires (annuaire des entreprises)
sirens = sorted({s['siren'] for s in sites.values() if s['siren']})
etat = {}
for i, s in enumerate(sirens):
    try:
        r = requests.get('https://recherche-entreprises.api.gouv.fr/search?q=' + s + '&per_page=1', headers=H, timeout=30)
        if r.status_code == 429: time.sleep(2); r = requests.get('https://recherche-entreprises.api.gouv.fr/search?q=' + s + '&per_page=1', headers=H, timeout=30)
        res = r.json().get('results', [])
        if res and res[0].get('siren') == s:
            e = res[0]; etat[s] = {'etat': e.get('etat_administratif'), 'nom': e.get('nom_complet'), 'naf': e.get('activite_principale'), 'fermeture': e.get('date_fermeture')}
    except Exception: pass
    time.sleep(0.16)
    if i % 500 == 0: log('annuaire', i, '/', len(sirens))
for s in sites.values():
    if s['siren']:
        e = etat.get(s['siren']); pc = proc.get(s['siren'])
        if e: s['etat'] = e['etat']; s['infos']['naf'] = e['naf']; s['infos']['fermeture'] = e['fermeture']; s['proprio'] = e['nom'] or s['proprio']
        if pc: s['proc_nature'], s['proc_date'], s['proc_tribunal'], s['proc_url'] = pc['nat'], pc['d'], pc['trib'], pc['url']
log('entreprises vérifiées', len(etat), 'en procédure', sum(1 for s in sites.values() if s.get('proc_nature')))

# 7. Friches (Cartofriches)
txt = get('https://static.data.gouv.fr/resources/sites-references-dans-cartofriches/20261007-122232/friches-standard.csv', timeout=300).content.decode('utf-8')
rd = csv.DictReader(io.StringIO(txt), delimiter=';'); hdr = rd.fieldnames; log('colonnes friches', hdr)
nf = 0
for r in rd:
    insee = (r.get('comm_insee') or '')
    if not insee.startswith(('2A', '2B')): continue
    lat = lon = None
    for k in hdr:
        v = r.get(k) or ''
        m = re.search(r'POINT\s*\(\s*([\d.]+)\s+([\d.]+)', v)
        if m: lon, lat = float(m.group(1)), float(m.group(2)); break
    if lat is None:
        for a, b in (('latitude', 'longitude'), ('lat', 'lon'), ('y', 'x')):
            if r.get(a) and r.get(b):
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
    sites[fid] = {'id': fid, 'kind': 'friche', 'dep': insee[:2], 'insee': insee, 'commune': r.get('comm_nom'), 'surface': surf, 'bati': bs,
                  'lat': round(lat, 6), 'lon': round(lon, 6), 'proprio': r.get('proprio_nom') or None,
                  'infos': {'nom': r.get('site_nom'), 'type': r.get('site_type'), 'statut': r.get('site_statut'), 'activite': r.get('activite_libelle'), 'url': r.get('site_url'), 'pollution': r.get('sol_pollution_existe')}}
    nf += 1
log('friches', nf)

# 8. Postes électriques (OpenStreetMap ; en Corse le réseau est exploité par EDF)
postes = []
q = f'[out:json][timeout:120];(node["power"="substation"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});way["power"="substation"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]}););out center tags;'
for u in ['https://overpass.kumi.systems/api/interpreter', 'https://overpass-api.de/api/interpreter', 'https://overpass.private.coffee/api/interpreter']:
    try:
        el = requests.post(u, data={'data': q}, headers=H, timeout=200).json()['elements']
        for e in el:
            c = e.get('center') or e; t = e.get('tags', {})
            postes.append({'lat': c['lat'], 'lon': c['lon'], 'nom': t.get('name') or t.get('ref') or 'Poste électrique', 'v': t.get('voltage') or '', 'sub': t.get('substation') or ''})
        if postes: break
    except Exception as e: log('overpass', u, str(e)[:120])
src = [p for p in postes if p['sub'] in ('transmission', 'distribution', '') and (p['v'] or p['sub'])] or postes
log('postes électriques', len(postes), 'utilisés', len(src))
for s in sites.values():
    best = None
    for p in src:
        d = hav(s['lat'], s['lon'], p['lat'], p['lon'])
        if best is None or d < best[0]: best = (d, p)
    if best: s['poste_km'], s['poste_nom'], s['poste_tension'] = round(best[0], 2), best[1]['nom'], best[1]['v']

# 9. Noms des communes puis envoi dans Supabase
com = {}
for dep in DEPS:
    for c in get(f'https://geo.api.gouv.fr/departements/{dep}/communes?fields=nom,code').json(): com[c['code']] = c['nom']
for s in sites.values():
    s['commune'] = s.get('commune') or com.get(s.get('insee'))
base = f"https://{os.environ['REF']}.supabase.co/rest/v1/fon_sites"
HS = {'apikey': os.environ['SR'], 'Authorization': 'Bearer ' + os.environ['SR'], 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates,return=minimal'}
requests.delete(base + '?dep=in.(2A,2B)', headers=HS, timeout=120).raise_for_status()
COLS = ['id', 'kind', 'dep', 'insee', 'commune', 'idu', 'section', 'numero', 'surface', 'bati', 'lat', 'lon', 'zone', 'typezone', 'activite', 'siren', 'proprio', 'forme', 'etat', 'proc_nature', 'proc_date', 'proc_tribunal', 'proc_url', 'poste_km', 'poste_nom', 'poste_tension', 'infos', 'geom']
rows = [{k: s.get(k) for k in COLS} for s in sites.values()]
for r in rows:
    if r['activite'] is None: r['activite'] = False
for i in range(0, len(rows), 500):
    rr = requests.post(base, headers=HS, data=json.dumps(rows[i:i + 500], ensure_ascii=False, default=str).encode(), timeout=180)
    if rr.status_code >= 300: log('ERREUR envoi', rr.status_code, rr.text[:300]); sys.exit(1)
log('envoyés', len(rows))
from collections import Counter
log('répartition', Counter(r['kind'] for r in rows), 'zone activité', sum(1 for r in rows if r['activite']), 'sociétés', sum(1 for r in rows if r['siren']), 'armée', sum(1 for s in sites.values() if (s.get('infos') or {}).get('armee')))
