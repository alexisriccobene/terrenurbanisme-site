"""Commerces de proximité (boulangeries, supérettes, supermarchés, pharmacies) depuis la BAse Nationale des Commerces Ouverte (OpenStreetMap, geodatamine.fr)."""
import csv, io, json, os, sys, zipfile, urllib.request
URL = 'https://geodatamine.fr/dump/shop_craft_office_csv.zip'
raw = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'TerrenUrbanisme/1.0'}), timeout=300).read()
z = zipfile.ZipFile(io.BytesIO(raw)); name = [n for n in z.namelist() if n.endswith('.csv')][0]
txt = io.TextIOWrapper(z.open(name), encoding='utf-8')
rd = csv.DictReader(txt)
print('colonnes', rd.fieldnames)
KEEP = {'bakery': 'bakery', 'convenience': 'convenience', 'supermarket': 'supermarket', 'pharmacy': 'pharmacy', 'chemist': None}
def g(r, *ks):
    for k in ks:
        if k in r and r[k]: return r[k].strip()
    return ''
out = []; types = {}
for r in rd:
    t = g(r, 'type', 'shop', 'amenity')
    types[t] = types.get(t, 0) + 1
    if t not in KEEP or not KEEP[t]: continue
    try: lon = float(g(r, 'X', 'lon', 'longitude')); lat = float(g(r, 'Y', 'lat', 'latitude'))
    except ValueError: continue
    nom = g(r, 'name', 'nom') or g(r, 'brand', 'marque')
    if not nom: continue
    out.append({'id': g(r, 'id', 'osm_id') or f'{t}-{lon:.5f}-{lat:.5f}', 'k': t, 'nom': nom[:120], 'marque': g(r, 'brand', 'marque')[:80], 'tel': g(r, 'phone', 'contact:phone', 'telephone')[:40], 'mail': g(r, 'email', 'contact:email')[:120], 'lon': round(lon, 6), 'lat': round(lat, 6)})
print('types principaux', sorted(types.items(), key=lambda x: -x[1])[:25])
print('retenus', len(out))
json.dump(out, open('commerces.json', 'w'), ensure_ascii=False)
