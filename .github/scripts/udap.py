"""Annuaire officiel des UDAP (service de l'architecte des Bâtiments de France) par département, depuis l'Annuaire de l'administration (service-public.gouv.fr)."""
import json, re, unicodedata, urllib.request, urllib.parse, os, sys
B = 'https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/records'
Q = {'where': 'search(nom,"départementale de l\'architecture")', 'select': 'nom,adresse_courriel,telephone,site_internet,formulaire_contact,adresse,url_service_public', 'limit': '100'}
R = []
for off in (0, 100):
    u = B + '?' + urllib.parse.urlencode({**Q, 'offset': str(off)})
    R += json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'TerrenUrbanisme/1.0'}), timeout=60))['results']
R = [r for r in R if r.get('nom', '').startswith('Unité départementale')]
print('UDAP trouvées', len(R))
if len(R) < 90: sys.exit('trop peu de résultats')
D={'01':'Ain','02':'Aisne','03':'Allier','04':'Alpes-de-Haute-Provence','05':'Hautes-Alpes','06':'Alpes-Maritimes','07':'Ardèche','08':'Ardennes','09':'Ariège','10':'Aube','11':'Aude','12':'Aveyron','13':'Bouches-du-Rhône','14':'Calvados','15':'Cantal','16':'Charente','17':'Charente-Maritime','18':'Cher','19':'Corrèze','2A':'Corse-du-Sud','2B':'Haute-Corse','21':"Côte-d'Or",'22':"Côtes-d'Armor",'23':'Creuse','24':'Dordogne','25':'Doubs','26':'Drôme','27':'Eure','28':'Eure-et-Loir','29':'Finistère','30':'Gard','31':'Haute-Garonne','32':'Gers','33':'Gironde','34':'Hérault','35':'Ille-et-Vilaine','36':'Indre','37':'Indre-et-Loire','38':'Isère','39':'Jura','40':'Landes','41':'Loir-et-Cher','42':'Loire','43':'Haute-Loire','44':'Loire-Atlantique','45':'Loiret','46':'Lot','47':'Lot-et-Garonne','48':'Lozère','49':'Maine-et-Loire','50':'Manche','51':'Marne','52':'Haute-Marne','53':'Mayenne','54':'Meurthe-et-Moselle','55':'Meuse','56':'Morbihan','57':'Moselle','58':'Nièvre','59':'Nord','60':'Oise','61':'Orne','62':'Pas-de-Calais','63':'Puy-de-Dôme','64':'Pyrénées-Atlantiques','65':'Hautes-Pyrénées','66':'Pyrénées-Orientales','67':'Bas-Rhin','68':'Haut-Rhin','69':'Rhône','70':'Haute-Saône','71':'Saône-et-Loire','72':'Sarthe','73':'Savoie','74':'Haute-Savoie','75':'Paris','76':'Seine-Maritime','77':'Seine-et-Marne','78':'Yvelines','79':'Deux-Sèvres','80':'Somme','81':'Tarn','82':'Tarn-et-Garonne','83':'Var','84':'Vaucluse','85':'Vendée','86':'Vienne','87':'Haute-Vienne','88':'Vosges','89':'Yonne','90':'Territoire-de-Belfort','91':'Essonne','92':'Hauts-de-Seine','93':'Seine-Saint-Denis','94':'Val-de-Marne','95':"Val-d'Oise",'971':'Guadeloupe','972':'Martinique','973':'Guyane','974':'La Réunion','976':'Mayotte'}
def k(s): return re.sub(r"[^a-z]", "", unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode())
def suffix(r): return r['nom'].split(' - ', 1)[1] if ' - ' in r['nom'] else r['nom']
SPEC = {'69': lambda r: 'Rhône et' in r['nom'], '73': lambda r: suffix(r) == 'Savoie et Haute-Savoie', '74': lambda r: 'Annecy' in r['nom'], '974': lambda r: 'Réunion' in r['nom'], '976': lambda r: 'Mayotte' in r['nom']}
def adr(r):
    a = json.loads(r['adresse'] or '[]'); a = [x for x in a if x['type_adresse'] == 'Adresse'] or a
    if not a: return ''
    x = a[0]; parts = [x.get('complement1'), x.get('complement2'), x.get('numero_voie'), ((x.get('code_postal') or '') + ' ' + (x.get('nom_commune') or '')).strip()]
    return ', '.join(p.strip() for p in parts if p and p.strip())
def tel(r):
    t = json.loads(r['telephone'] or '[]'); return (t[0]['valeur'], (t[0].get('description') or '').strip()) if t else ('', '')
def site(r):
    s = json.loads(r['site_internet'] or '[]'); return s[0]['valeur'] if s else ''
rows = []
for dep, n in D.items():
    if dep in SPEC: c = [r for r in R if SPEC[dep](r)]
    else: c = [r for r in R if k(suffix(r)) == k(n)]
    if not c: print('sans UDAP', dep, n); continue
    r = c[0]; t, h = tel(r)
    mail = r['adresse_courriel'] or ''
    if dep == '2B': mail = 'udap.haute-corse@culture.gouv.fr'  # adresse publiée par le service lui-même (culture.gouv.fr)
    rows.append({'dep': dep, 'nom': r['nom'].replace('’', "'"), 'adresse': adr(r), 'tel': t, 'horaires': h, 'courriel': mail, 'site': site(r), 'fiche': r['url_service_public'] or '', 'rdv': r['formulaire_contact'] or ''})
rows.append({'dep': '971', 'nom': 'Direction des affaires culturelles de Guadeloupe, pôle architecture et patrimoine', 'adresse': '', 'tel': '', 'horaires': '', 'courriel': '', 'site': 'https://www.culture.gouv.fr/Regions/Dac-Guadeloupe/Disciplines-et-secteurs-a-la-DAC-Guadeloupe/Architecture-et-Patrimoine', 'fiche': '', 'rdv': ''})
print('lignes', len(rows))
json.dump(rows, open('udap.json', 'w'), ensure_ascii=False)
