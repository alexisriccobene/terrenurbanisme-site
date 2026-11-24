# Exploration des sources de données (formats, volumes) pour la Corse
import requests, json, os
H = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
def g(n, u, keep=3000):
    try:
        r = requests.get(u, headers=H, timeout=90)
        t = r.text
        print('==', n, r.status_code, len(r.content)); print(t[:keep]); print()
        return r
    except Exception as e: print('==', n, 'ERR', e)
g('pm_dataset', 'https://www.data.gouv.fr/api/1/datasets/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/', 200)
r = requests.get('https://www.data.gouv.fr/api/1/datasets/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/', headers=H, timeout=60).json()
for res in r.get('resources', [])[:60]: print(res.get('title'), res.get('format'), res.get('filesize'), res.get('url'))
r = requests.get('https://www.data.gouv.fr/api/1/datasets/sites-references-dans-cartofriches/', headers=H, timeout=60).json()
for res in r.get('resources', [])[:20]: print('FRICHES', res.get('title'), res.get('format'), res.get('filesize'), res.get('url'))
g('bodacc', 'https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records?limit=2&where=numerodepartement%3D%222B%22%20and%20familleavis%3D%22collective%22&order_by=dateparution%20desc', 6000)
g('bodacc_count', 'https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records?limit=0&where=(numerodepartement%3D%222B%22%20or%20numerodepartement%3D%222A%22)%20and%20familleavis%3D%22collective%22%20and%20dateparution%3E%3D%222021-01-01%22', 500)
g('bdtopo_feat', 'https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=BDTOPO_V3:batiment&count=2&outputFormat=application/json&bbox=42.68,9.42,42.72,9.46,urn:ogc:def:crs:EPSG::4326', 4000)
g('zone_urba', 'https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=wfs_du:zone_urba&count=2&outputFormat=application/json&bbox=42.68,9.42,42.72,9.46,urn:ogc:def:crs:EPSG::4326', 3000)
g('cadastre_2B', 'https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/departements/2B/', 2000)
q = '[out:json][timeout:60];area["ISO3166-2"="FR-20R"]->.a;(node["power"="substation"](area.a);way["power"="substation"](area.a););out center tags;'
r = requests.post('https://overpass-api.de/api/interpreter', data={'data': q}, headers=H, timeout=120)
print('== overpass', r.status_code); 
try:
    el = r.json()['elements']; print(len(el)); print(json.dumps(el[:5], ensure_ascii=False)[:2000])
except Exception as e: print(r.text[:500])
g('rne_api', 'https://recherche-entreprises.api.gouv.fr/search?q=orezza&per_page=1', 3000)
