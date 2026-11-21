"""Couverture du Géoportail de l'Urbanisme pour toutes les communes de France.
etat : publie_plu (zonage PLU/PLUi au centre de la commune), publie_cc (carte communale), rnu, non_publie."""
import requests, json, time, csv, sys
from concurrent.futures import ThreadPoolExecutor
H = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
C = 'https://apicarto.ign.fr/api/gpu'
com = requests.get('https://geo.api.gouv.fr/communes?fields=nom,code,population,codeDepartement,centre,codeEpci&format=json', headers=H, timeout=120).json()
print(len(com), 'communes'); sys.stdout.flush()
S = requests.Session(); S.headers.update(H)
def get(u, p):
    for t in range(4):
        try:
            r = S.get(u, params=p, timeout=40)
            if r.status_code == 200: return r.json()
        except Exception: pass
        time.sleep(2 + 3 * t)
    return None
def one(c):
    ins = c['code']; ce = c.get('centre') or {}
    g = json.dumps(ce) if ce else None
    etat = 'inconnu'; typ = ''; date = ''
    if g:
        z = get(C + '/zone-urba', {'geom': g})
        if z and z.get('features'):
            p = z['features'][0]['properties']; etat = 'publie_plu'; typ = p.get('idurba', '') ; date = p.get('datappro', '')
        else:
            cc = get(C + '/secteur-cc', {'geom': g})
            if cc and cc.get('features'): etat = 'publie_cc'; date = cc['features'][0]['properties'].get('datappro', '')
    if etat == 'inconnu':
        m = get(C + '/municipality', {'insee': ins})
        if m is not None:
            f = m.get('features') or []
            etat = 'rnu' if (f and f[0]['properties'].get('is_rnu')) else 'non_publie'
    return [ins, c['nom'], c.get('population') or 0, c.get('codeDepartement', ''), c.get('codeEpci', '') or '', etat, typ, date]
out = []
with ThreadPoolExecutor(16) as ex:
    for i, r in enumerate(ex.map(one, com)):
        out.append(r)
        if i % 2000 == 0: print(i, r); sys.stdout.flush()
csv.writer(open('/tmp/out/couverture-france.csv', 'w', newline='')).writerows([['insee', 'commune', 'population', 'dep', 'epci', 'etat', 'idurba', 'datappro']] + out)
from collections import Counter
print(Counter(r[5] for r in out))
np_ = sorted([r for r in out if r[5] == 'non_publie'], key=lambda r: -int(r[2] or 0))
print('non publiées', len(np_), 'population', sum(int(r[2] or 0) for r in np_))
for r in np_[:60]: print(r)
