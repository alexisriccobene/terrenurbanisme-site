import requests, os, json, gzip
base = f"https://{os.environ['REF']}.supabase.co"; HS = {'apikey': os.environ['SR'], 'Authorization': 'Bearer ' + os.environ['SR']}
r = requests.get(f'{base}/storage/v1/object/foncier/2B.json.gz', headers=HS, timeout=300); l = json.loads(gzip.decompress(r.content))
for s in l[:5]: print({k: s.get(k) for k in ('id','lat','lon','poste_km','poste_nom','poste_tension','poste_exploitant')})
import collections; print(collections.Counter(int(s.get('poste_km',0)//100) for s in l).most_common(5))
