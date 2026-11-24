# Couverture du Géoportail de l'Urbanisme pour les communes corses : document publié, RNU, ou document non publié
import requests, json, time, csv
H={'User-Agent':'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
com=[]
for d in ('2A','2B'): com += requests.get(f'https://geo.api.gouv.fr/departements/{d}/communes?fields=nom,code,population',headers=H,timeout=60).json()
out=[]
for c in com:
    ins=c['code']; rnu=None; docs=[]
    for t in range(3):
        try:
            m=requests.get('https://apicarto.ign.fr/api/gpu/municipality',params={'insee':ins},headers=H,timeout=40).json()
            rnu=(m['features'][0]['properties'].get('is_rnu') if m.get('features') else None); break
        except Exception: time.sleep(3)
    for t in range(3):
        try: docs=requests.get('https://www.geoportail-urbanisme.gouv.fr/api/document',params={'grid':ins},headers=H,timeout=40).json(); break
        except Exception: time.sleep(3)
    pub=[x for x in docs if isinstance(x,dict)]
    typ=';'.join(sorted(set(str(x.get('type') or x.get('duType') or '') for x in pub)))
    etat='publie' if pub else ('rnu' if rnu else 'non_publie')
    out.append([ins,c['nom'],c.get('population') or 0,etat,typ])
    time.sleep(0.15)
csv.writer(open('/tmp/out/couverture-corse.csv','w',newline='')).writerows([['insee','commune','population','etat','type']]+out)
from collections import Counter
print('TOTAL',len(out), Counter(r[3] for r in out))
pop=Counter(); 
for r in out: pop[r[3]]+=r[2]
print('POPULATION',dict(pop))
print('NON_PUBLIE_GROSSES', sorted([(r[2],r[1]) for r in out if r[3]=='non_publie'],reverse=True)[:40])
print('EXEMPLE_DOC', json.dumps(next((x for x in [requests.get('https://www.geoportail-urbanisme.gouv.fr/api/document',params={'grid':'2A247'},headers=H,timeout=40).json()]),None))[:600])
