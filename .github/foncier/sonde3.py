import requests, json, time
H={'User-Agent':'TerrenUrbanisme/1.0'}
r=requests.get('https://data.economie.gouv.fr/api/v2/catalog/datasets/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/attachments',headers=H,timeout=60).json()
for a in r.get('attachments',[]): print('PJ', a.get('metas',{}).get('id') or a.get('id'), json.dumps(a)[:300])
t=time.time()
w='numerodepartement="75" and familleavis="radiation" and dateparution>="2025-01-01" and dateparution<="2025-12-31"'
u='https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/exports/json?select=registre,dateparution&where='+requests.utils.quote(w)
x=requests.get(u,headers=H,timeout=600); j=x.json(); print('export bodacc 75 2025 radiations', len(j), round(time.time()-t), 's', j[:2])
q='[out:json][timeout:300];area["ISO3166-1"="FR"][admin_level=2]->.a;(node["power"="substation"](area.a);way["power"="substation"](area.a););out center tags;'
for u in ['https://overpass.kumi.systems/api/interpreter','https://overpass-api.de/api/interpreter','https://overpass.private.coffee/api/interpreter']:
    try:
        t=time.time(); e=requests.post(u,data={'data':q},headers=H,timeout=400).json()['elements']; print('overpass FR',u,len(e),round(time.time()-t),'s'); 
        if e: break
    except Exception as ex: print('overpass err',u,str(ex)[:150])
