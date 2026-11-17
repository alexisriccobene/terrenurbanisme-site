import requests, json
H={'User-Agent':'TerrenUrbanisme/1.0'}
p=requests.get('https://apicarto.ign.fr/api/cadastre/parcelle?code_insee=2B251&section=AB&numero=0282',headers=H,timeout=60).json()
f=p['features'][0]; print('parcelle', f['properties'].get('contenance'))
g=json.dumps(f['geometry'])
for t in ['zone-urba','document','secteur-cc']:
    r=requests.get('https://apicarto.ign.fr/api/gpu/'+t,params={'geom':g},headers=H,timeout=60)
    print(t, r.status_code, r.text[:1200])
r=requests.get('https://apicarto.ign.fr/api/gpu/municipality',params={'insee':'2B251'},headers=H,timeout=60); print('municipality', r.text[:800])
