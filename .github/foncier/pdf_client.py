import os, requests, json
SR = os.environ['SR']; U = 'https://nmoigruxnhsidrhqtzid.supabase.co'
h = {'apikey': SR, 'Authorization': 'Bearer ' + SR}
d = requests.get(U + '/rest/v1/dossiers?select=id,perso,pdf_path&id=eq.39686a13-3179-4ce2-86d5-284c9cadfdfa', headers=h).json()
print(json.dumps(d)[:3000])
p = 'ca45b46d-24e0-4b79-8067-217f6b84a6ed/client/credit_330fecb6-ded4-4bff-9a10-417036d95d41.pdf'
r = requests.get(U + '/storage/v1/object/dossiers/' + p, headers=h); print(r.status_code, len(r.content))
open('/tmp/out/client.pdf', 'wb').write(r.content)
r2 = requests.get('https://terrenurbanisme.com/rapport/c-39686a133179.pdf'); print('court', r2.status_code, r2.headers.get('content-type'), len(r2.content))
r3 = requests.get('https://terrenurbanisme.com/r/c-39686a133179'); print('page', r3.status_code, len(r3.content))
