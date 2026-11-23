"""Repère les ressources data.gouv (API tabulaire) pour les modules pros : loyers, copropriétés, équipements."""
import requests, json
S = requests.Session(); S.headers['User-Agent'] = 'TerrenUrbanisme'
def ds(q, n=6):
    r = S.get('https://www.data.gouv.fr/api/1/datasets/', params={'q': q, 'page_size': n}, timeout=60).json()
    for d in r.get('data', []):
        print('\nDS', d['id'], '|', d['title'][:90], '|', (d.get('organization') or {}).get('name', '')[:40], '| maj', (d.get('last_modified') or '')[:10])
        for rs in d.get('resources', [])[:12]:
            print('   R', rs['id'], rs.get('format'), (rs.get('filesize') or 0) // 1000000, 'Mo', '|', rs['title'][:80])
for q in []:
    print('\n=====', q); ds(q)
def tab(rid, q):
    try:
        r = S.get('https://tabular-api.data.gouv.fr/api/resources/%s/data/' % rid, params=q, timeout=60)
        print('TAB', rid, r.status_code, r.text[:900])
    except Exception as e: print('TAB err', e)
import sys
for rid in ['129f764d-b613-44e4-952c-5ff50a8c9b73', '55b34088-0964-415f-9df7-d87dd98a09be']:
    tab(rid, {'page_size': 2})
    for col in ['INSEE_C__exact', 'insee_c__exact', 'INSEE__exact']:
        tab(rid, {col: '2B096'})
for rid in ['cc062fa7-4a80-449c-ab73-d2856b455ec9', '132ed35f-db38-48d9-a31f-3dd7a0942cd9']:
    tab(rid, {'page_size': 1})
for q in ['BPE base permanente équipements', 'équipements géolocalisés insee']:
    print('\n=====', q); ds(q, 8)
