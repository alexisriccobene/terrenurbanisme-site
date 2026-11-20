import requests
H={'User-Agent':'TerrenUrbanisme/1.0'}
for q in ['zonage PLU Haute-Corse','zonage PLU Corse-du-Sud','plan local urbanisme Corse','PLU Corte','PLU Lucciana','documents urbanisme Corse','zone urba corse']:
    r=requests.get('https://www.data.gouv.fr/api/1/datasets/',params={'q':q,'page_size':10},headers=H,timeout=60).json()
    for d in r.get('data',[]): print('DS',q,'|',d['title'],'|',(d.get('organization') or {}).get('name'),'|',d['page'])
# Catalogue géo-IDE (DDT/DREAL)
for q in ['PLU Haute-Corse','zonage PLU 2B','urbanisme Corse']:
    try:
        r=requests.get('https://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/q',params={'any':q,'_content_type':'json','fast':'index','from':1,'to':15},headers=H,timeout=60)
        print('GEOIDE',q,r.status_code,r.text[:1500])
    except Exception as e: print('GEOIDE ERR',e)
