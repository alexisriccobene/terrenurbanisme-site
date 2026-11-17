"""Télécharge un fichier du stockage (bucket/chemin indiqués dans demande.json) vers les sorties de test."""
import os, json, requests
d = json.load(open('.github/foncier/demande.json'))
base = f"https://{os.environ['REF']}.supabase.co"; K = os.environ['SR']
r = requests.get(f"{base}/storage/v1/object/{d['bucket']}/{d['chemin']}", headers={'apikey': K, 'Authorization': 'Bearer ' + K}, timeout=120)
print(r.status_code, len(r.content))
open('/tmp/out/' + d.get('nom', 'fichier.pdf'), 'wb').write(r.content)
