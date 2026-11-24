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
r = S.get('https://tabular-api.data.gouv.fr/api/resources/cc062fa7-4a80-449c-ab73-d2856b455ec9/data/', params={'commune__exact': '2B096', 'page_size': 3}, timeout=60)
print('COPRO', r.status_code); j = r.json()
for x in j.get('data', [])[:3]: print(json.dumps(x, ensure_ascii=False)[:2500])
print('total', j.get('meta'))
for q in [{'page_size': 2}, {'DEPCOM__exact': '2B096', 'page_size': 3}, {'depcom__exact': '2B096', 'page_size': 3}]:
    tab('f7babc17-55e1-4eea-81bd-cfaaea9b37bd', q)
