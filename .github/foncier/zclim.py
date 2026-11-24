"""Télécharge l'annexe I (zones climatiques) de l'arrêté du 26 octobre 2010 publiée par AIDA (INERIS)."""
import requests, re
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0'
t = S.get('https://aida.ineris.fr/node/27781', timeout=90).text
imgs = sorted(set(re.findall(r'(?:src|href)="([^"]*a261010_0\d[^"]*)"', t)))
print(imgs)
for i, u in enumerate(imgs):
    if u.startswith('/'): u = 'https://aida.ineris.fr' + u
    r = S.get(u, timeout=90); n = '/tmp/out/' + u.split('/')[-1].split('?')[0]; open(n, 'wb').write(r.content); print(n, r.status_code, len(r.content))
