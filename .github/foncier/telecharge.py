# Télécharge des fichiers listés dans demande.json (urls) vers tests-rapports/foncier/
import requests, json, os
H={'User-Agent':'Mozilla/5.0 (TerrenUrbanisme)'}
d=json.load(open('.github/foncier/demande.json'))
for nom,u in d['urls'].items():
    try:
        r=requests.get(u,headers=H,timeout=600); r.raise_for_status(); open('/tmp/out/'+nom,'wb').write(r.content); print('OK',nom,len(r.content))
    except Exception as e: print('ERR',nom,e)
