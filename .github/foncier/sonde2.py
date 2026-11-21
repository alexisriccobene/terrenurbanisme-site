import requests, zipfile, io, os, csv, gzip, json, time
H = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
def dl(u, p, to=900):
    t=time.time()
    with requests.get(u, headers=H, stream=True, timeout=to) as r:
        print('DL', r.status_code, u[-80:]); r.raise_for_status()
        with open(p, 'wb') as f:
            for c in r.iter_content(1 << 20): f.write(c)
    print('  taille', os.path.getsize(p), round(time.time()-t), 's')
# Personnes morales 2026
dl('https://data.economie.gouv.fr/api/v2/catalog/datasets/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/attachments/fichiers_des_parcelles_dpts_1_a_30_situation_2026zip', '/tmp/pm.zip')
z = zipfile.ZipFile('/tmp/pm.zip')
for i in z.infolist()[:60]: print(' ', i.filename, i.file_size)
def peek(zf, depth=0):
    for i in zf.infolist():
        n=i.filename.lower()
        if n.endswith('.zip'):
            inner = zipfile.ZipFile(io.BytesIO(zf.read(i)))
            if '2a' in n or '2b' in n or '20' in n: print('INNER', i.filename); peek(inner, depth+1)
        elif ('2a' in n or '2b' in n) and not n.endswith('/'):
            print('FILE', i.filename, i.file_size)
            with zf.open(i) as f:
                for k, line in enumerate(f):
                    print('   ', line.decode('latin-1').rstrip()[:400])
                    if k > 4: break
peek(z)
# Friches
dl('https://static.data.gouv.fr/resources/sites-references-dans-cartofriches/20261007-122232/friches-standard.csv', '/tmp/fr.csv')
with open('/tmp/fr.csv', encoding='utf-8') as f:
    rd = csv.reader(f); h = next(rd); print('FRICHES HEADER', h)
    n=0
    for row in rd:
        d=dict(zip(h,row))
        if any(str(v).startswith(('2A','2B')) for v in row[:12]) or 'Corse' in ' '.join(row[:15]):
            n+=1
            if n<=2: print(json.dumps(d, ensure_ascii=False)[:1500])
    print('friches corse approx', n)
# Cadastre 2B
try: dl('https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/departements/2B/cadastre-2B-parcelles.json.gz', '/tmp/c2b.gz', 1200)
except Exception as e: print('cadastre ERR', e)
# Overpass miroirs
q = '[out:json][timeout:90];area["ISO3166-2"="FR-20R"]->.a;(node["power"="substation"](area.a);way["power"="substation"](area.a););out center tags;'
for u in ['https://overpass.kumi.systems/api/interpreter','https://overpass.private.coffee/api/interpreter','https://overpass-api.de/api/interpreter','https://maps.mail.ru/osm/tools/overpass/api/interpreter']:
    try:
        r = requests.post(u, data={'data': q}, headers=H, timeout=150); print('OVERPASS', u, r.status_code)
        el = r.json()['elements']; print(len(el)); print(json.dumps(el[:4], ensure_ascii=False)[:1500]); break
    except Exception as e: print('  err', str(e)[:200])
