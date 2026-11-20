# Audit national des rapports : pour chaque département, génère des rapports d'aperçu sur des parcelles réelles
# (grande commune + petite commune) et contrôle le texte du PDF (chapitres vides, sources indisponibles, incohérences).
import json, os, random, re, subprocess, sys, time, urllib.parse, urllib.request

KEY = os.environ['KEY']; REF = os.environ.get('REF', 'nmoigruxnhsidrhqtzid')
DEPS = os.environ['DEPS'].split(); N = int(os.environ.get('N', '2'))
OUT = os.environ.get('OUT', 'out'); os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'TerrenUrbanisme-audit/1.0 (contact@terrenurbanisme.com)'}

def get(url, t=40, tries=3):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t) as r: return json.loads(r.read())
        except Exception as e:
            last = e; time.sleep(2 + 3 * a)
    raise last

def communes(dep):
    L = get(f'https://geo.api.gouv.fr/departements/{dep}/communes?fields=code,nom,population,centre')
    L = [c for c in L if c.get('centre') and c.get('population')]
    L.sort(key=lambda c: -c['population'])
    rnd = random.Random('tu-' + dep)
    out = [L[0]]
    petites = [c for c in L if 200 <= c['population'] <= 3000] or L[len(L) // 2:]
    while len(out) < N and petites:
        c = rnd.choice(petites); petites.remove(c)
        if c['code'] != out[0]['code']: out.append(c)
    return out

def parcelle(c):
    lon, lat = c['centre']['coordinates']
    for dx, dy in [(0, 0), (0.0006, 0), (0, 0.0006), (-0.0006, 0), (0, -0.0006), (0.0012, 0.0012), (-0.0012, -0.0012)]:
        g = json.dumps({'type': 'Point', 'coordinates': [lon + dx, lat + dy]})
        try:
            j = get('https://apicarto.ign.fr/api/cadastre/parcelle?geom=' + urllib.parse.quote(g), 40, 2)
        except Exception: continue
        for f in j.get('features', []):
            p = f['properties']
            insee = (p.get('code_dep') or '') + (p.get('code_com') or '')
            if p.get('code_arr') and p['code_arr'] != '000' and insee in ('75056', '69123', '13055'): insee = insee[:2] + p['code_arr']
            if len(insee) == 5 and p.get('section') and p.get('numero'):
                return insee, p['section'].lstrip('0') or '0', str(int(p['numero']))
    return None

PATTERNS = [
    ("source non interrogée", r"n'ont pas pu être interrogées|n'a pas pu être interrog|n'ont pas pu être consult|n'a pas pu être consult"),
    ("non disponible", r"\bnon disponible|\bindisponible"),
    ("non identifié", r"Non identifié"),
    ("valeur technique", r"\bundefined\b|\bNaN\b|\bnull\b|\[object|Infinity"),
    ("erreur", r"\b[Ee]rreur\b(?! ou d.une omission)"),
    ("aucune donnée", r"[Aa]ucune donnée"),
    ("accent", r"\btres faible|\btres fort|\bmodere\b|\bzone a\b"),
    ("règlement non lu", r"règlement (?:n'a pas pu|n'est pas disponible|introuvable)|pas pu être lu"),
]

def audit_pdf(path):
    t = subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True, text=True).stdout
    pages = t.split('\f')
    if pages and not pages[-1].strip(): pages = pages[:-1]
    flags = {}
    for name, rx in PATTERNS:
        hits = []
        for i, pg in enumerate(pages):
            for m in re.finditer(rx, pg):
                a = max(0, m.start() - 90); hits.append({'p': i + 1, 'x': ' '.join(pg[a:m.end() + 90].split())})
        if hits: flags[name] = hits[:6]
    vides = []; annexe = next((i for i, pg in enumerate(pages) if 'Les pages suivantes reproduisent' in pg), len(pages))
    for i, pg in enumerate(pages[:annexe]):
        body = '\n'.join(l for l in pg.splitlines() if not re.search(r'terrenurbanisme\.com|Document d.information|TerrenUrbanisme|^\s*\d+ / \d+\s*$', l))
        if len(re.sub(r'\s+', '', body)) < 120: vides.append(i + 1)
    if vides: flags['page presque vide'] = [{'p': p, 'x': ''} for p in vides]
    syn = ' '.join((pages[2] if len(pages) > 2 else '').split())
    verdict = next((v for v in ['NON CONSTRUCTIBLE', 'CONSTRUCTIBLE SOUS CONDITIONS', 'SOUS CONDITIONS', 'CONSTRUCTIBLE', 'NON CONNU', 'À VÉRIFIER'] if v in syn.upper()), '')
    if not verdict: flags['verdict absent'] = [{'p': 3, 'x': syn[:300]}]
    fib = re.search(r'Fibre et internet(.{0,400})', ' '.join(t.split()))
    fibre = (fib.group(1)[:220] if fib else 'section absente')
    if not fib or re.search(r"pas pu être interrog", fibre): flags['fibre'] = [{'p': 0, 'x': fibre}]
    return {'pages': len(pages), 'verdict': verdict, 'fibre': fibre, 'synthese': syn[:900], 'flags': flags}, t

res = []
for dep in DEPS:
    try: cs = communes(dep)
    except Exception as e:
        res.append({'dep': dep, 'erreur': 'liste des communes : ' + repr(e)[:200]}); continue
    for c in cs:
        r = {'dep': dep, 'commune': c['nom'], 'insee_geo': c['code'], 'pop': c['population']}
        pc = parcelle(c)
        if not pc:
            r['erreur'] = 'aucune parcelle trouvée au centre'; res.append(r); print(json.dumps(r, ensure_ascii=False)); continue
        insee, sec, num = pc; r.update({'insee': insee, 'section': sec, 'numero': num})
        url = f'https://{REF}.supabase.co/functions/v1/stripe-webhook?key={KEY}&insee={insee}&section={sec}&numero={num}'
        t0 = time.time(); pdf = f'{OUT}/{insee}-{sec}-{num}.pdf'
        ok = False
        for essai in range(2):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, data=b'', method='POST', headers=UA), timeout=430) as rr:
                    b = rr.read()
                if b[:4] == b'%PDF':
                    open(pdf, 'wb').write(b); ok = True; break
                r['reponse'] = b[:300].decode('utf-8', 'replace')
            except Exception as e:
                r['reponse'] = repr(e)[:300]
                if '546' in r['reponse']: r['limite_calcul'] = True
            time.sleep(5)
        r['secondes'] = round(time.time() - t0); r['essais'] = essai + 1
        if not ok:
            r['erreur'] = 'pas de PDF'; res.append(r); print(json.dumps(r, ensure_ascii=False)); continue
        a, txt = audit_pdf(pdf); r.update(a)
        open(pdf[:-4] + '.txt', 'w').write(txt)
        os.remove(pdf)
        res.append(r); print(json.dumps({k: r[k] for k in ('dep', 'commune', 'insee', 'section', 'numero', 'pages', 'verdict', 'secondes')}, ensure_ascii=False), '| alertes :', ', '.join(r['flags']) or 'aucune')
json.dump(res, open(f'{OUT}/resultats.json', 'w'), ensure_ascii=False, indent=1)
