"""Pour les communes corses dont le PLU n'est pas publié au Géoportail : trouve le site de la mairie
(annuaire service-public) et recense les PDF de zonage / règlement publiés dessus."""
import requests, csv, re, json, time, sys
from urllib.parse import urljoin, urlparse
H = {'User-Agent': 'Mozilla/5.0 (TerrenUrbanisme; contact@terrenurbanisme.com)'}
rows = [(r['insee'], r['commune'], r['population'], r['etat'], r['dep']) for r in csv.DictReader(open('.github/plu/couverture-france.csv')) if r['etat'] in ('non_publie', 'inconnu')]
import os
if os.environ.get('DEPS') or True:
    _d = json.load(open('.github/plu-demande.json')).get('deps')
    if _d: rows = [r for r in rows if r[0][:2] in _d]
rows.sort(key=lambda r: -int(r[2] or 0))
print(len(rows), 'communes non publiées')
def site(insee):
    u = 'https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/records'
    try:
        j = requests.get(u, params={'where': f'code_insee_commune="{insee}" and pivot like "mairie"', 'limit': 5}, headers=H, timeout=30).json()
        for r in j.get('results', []):
            s = r.get('site_internet')
            if s:
                s = json.loads(s) if isinstance(s, str) else s
                for x in s or []:
                    v = x.get('valeur') if isinstance(x, dict) else x
                    if v: return v
    except Exception as e: print('annuaire', insee, e)
    return ''
KEY = re.compile(r'zonage|plu|urbanisme|reglement|règlement|planche|graphique|document', re.I)
from concurrent.futures import ThreadPoolExecutor
def one(row):
    ins, nom, pop, etat, typ = row
    s = site(ins); pdfs = set(); pages = set()
    if s:
        if not s.startswith('http'): s = 'http://' + s
        todo = [s]; seen = set(); host = urlparse(s).netloc.replace('www.', '')
        while todo and len(seen) < 120:
            u = todo.pop(0)
            if u in seen: continue
            seen.add(u)
            try: r = requests.get(u, headers=H, timeout=20)
            except Exception: continue
            if 'html' not in r.headers.get('content-type', ''): continue
            for m in re.finditer(r'href=["\']([^"\'#]+)', r.text):
                l = urljoin(u, m.group(1)); lo = l.lower()
                if lo.endswith('.pdf'):
                    if KEY.search(lo): pdfs.add(l)
                elif host in urlparse(l).netloc and KEY.search(lo) and l not in seen and len(todo) < 80:
                    todo.insert(0, l); pages.add(l)
                elif host in urlparse(l).netloc and u == s and l not in seen:
                    todo.append(l)
    print(ins, nom, s, len(pdfs)); sys.stdout.flush()
    return ({'insee': ins, 'nom': nom, 'pop': pop, 'site': s, 'pdfs': sorted(pdfs), 'pages': sorted(pages)[:20]})
with ThreadPoolExecutor(16) as ex: out = list(ex.map(one, rows))
json.dump(out, open('/tmp/out/plu_sites.json', 'w'), ensure_ascii=False, indent=1)
