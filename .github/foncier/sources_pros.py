"""Repère les ressources data.gouv (API tabulaire) pour les modules pros : loyers, copropriétés, équipements."""
import requests, json
S = requests.Session(); S.headers['User-Agent'] = 'TerrenUrbanisme'
def ds(q, n=6):
    r = S.get('https://www.data.gouv.fr/api/1/datasets/', params={'q': q, 'page_size': n}, timeout=60).json()
    for d in r.get('data', []):
        print('\nDS', d['id'], '|', d['title'][:90], '|', (d.get('organization') or {}).get('name', '')[:40], '| maj', (d.get('last_modified') or '')[:10])
        for rs in d.get('resources', [])[:12]:
            print('   R', rs['id'], rs.get('format'), (rs.get('filesize') or 0) // 1000000, 'Mo', '|', rs['title'][:80])
for q in ['carte des loyers indicateurs de loyers d\'annonce commune', 'registre national copropriétés', 'base permanente des équipements géolocalisés', 'zonage climatique RE2020', 'zones de neige vent eurocode']:
    print('\n=====', q); ds(q)
def tab(rid, q):
    try:
        r = S.get('https://tabular-api.data.gouv.fr/api/resources/%s/data/' % rid, params=q, timeout=60)
        print('TAB', rid, r.status_code, r.text[:900])
    except Exception as e: print('TAB err', e)
import sys
