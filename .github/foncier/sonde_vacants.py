# Sonde : les bâtiments jugés « sans entreprise en activité » ont-ils réellement des entreprises autour (API Recherche d'entreprises) ?
import requests, json, time
from shapely.geometry import shape
H = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
IDU = ['2B033000BK0295', '2B1200000B3059', '2B033000BM1108', '2B0420000A1348', '2B1200000B2456', '2B033000BK0242', '2B1200000B2601', '2B0420000E0206']
u = 'https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json&srsName=EPSG:4326&typeNames=CADASTRALPARCELS.PARCELLAIRE_EXPRESS:parcelle&CQL_FILTER=' + requests.utils.quote('idu IN (' + ','.join("'" + i + "'" for i in IDU) + ')')
for f in requests.get(u, headers=H, timeout=60).json()['features']:
    g = shape(f['geometry']); c = g.representative_point(); idu = f['properties']['idu']
    time.sleep(0.4)
    j = requests.get(f'https://recherche-entreprises.api.gouv.fr/near_point?lat={c.y}&long={c.x}&radius=0.1&per_page=10', headers=H, timeout=60).json()
    print('==', idu, round(c.y, 5), round(c.x, 5), 'total', j.get('total_results'))
    for r in j.get('results', [])[:10]:
        for e in r.get('matching_etablissements', [])[:2]:
            d = ((e.get('latitude') and float(e['latitude']) - c.y) ** 2 + (float(e.get('longitude') or 0) - c.x) ** 2) ** 0.5 * 111000 if e.get('latitude') else None
            print('  ', r.get('nom_complet', '')[:50], '|', e.get('adresse', '')[:70], '|', e.get('etat_administratif'), '|', round(d) if d else '?', 'm', '| dans:', g.buffer(0.00015).contains(shape({'type': 'Point', 'coordinates': [float(e['longitude']), float(e['latitude'])]})) if e.get('latitude') else '')
