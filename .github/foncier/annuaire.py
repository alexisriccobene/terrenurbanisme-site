"""Coordonnées officielles des mairies (annuaire service-public) pour une liste de codes INSEE : e-mail, téléphone, site, formulaire de contact."""
import requests, json, os, time
H = {'User-Agent': 'Mozilla/5.0 (TerrenUrbanisme; contact@terrenurbanisme.com)'}
D = json.load(open('.github/plu-demande.json'))
U = 'https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/records'
def j(v):
    try: return json.loads(v) if isinstance(v, str) else v
    except Exception: return v
out = []
for insee in D['insee']:
    rec = None
    for k in range(3):
        try:
            r = requests.get(U, params={'where': f'code_insee_commune="{insee}" and pivot like "mairie"', 'limit': 5}, headers=H, timeout=30).json()
            res = [x for x in r.get('results', []) if 'mairie' in json.dumps(j(x.get('pivot')) or '').lower()]
            rec = res[0] if res else None; break
        except Exception as e: print(insee, 'essai', k, e); time.sleep(3)
    if not rec: print(insee, 'introuvable'); out.append({'insee': insee}); continue
    tel = j(rec.get('telephone')) or []; site = j(rec.get('site_internet')) or []; form = j(rec.get('formulaire_contact')) or rec.get('formulaire_contact')
    o = {'insee': insee, 'nom': rec.get('nom'), 'email': rec.get('adresse_courriel'), 'tel': [t.get('valeur') for t in tel] if isinstance(tel, list) else tel,
         'site': [s.get('valeur') for s in site] if isinstance(site, list) else site, 'formulaire': form}
    print(json.dumps(o, ensure_ascii=False)); out.append(o); time.sleep(0.3)
os.makedirs("/tmp/out", exist_ok=True)
json.dump(out, open("/tmp/out/mairies.json", "w"), ensure_ascii=False, indent=1)
