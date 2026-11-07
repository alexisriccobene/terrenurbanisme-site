# Génère data/communes/{dep}.json : prix DVF par commune (Etalab) et classement loi Montagne (ANCT)
import csv, io, json, os, re, sys, urllib.request
from collections import defaultdict
import openpyxl

UA = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
        return r.read()
INSEE = re.compile(r'^(\d{5}|2[AB]\d{3})$')
def dep(c): return c[:3] if c.startswith('97') else c[:2]
out = defaultdict(dict); meta = {}
def note(msg): print('::notice::' + str(msg).replace('\n', ' | ')[:900], flush=True)
import traceback, atexit
def bilan():
    note('bilan ' + json.dumps({k: (v if k != 'montagne' else {r: {x: y for x, y in i.items() if x != 'exemple'} for r, i in v.items()}) for k, v in meta.items()}, ensure_ascii=False))
    for r, i in meta.get('montagne', {}).items():
        if 'exemple' in i: note('exemple ' + r[:8] + ' ' + json.dumps(i['exemple'][:6], ensure_ascii=False))
atexit.register(bilan)

# 1. Prix : statistiques DVF par commune
try:
    raw = get('https://www.data.gouv.fr/api/1/datasets/r/851d342f-9c96-41c1-924a-11a7a7aae8a6')
except Exception as e:
    note('prix téléchargement ' + repr(e)); raise
txt = raw.decode('utf-8-sig', 'replace')
sep = ';' if txt[:2000].count(';') > txt[:2000].count(',') else ','
rd = csv.DictReader(io.StringIO(txt), delimiter=sep)
meta['prix_colonnes'] = rd.fieldnames
n = 0
def num(v):
    try: return round(float(v)) if v not in (None, '', 'NA') else None
    except: return None
for r in rd:
    if (r.get('echelle_geo') or '') != 'commune': continue
    c = (r.get('code_geo') or '').strip()
    if not INSEE.match(c): continue
    p = []
    for t in ('maison', 'appartement', 'local'): p += [num(r.get('med_prix_m2_whole_' + t)), num(r.get('nb_ventes_whole_' + t)), num(r.get('moy_prix_m2_whole_' + t))]
    if any(x for x in p): out[dep(c)].setdefault(c, {})['p'] = p; n += 1
meta['prix_communes'] = n

# 2. Loi Montagne : communes classées (DGALN, au COG le plus récent)
mont = {}
for rid in ['87bc6d48-f1ed-4924-be55-0142660033de', '8d0ae2b1-9b8c-48df-89b9-6334b166e5c5', 'fa1eeb72-6adb-4efd-a1a1-9f1266c78315']:  # COG 2022, 2021, 2020
    try:
        wb = openpyxl.load_workbook(io.BytesIO(get('https://www.data.gouv.fr/api/1/datasets/r/' + rid)), read_only=True, data_only=True)
        info = {'feuilles': wb.sheetnames}
        ws = wb['Perimetre'] if 'Perimetre' in wb.sheetnames else wb.worksheets[0]
        rows = [[('' if v is None else str(v).strip()) for v in row] for row in ws.iter_rows(values_only=True)]
        hi = next(i for i, r in enumerate(rows[:20]) if 'INSEE_COM' in r)
        j = rows[hi].index('INSEE_COM')
        pj = next((k for k, h in enumerate(rows[hi]) if h.lower().startswith('r') and 'glement' in h.lower()), None)
        info.update({'feuille': ws.title, 'colonne': j, 'exemple': rows[:6]})
        info['partiel_exemples'] = sorted({r[pj] for r in rows[hi + 1:] if pj is not None and pj < len(r) and 'parti' in r[pj].lower()})[:5]
        cur = {}
        for r in rows[hi + 1:]:
            v = r[j] if j < len(r) else ''
            if v.isdigit() and len(v) == 4: v = '0' + v
            if INSEE.match(v): cur[v] = 2 if (pj is not None and pj < len(r) and 'parti' in r[pj].lower()) else 1
        info['communes'] = len(cur)
        meta.setdefault('montagne', {})[rid] = info
        if not mont and len(cur) > 3000: mont = cur  # version la plus récente lisible
    except Exception as e:
        meta.setdefault('montagne', {})[rid] = {'erreur': str(e)[:300]}
for c, v in mont.items(): out[dep(c)].setdefault(c, {})['mt'] = v
meta['montagne_communes'] = len(mont)

