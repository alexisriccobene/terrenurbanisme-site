"""Recherche sur data.gouv des jeux de données d'urbanisme publiés par les DDT(M) de Corse (cartes communales, PLU, secteurs)."""
import requests, json, os
H = {'User-Agent': 'Mozilla/5.0 (TerrenUrbanisme; contact@terrenurbanisme.com)'}
os.makedirs('/tmp/out', exist_ok=True); res = []
orgs = set()
for q in ('ddtm haute-corse', 'ddt haute-corse', 'ddtm corse-du-sud', 'ddt corse-du-sud', 'dreal corse', 'collectivite de corse'):
    try:
        for o in requests.get('https://www.data.gouv.fr/api/1/organizations/', params={'q': q, 'page_size': 10}, headers=H, timeout=30).json().get('data', []):
            orgs.add((o['id'], o['name'], o['slug']))
    except Exception as e: print('org', q, e)
print(orgs)
for oid, nom, slug in orgs:
    page = 1
    while True:
        try: j = requests.get(f'https://www.data.gouv.fr/api/1/organizations/{oid}/datasets/', params={'page_size': 100, 'page': page}, headers=H, timeout=60).json()
        except Exception as e: print(nom, e); break
        for d in j.get('data', []):
            t = d['title']
            if any(k in t.lower() for k in ('carte communale', 'cartes communales', 'urbanisme', 'plan local', 'plu', 'secteur', 'pos ')):
                rs = [(r.get('title'), r.get('format'), r.get('url')) for r in d.get('resources', [])]
                print(nom, '|', t, '|', d['page']); [print('    ', r) for r in rs[:6]]
                res.append({'org': nom, 'titre': t, 'page': d['page'], 'ressources': rs})
        if not j.get('next_page'): break
        page += 1
for q in ('carte communale haute-corse', 'carte communale corse-du-sud', 'secteurs constructibles carte communale corse'):
    try:
        for d in requests.get('https://www.data.gouv.fr/api/1/datasets/', params={'q': q, 'page_size': 20}, headers=H, timeout=60).json().get('data', []):
            print('Q', q, '|', d['title'], '|', (d.get('organization') or {}).get('name'), '|', d['page'])
    except Exception as e: print(q, e)
json.dump(res, open('/tmp/out/dg.json', 'w'), ensure_ascii=False, indent=1)
