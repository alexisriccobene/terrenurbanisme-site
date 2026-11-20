# Diagnostic des règlements non lus : propriétés de la zone (Géoportail de l'Urbanisme), fichiers du document, accessibilité des PDF
import json, os, sys, urllib.request, urllib.parse, re, time
UA = {'User-Agent': 'TerrenUrbanisme-diag/1.0 (contact@terrenurbanisme.com)'}
def get(u, t=60, raw=False):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r:
                b = r.read(); return b if raw else json.loads(b)
        except Exception as e:
            last = e; time.sleep(2 + 2 * a)
    raise last
def head(u):
    try:
        rq = urllib.request.Request(u, headers=dict(UA, Range='bytes=0-1023'))
        with urllib.request.urlopen(rq, timeout=60) as r:
            return {'st': r.status, 'type': r.headers.get('Content-Type'), 'len': r.headers.get('Content-Range') or r.headers.get('Content-Length')}
    except Exception as e:
        return {'err': str(e)[:160]}
out = []
for ref in os.environ['PARCELLES'].split():
    insee, sec, num = ref.split(':'); r = {'ref': ref}
    try:
        pj = get(f'https://apicarto.ign.fr/api/cadastre/parcelle?code_insee={insee}&section={sec.zfill(2)}&numero={num.zfill(4)}')
        f = pj['features'][0]; g = f['geometry']
        from statistics import mean
        ring = g['coordinates'][0][0] if g['type'] == 'MultiPolygon' else g['coordinates'][0]
        c = {'type': 'Point', 'coordinates': [mean(p[0] for p in ring), mean(p[1] for p in ring)]}
        zj = get('https://apicarto.ign.fr/api/gpu/zone-urba?geom=' + urllib.parse.quote(json.dumps(c)))
        zs = [z['properties'] for z in zj.get('features', [])]
        r['zones'] = [{k: z.get(k) for k in ('libelle', 'libelong', 'typezone', 'nomfic', 'urlfic', 'gpu_doc_id', 'partition', 'idurba', 'datappro')} for z in zs]
        if zs:
            z = zs[0]
            if z.get('gpu_doc_id') and z.get('nomfic') and z.get('partition'):
                u = f"https://data.geopf.fr/annexes/gpu/documents/{z['partition']}/{z['gpu_doc_id']}/{str(z['nomfic']).split('#')[0]}"
                r['gpu_url'] = u; r['gpu_head'] = head(u)
            if z.get('urlfic'): r['urlfic_head'] = head(str(z['urlfic']).split('#')[0])
            if z.get('gpu_doc_id'):
                try:
                    fl = get(f"https://www.geoportail-urbanisme.gouv.fr/api/document/{z['gpu_doc_id']}/files")
                    names = [x.get('name') or x.get('path') or str(x) for x in (fl if isinstance(fl, list) else fl.get('files', []))]
                    r['files_n'] = len(names); r['reglement_files'] = [n for n in names if re.search(r'r[eè]gl', str(n), re.I)][:20]
                except Exception as e: r['files_err'] = str(e)[:160]
    except Exception as e:
        r['err'] = str(e)[:200]
    out.append(r); print(json.dumps(r, ensure_ascii=False)[:600])
json.dump(out, open('diag_zones.json', 'w'), ensure_ascii=False, indent=1)
