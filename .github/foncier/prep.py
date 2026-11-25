# Données nationales communes à tous les départements : postes électriques (OSM), friches (Cartofriches), noms des communes
import requests, json, time, sys
H = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
def log(*a): print(*a, flush=True)
q = '[out:json][timeout:600];area["ISO3166-1"="FR"][admin_level=2]->.a;(node["power"="substation"](area.a);way["power"="substation"](area.a););out center tags;'
postes = []
for t in range(3):
    for u in ['https://overpass-api.de/api/interpreter', 'https://overpass.private.coffee/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']:
        try:
            el = requests.post(u, data={'data': q}, headers=H, timeout=700).json()['elements']
            for e in el:
                c = e.get('center') or e; tg = e.get('tags', {})
                sub = tg.get('substation') or ''; v = tg.get('voltage') or ''
                if sub in ('minor_distribution', 'industrial', 'traction', 'converter') : continue
                if not (v or sub in ('transmission', 'distribution')): continue
                postes.append([round(c['lat'], 5), round(c['lon'], 5), (tg.get('name') or tg.get('ref') or 'Poste électrique')[:60], v[:30], tg.get('operator', '')[:30]])
            if postes: break
        except Exception as ex: log('overpass', u, str(ex)[:150])
    if postes: break
    time.sleep(60)
log('postes retenus', len(postes))
if not postes: sys.exit('aucun poste')
json.dump(postes, open('/tmp/commun/postes.json', 'w'))
for t in range(5):
    try:
        r = requests.get('https://static.data.gouv.fr/resources/sites-references-dans-cartofriches/20261007-122232/friches-standard.csv', headers=H, timeout=600); r.raise_for_status()
        open('/tmp/commun/friches.csv', 'wb').write(r.content); log('friches', len(r.content)); break
    except Exception as ex: log('friches', ex); time.sleep(30)
com = {}
for t in range(6):
    try:
        for c in requests.get('https://geo.api.gouv.fr/communes?fields=nom,code,codeDepartement,centre&format=json', headers=H, timeout=300).json():
            com[c['code']] = [c['nom'], c.get('codeDepartement'), (c.get('centre') or {}).get('coordinates')]
        break
    except Exception as ex: log('communes', str(ex)[:150]); time.sleep(30)
for t in range(6):
    try:
        for c in requests.get('https://geo.api.gouv.fr/communes?type=arrondissement-municipal&fields=nom,code,codeDepartement,centre&format=json', headers=H, timeout=300).json():
            com[c['code']] = [c['nom'], c.get('codeDepartement'), (c.get('centre') or {}).get('coordinates')]
        break
    except Exception as ex: log('arrondissements', str(ex)[:150]); time.sleep(30)
log('communes', len(com))
if len(com) < 30000: sys.exit('communes incomplètes')
json.dump(com, open('/tmp/commun/communes.json', 'w'), ensure_ascii=False)
# Établissements en activité géolocalisés (Sirene, INSEE) : un bâtiment occupé par une entreprise n'est pas disponible
import subprocess
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'duckdb'], check=True)
import duckdb
GEO = 'https://static.data.gouv.fr/resources/geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques/20261123-064215/geoloc-geolocalisationetablissement-sirene-pour-etudes-statistiques-parquet.parquet'
STK = 'https://static.data.gouv.fr/resources/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/20261103-101714/stock-stocketablissement-parquet.parquet'
for t in range(3):
    try:
        c = duckdb.connect(); c.execute("INSTALL httpfs; LOAD httpfs; SET threads=4; SET memory_limit='5GB';")
        c.execute(f"""COPY (
          SELECT s.siren, g.y_latitude AS lat, g.x_longitude AS lon, coalesce(g.distance_precision, 0) AS prec,
                 nullif(trim(coalesce(s.enseigne1Etablissement, s.denominationUsuelleEtablissement, '')), '') AS nom,
                 s.activitePrincipaleEtablissement AS ape,
                 CASE WHEN g.plg_code_commune LIKE '97%' THEN substr(g.plg_code_commune, 1, 3) ELSE substr(g.plg_code_commune, 1, 2) END AS dep
          FROM read_parquet('{STK}') s JOIN read_parquet('{GEO}') g USING (siret)
          WHERE s.etatAdministratifEtablissement = 'A' AND g.y_latitude IS NOT NULL AND g.plg_code_commune IS NOT NULL
        ) TO '/tmp/commun/sirene' (FORMAT parquet, PARTITION_BY (dep), OVERWRITE_OR_IGNORE)""")
        log('sirene actifs', c.execute("SELECT count(*) FROM read_parquet('/tmp/commun/sirene/*/*.parquet')").fetchone()[0]); break
    except Exception as ex: log('sirene', str(ex)[:300]); time.sleep(60)
else: sys.exit('sirene indisponible')
