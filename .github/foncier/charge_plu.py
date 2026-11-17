"""Charge les zonages PLU extraits des cartes PDF communales (.github/plu/<insee>.json) dans zonage_local."""
import os, json, glob, requests
base = f"https://{os.environ['REF']}.supabase.co"
H = {'apikey': os.environ['SR'], 'Authorization': 'Bearer ' + os.environ['SR'], 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
for f in sorted(glob.glob('.github/plu/*.json')):
    rows = json.load(open(f)); insee = os.path.basename(f)[:-5]
    requests.delete(f'{base}/rest/v1/zonage_local?insee=eq.{insee}', headers=H, timeout=120).raise_for_status()
    for i in range(0, len(rows), 50):
        r = requests.post(f'{base}/rest/v1/zonage_local', headers=H, data=json.dumps(rows[i:i+50]), timeout=120)
        if r.status_code >= 300: print(r.text[:500]); r.raise_for_status()
    print(insee, len(rows), 'zones')
