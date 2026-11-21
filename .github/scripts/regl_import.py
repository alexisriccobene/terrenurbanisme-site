# Import de règlements publiés hors Géoportail : téléchargement (PDF ou ZIP), dépôt dans le stockage public « reglements »,
# et (mode « importer ») enregistrement dans reglement_sources. Mode « lister » : inventaire seulement.
import json, os, re, subprocess, sys, zipfile, urllib.request, urllib.parse, urllib.error
REF = os.environ['REF']; SRK = os.environ.get('SRK', ''); MODE = os.environ.get('MODE', 'lister')
PART = os.environ.get('PART', ''); SRC = os.environ['SRC'].split()
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'}
def sql(q):
    rq = urllib.request.Request(f"https://api.supabase.com/v1/projects/{REF}/database/query", data=json.dumps({'query': q}).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + os.environ['SUPABASE_ACCESS_TOKEN'], 'Content-Type': 'application/json'})
    return urllib.request.urlopen(rq, timeout=120).read()
os.makedirs('/tmp/r', exist_ok=True); fichiers = []
for u in SRC:
    n = '/tmp/r/' + re.sub(r'[^A-Za-z0-9._-]', '_', urllib.parse.unquote(u.split('/')[-1]))[:120]
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=600) as x, open(n, 'wb') as f:
        while True:
            b = x.read(1 << 20)
            if not b: break
            f.write(b)
    if zipfile.is_zipfile(n):
        with zipfile.ZipFile(n) as z:
            for i in z.infolist():
                if i.filename.lower().endswith('.pdf') and re.search(os.environ.get('FILTRE') or '.', i.filename, re.I):
                    out = '/tmp/r/' + re.sub(r'[^A-Za-z0-9._-]', '_', i.filename)[-150:]
                    open(out, 'wb').write(z.read(i)); fichiers.append((i.filename, out))
    else: fichiers.append((u.split('/')[-1], n))
inv = []
for nom, chemin in fichiers:
    info = subprocess.run(['pdfinfo', chemin], capture_output=True, text=True).stdout
    pages = next((l.split(':', 1)[1].strip() for l in info.splitlines() if l.startswith('Pages')), None)
    t = subprocess.run(['pdftotext', '-l', '2', chemin, '-'], capture_output=True, text=True).stdout
    e = {'nom': nom, 'mo': round(os.path.getsize(chemin) / 1048576, 2), 'pages': pages, 'debut': re.sub(r'[\x00-\x1f]', ' ', re.sub(r'\s+', ' ', t[:400]))}
    if MODE == 'importer':
        cle = PART + '/' + re.sub(r'[^A-Za-z0-9._-]', '_', nom.split('/')[-1])
        rq = urllib.request.Request(f"https://{REF}.supabase.co/storage/v1/object/reglements/{cle}", data=open(chemin, 'rb').read(), method='POST',
            headers={'Authorization': 'Bearer ' + SRK, 'apikey': SRK, 'Content-Type': 'application/pdf', 'x-upsert': 'true'})
        try: urllib.request.urlopen(rq, timeout=300).read(); e['url'] = f"https://{REF}.supabase.co/storage/v1/object/public/reglements/{cle}"
        except urllib.error.HTTPError as er: e['erreur'] = str(er.code) + ' ' + er.read()[:200].decode('utf-8', 'replace')
    inv.append(e)
sql("insert into public.tu_debug (k, v) values ('regl_import', $tu$" + json.dumps({'part': PART, 'mode': MODE, 'fichiers': inv}, ensure_ascii=False).replace('$tu$', '') + "$tu$::jsonb)")
print(len(inv), 'fichiers')
