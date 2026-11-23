"""Vérifie les couches de fond de carte IGN (Géoplateforme) utilisables sur la carte du site."""
import requests
H = {'User-Agent': 'Mozilla/5.0'}
base = 'https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={l}&STYLE={s}&TILEMATRIXSET=PM&TILEMATRIX=14&TILEROW=5636&TILECOL=8299&FORMAT={f}'
for l, s, f in [('GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2', 'normal', 'image/png'), ('GEOGRAPHICALNAMES.NAMES', 'normal', 'image/png'), ('GEOGRAPHICALNAMES.NAMES', 'PCI vecteur', 'image/png'),
                ('TRANSPORTNETWORKS.ROADS', 'normal', 'image/png'), ('HYDROGRAPHY.HYDROGRAPHY', 'normal', 'image/png'), ('ADMINEXPRESS-COG.LATEST', 'normal', 'image/png'), ('LIMITES_ADMINISTRATIVES_EXPRESS.LATEST', 'normal', 'image/png'),
                ('CADASTRALPARCELS.PARCELLAIRE_EXPRESS', 'PCI vecteur', 'image/png'), ('ORTHOIMAGERY.ORTHOPHOTOS', 'normal', 'image/jpeg')]:
    r = requests.get(base.format(l=l, s=s.replace(' ', '%20'), f=f), headers=H, timeout=30)
    print(l, s, r.status_code, r.headers.get('content-type'), len(r.content), r.text[:150] if 'xml' in (r.headers.get('content-type') or '') else '')
r = requests.get('https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities', headers=H, timeout=60).text
import re
for idn in re.findall(r'<ows:Identifier>([A-Z][A-Z0-9_.\-]*(?:NAMES|NOMS|TOPONYM|LABEL|ROAD|HYDRO|PLAN)[A-Z0-9_.\-]*)</ows:Identifier>', r): print('CAP', idn)