# 3. Taxe d'aménagement : taux votés par les collectivités (DGFiP, data.economie.gouv.fr)
import datetime
try:
    today = datetime.date.today().isoformat()
    raw = get('https://www.data.gouv.fr/api/1/datasets/r/22f858cc-8a38-4f86-895c-a77d3a4d3c13')
    txt = raw.decode('utf-8-sig', 'replace'); del raw
    rd = csv.DictReader(io.StringIO(txt), delimiter=';')
    meta['ta_colonnes'] = rd.fieldnames
    def fl(v):
        try: return float(str(v).replace(',', '.')) if v not in (None, '') else None
        except: return None
    zones = defaultdict(int); best = {}  # clé -> (date effet, valeur)
    def keep(k, eff, val):
        if k not in best or eff >= best[k][0]: best[k] = (eff, val)
    for r in rd:
        eff = (r.get('DATE EFFET') or '')[:10]; fin = (r.get('DATE FIN') or '')[:10]
        if not eff or eff > today or (fin and fin < today): continue
        z = (r.get('ZONE APPLICATION') or '').strip(); zones[z] += 1
        t = fl(r.get('TAUX'))
        if t is None or t < 0 or t > 20: continue
        dp = (r.get('DEPARTEMENT') or '').strip().upper().zfill(2); co = (r.get('COMMUNE') or '').strip()
        zl = z.lower()
        if zl.startswith('d'):  # part départementale
            keep(('D', dp), eff, t); continue
        if zl.startswith('r'):  # part régionale (Île-de-France)
            keep(('R', dp), eff, t); continue
        if not co: continue
        insee = (dp[:2] if not dp.startswith('97') else dp[:3]) + co.zfill(3 if not dp.startswith('97') else 2)
        if not INSEE.match(insee): continue
        sec = (r.get('SECTION') or '').strip().upper(); par = (r.get('PARCELLE') or '').strip()
        if sec and par:
            keep(('S', insee, sec.lstrip('0') + '-' + par.lstrip('0')), eff, t)
        else:
            keep(('C', insee), eff, t)
            vs = fl(r.get('VALEUR FORFAITAIRE STATIONNEMENT'))
            ab = fl(r.get('Abris de jardin'))
            if vs: keep(('V', insee), eff, vs)
            if ab: keep(('A', insee), eff, ab)
    del txt
    meta['ta_zones'] = dict(zones)
    nc = ns = 0; per = defaultdict(int)
    for k, (eff, v) in best.items():
        if k[0] == 'C': out[dep(k[1])].setdefault(k[1], {}).setdefault('ta', {})['c'] = v; nc += 1
        elif k[0] == 'V': out[dep(k[1])].setdefault(k[1], {}).setdefault('ta', {})['v'] = v
        elif k[0] == 'A': out[dep(k[1])].setdefault(k[1], {}).setdefault('ta', {})['a'] = v
        elif k[0] == 'S':
            if per[k[1]] >= 4000: continue
            per[k[1]] += 1; ns += 1
            out[dep(k[1])].setdefault(k[1], {}).setdefault('ta', {}).setdefault('s', {})[k[2]] = v
        elif k[0] in ('D', 'R'):
            d0 = k[1] if not k[1].startswith('97') else k[1]
            if d0 in ('20',): continue
            out[d0].setdefault('_dep', {})['td' if k[0] == 'D' else 'tr'] = v
    meta['ta_communes'] = nc; meta['ta_parcelles'] = ns
    meta['ta_departements'] = sorted(d for d, o in out.items() if '_dep' in o and 'td' in o['_dep'])
except Exception as e:
    note('taxe aménagement ' + repr(e)[:400])

# 4. Service public d'eau potable de chaque commune (SISPEA, Office français de la biodiversité)
import zipfile
try:
    zraw = None
    for an in range(datetime.date.today().year, 2019, -1):
        try:
            zraw = get(f'http://www.services.eaufrance.fr/documents/serviceMembers/CompositionCommunaleServices_AEP_{an}.zip')
            if zraw[:2] == b'PK': meta['eau_annee'] = an; break
        except Exception: zraw = None
    zf = zipfile.ZipFile(io.BytesIO(zraw)); nm = zf.namelist()[0]; meta['eau_fichier'] = zf.namelist()
    data = zf.read(nm)
    if nm.lower().endswith(('.xlsx', '.xls')):
        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True); ws = wb.worksheets[0]
        rows = [[('' if v is None else str(v).strip()) for v in r] for r in ws.iter_rows(values_only=True)]
    else:
        t = None
        for enc in ('utf-8-sig', 'cp1252', 'latin-1'):
            try: t = data.decode(enc); break
            except Exception: pass
        sp = ';' if t[:3000].count(';') > t[:3000].count(',') else ','
        rows = list(csv.reader(io.StringIO(t), delimiter=sp))
    hi = next(i for i, r in enumerate(rows[:15]) if any(re.search(r'insee', c, re.I) for c in r))
    H = [h.strip() for h in rows[hi]]; meta['eau_colonnes'] = H; meta['eau_exemple'] = rows[hi + 1:hi + 3]
    def col(*pats):
        for p in pats:
            for i, h in enumerate(H):
                if re.search(p, h, re.I): return i
        return None
    ci = col(r'code insee'); cc = col(r"nom de la collectivit. de l.entit"); cm = col(r'type du mode de gestion'); co = col(r"nom de l.op[ée]rateur"); cd = col(r'^distribution$')
    meta['eau_index'] = [ci, cc, cm, co, cd]
    ne = 0
    for r in rows[hi + 1:]:
        if ci is None or ci >= len(r): continue
        c = r[ci].strip().upper()
        if c.endswith('.0'): c = c[:-2]
        if c.isdigit(): c = c.zfill(5)
        if not INSEE.match(c): continue
        g = lambda j: (r[j].strip() if j is not None and j < len(r) and r[j].strip() not in ('-', 'None') else '')
        if cd is not None and g(cd) and g(cd).lower() != 'oui' and 'eau' in out[dep(c)].get(c, {}): continue
        e = {k: v for k, v in (('c', g(cc)), ('m', g(cm)), ('o', g(co))) if v}
        if e and (cd is None or g(cd).lower() == 'oui' or 'eau' not in out[dep(c)].get(c, {})):
            if 'eau' not in out[dep(c)].get(c, {}): ne += 1
            out[dep(c)].setdefault(c, {})['eau'] = e
    meta['eau_communes'] = ne
except Exception as e:
    note('eau potable ' + repr(e)[:400])

if meta['prix_communes'] < 20000 or meta['montagne_communes'] < 3000:
    sys.exit('données incomplètes : fichiers non écrits')
os.makedirs('data/communes', exist_ok=True)
for d, obj in out.items():
    with open(f'data/communes/{d}.json', 'w') as f: json.dump(obj, f, separators=(',', ':'))
with open('data/meta.json', 'w') as f: json.dump(meta, f, ensure_ascii=False, indent=1)
print('ok', meta['prix_communes'], meta['montagne_communes'], len(out))
