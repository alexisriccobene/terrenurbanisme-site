"""Cherche d'autres sources du plan de zonage complet de Corte (2B096) : archives web, mairie, data.gouv, GPU."""
import requests, re, os, json
os.makedirs('/tmp/out', exist_ok=True)
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0'
def get(u, **k):
    try: return S.get(u, timeout=90, **k)
    except Exception as e: print('ERR', u[:90], str(e)[:80]); return None
# 1. archives web
for q in ['mairie-corte.fr/modules.php*', 'www.mairie-corte.fr/modules.php*', 'ville-corte.fr/*', 'www.ville-corte.fr/*']:
    r = get('http://web.archive.org/cdx/search/cdx', params={'url': q, 'output': 'json', 'collapse': 'urlkey', 'limit': 5000})
    if r is not None and r.ok:
        try: rows = r.json()[1:]
        except Exception: rows = []
        print('ARCHIVE', q, len(rows))
        for x in rows:
            o = x[2]
            if re.search(r'(?i)download|pdf|plu|zonage|urbanism|plan', o): print('  A', x[1], x[4], x[3][:25], o[:160])
# 2. mairie : plage large de lid
for lid in list(range(1000, 1440)) + list(range(1520, 1800)):
    r = get('https://www.mairie-corte.fr/modules.php?name=Downloads&d_op=getit&lid=%d' % lid, stream=True)
    if r is None: continue
    cd = r.headers.get('content-disposition', ''); ct = r.headers.get('content-type', '')
    if 'html' not in ct: print('LID', lid, r.status_code, ct[:25], r.headers.get('content-length', '?'), cd[:120], r.url[-80:])
    r.close()
# 3. data.gouv
for q in ['Corte PLU', 'Corte urbanisme', 'plan local urbanisme Haute-Corse', 'PLU Corse zonage']:
    r = get('https://www.data.gouv.fr/api/1/datasets/', params={'q': q, 'page_size': 30})
    if r is not None and r.ok:
        for d in r.json().get('data', []): print('DG', q, '|', d['title'][:100], '|', (d.get('organization') or {}).get('name', '')[:40], '|', d['page'])
# 4. GPU
for u in ['https://www.geoportail-urbanisme.gouv.fr/api/document?grid=2B096', 'https://apicarto.ign.fr/api/gpu/municipality?insee=2B096',
          'https://www.geoportail-urbanisme.gouv.fr/api/document?documentFamily=PLU&grid=2B096&status=document.production']:
    r = get(u)
    if r is not None: print('GPU', u[-70:], r.status_code, r.text[:600])
