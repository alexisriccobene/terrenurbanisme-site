"""Teste des sources officielles pour les services à proximité (Sirene, annuaire de l'Éducation, gares SNCF)."""
import requests, json, time
S = requests.Session(); S.headers['User-Agent'] = 'TerrenUrbanisme'
for nom, lat, lon in [('Montpellier', 43.6297, 3.8467), ('Corte', 42.3065, 9.1503), ('Sotta', 41.5422, 9.1795)]:
    print('\n#####', nom)
    for naf in ['47.73Z', '10.71C', '47.11D,47.11F', '86.21Z']:
        t = time.time()
        try:
            r = S.get('https://recherche-entreprises.api.gouv.fr/near_point', params={'lat': lat, 'long': lon, 'radius': 3, 'activite_principale': naf, 'per_page': 5, 'etat_administratif': 'A'}, timeout=20)
            j = r.json(); res = j.get('results', [])
            print('SIRENE', naf, r.status_code, round(time.time() - t, 1), 's', j.get('total_results'), [(x.get('nom_complet'), [(m.get('enseigne_1') or m.get('nom_commercial'), m.get('latitude'), m.get('longitude'), m.get('etat_administratif')) for m in (x.get('matching_etablissements') or [])][:2]) for x in res[:3]])
        except Exception as e: print('SIRENE err', naf, e)
    t = time.time()
    try:
        u = 'https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/records'
        r = S.get(u, params={'where': "within_distance(position, geom'POINT(%f %f)', 3km)" % (lon, lat), 'order_by': "distance(position, geom'POINT(%f %f)')" % (lon, lat), 'limit': 5, 'select': 'nom_etablissement,type_etablissement,ecole_maternelle,ecole_elementaire,position,statut_public_prive'}, timeout=20)
        print('EDUC', r.status_code, round(time.time() - t, 1), 's', r.text[:700])
    except Exception as e: print('EDUC err', e)
    t = time.time()
    try:
        u = 'https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/gares-de-voyageurs/records'
        r = S.get(u, params={'where': "within_distance(position_geographique, geom'POINT(%f %f)', 15km)" % (lon, lat), 'order_by': "distance(position_geographique, geom'POINT(%f %f)')" % (lon, lat), 'limit': 2}, timeout=20)
        print('SNCF', r.status_code, round(time.time() - t, 1), 's', r.text[:500])
    except Exception as e: print('SNCF err', e)
