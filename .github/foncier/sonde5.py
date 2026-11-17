import requests, json
H={'User-Agent':'TerrenUrbanisme/1.0'}
r=requests.get('https://apicarto.ign.fr/api/gpu/municipality',params={'insee':'2B251'},headers=H,timeout=60).json()
for f in r['features']: print('MUNI', json.dumps(f['properties'],ensure_ascii=False))
for t in ['document','procedure']:
    try:
        r=requests.get('https://www.geoportail-urbanisme.gouv.fr/api/document',params={'grid':'2B251'},headers=H,timeout=60); print('API',r.status_code,r.text[:1500]); break
    except Exception as e: print(e)
r=requests.get('https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=wfs_du:doc_urba&outputFormat=application/json&count=5&CQL_FILTER='+requests.utils.quote("partition LIKE '%2B251%' OR idurba LIKE '%2B251%'"),headers=H,timeout=60); print('DOCURBA', r.status_code, r.text[:1500])
