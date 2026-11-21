# Télécharge les sources des PLU non publiés listées dans .github/plu/sources.json (exécuté dans le clone de la branche plu-src)
import json, os, subprocess, hashlib, re, urllib.request, urllib.parse
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
def get(u, timeout=600):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout) as r: return r.status, r.headers.get('Content-Type', ''), r.read()
def wpdm(u):
    # WordPress Download Manager : /download/<slug>/ -> ?wpdmdl=<id>
    m = re.search(r'^(https?://[^/]+)/download/([^/]+)/?', u)
    if not m: return None
    try:
        _, _, b = get(f'{m.group(1)}/wp-json/wp/v2/wpdmpro?slug={m.group(2)}', 60)
        J = json.loads(b)
        if J: return f'{u.rstrip("/")}/?wpdmdl={J[0]["id"]}'
    except Exception as e: print('  wpdm', e)
    return None
S = json.load(open('../.github/plu/sources.json'))
for ins, files in S.items():
    h = hashlib.md5(json.dumps(files, sort_keys=True).encode()).hexdigest()
    if os.path.exists(f'{ins}/.sources') and open(f'{ins}/.sources').read() == h: continue
    subprocess.run(['rm', '-rf', ins]); os.makedirs(ins)
    for kind in ('parcelles', 'batiments'):
        subprocess.run(['curl', '-sSfL', '--retry', '3', '-o', f'{ins}/cadastre-{kind}.json.gz', f'https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/{ins[:2]}/{ins}/cadastre-{ins}-{kind}.json.gz'])
    for n, u in files.items():
        if '/' in n or n.startswith(('.', '_')): continue
        try:
            st, ct, b = get(u)
            if 'html' in ct.lower() and not b.startswith(b'%PDF'):
                u2 = wpdm(u)
                if u2: st, ct, b = get(u2)
            ok = b.startswith(b'%PDF') or b[:2] == b'PK'
            print(ins, n, st, len(b), 'OK' if ok else 'PAS UN PDF ' + ct)
            if ok and len(b) < 95e6: open(f'{ins}/{n}', 'wb').write(b)
        except Exception as e: print(ins, n, 'ERREUR', str(e)[:120])
    open(f'{ins}/.sources', 'w').write(h)
