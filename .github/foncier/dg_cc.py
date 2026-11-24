"""Recherche des secteurs de cartes communales de Corse (standard CNIG) sur data.gouv et geo-ide."""
import requests, json
H = {'User-Agent': 'Mozilla/5.0 (TerrenUrbanisme; contact@terrenurbanisme.com)'}
seen = set()
for q in ('n secteur cc 02b', 'n secteur cc 02a', 'n_secteur_cc_02b', 'n_secteur_cc_02a', 'secteur cc 2b', 'secteur cc 2a', 'carte communale haute-corse', 'carte communale corse-du-sud', 'carte communale corse', 'zonage carte communale corse', 'n zonage plu 02b', 'documents urbanisme haute-corse', 'documents d urbanisme corse-du-sud', 'n document urbanisme 02b'):
    for k in range(3):
        try:
            j = requests.get('https://www.data.gouv.fr/api/1/datasets/', params={'q': q, 'page_size': 30}, headers=H, timeout=60).json(); break
        except Exception as e: print('err', q, e); j = {}
    for d in j.get('data', []):
        if d['id'] in seen: continue
        seen.add(d['id']); org = (d.get('organization') or {}).get('name', '')
        t = d['title']
        if any(x in (t + org).lower() for x in ('corse', '02b', '02a', '2b', '2a')):
            print('Q', q, '|', t, '|', org, '|', d['page'])
            for r in d.get('resources', [])[:4]: print('     ', r.get('format'), r.get('url'))
# catalogue geo-ide (CSW / recherche)
for q in ('carte communale Haute-Corse', 'carte communale Corse-du-Sud', 'secteur carte communale 2B', 'secteur carte communale 2A'):
    try:
        r = requests.get('https://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/q', params={'any': q, '_content_type': 'json', 'fast': 'index', 'from': 1, 'to': 40}, headers=H, timeout=60)
        print('GEOIDE', q, r.status_code, r.text[:3000])
    except Exception as e: print('geoide', q, e)
