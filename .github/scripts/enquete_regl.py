# Enquête approfondie sur les règlements non lisibles : reproduit la logique du rapport (zone au centre, fichier du zonage,
# liste des pièces du Géoportail), télécharge le PDF et vérifie qu'il s'agit bien d'un vrai règlement (texte, articles, zone).
import json, os, re, subprocess, time, urllib.request, urllib.error, urllib.parse
CARTO = 'https://apicarto.ign.fr/api'; UA = {'User-Agent': 'Mozilla/5.0 TerrenUrbanisme-enquete/1.0 (contact@terrenurbanisme.com)'}
def get(url, t=60, raw=False):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t) as r:
                b = r.read(); return (r.status, r.headers.get('Content-Type', ''), b) if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if raw: return (e.code, '', b'')
            if e.code in (400, 404): return None
        except Exception as e:
            last = e
        time.sleep(3 * (k + 1))
    return (0, '', b'') if raw else None
def pt(c): return urllib.parse.quote(json.dumps({'type': 'Point', 'coordinates': c}))
def lire_pdf(url):
    st, ct, b = get(url, 300, raw=True)
    r = {'url': url, 'http': st, 'mo': round(len(b) / 1048576, 2)}
    if st != 200 or not b: return r
    if not b[:5] == b'%PDF-': r['pas_pdf'] = ct; r['debut_html'] = b[:600].decode('utf-8', 'replace'); return r
    open('/tmp/r.pdf', 'wb').write(b)
    info = subprocess.run(['pdfinfo', '/tmp/r.pdf'], capture_output=True, text=True).stdout
    r['pages'] = next((l.split(':', 1)[1].strip() for l in info.splitlines() if l.startswith('Pages')), None)
    t = subprocess.run(['pdftotext', '-layout', '/tmp/r.pdf', '-'], capture_output=True, text=True).stdout
    r['chars'] = len(t); r['debut'] = re.sub(r'[\x00-\x08\x0b-\x1f]', ' ', re.sub(r'\s+', ' ', t[:1500]))
    r['articles'] = len(re.findall(r'\barticle\b', t, re.I)); r['hauteur'] = len(re.findall(r'hauteur', t, re.I))
    r['liens'] = sorted(set(re.findall(r'https?://[^\s<>"\)]+', t)))[:15]
    return r
def enquete(insee):
    c = get(f'https://geo.api.gouv.fr/communes/{insee}?fields=nom,centre') or {}
    r = {'insee': insee, 'nom': c.get('nom')}
    ctr = (c.get('centre') or {}).get('coordinates')
    z = get(f"{CARTO}/gpu/zone-urba?geom={pt(ctr)}") or {}
    zs = z.get('features') or []
    if not zs:
        d = get(f"{CARTO}/gpu/document?geom={pt(ctr)}") or {}
        r['documents_centre'] = [f.get('properties') for f in d.get('features') or []][:3]
        m = get(f"{CARTO}/gpu/municipality?insee={insee}") or {}
        r['municipality'] = [f.get('properties') for f in m.get('features') or []][:1]
        r['etat'] = 'pas_de_zonage'; return r
    p = zs[0]['properties']; r['zone'] = {k: p.get(k) for k in ('libelle', 'libelong', 'typezone', 'partition', 'gpu_doc_id', 'nomfic', 'urlfic', 'datappro', 'gpu_timestamp')}
    files = get(f"https://www.geoportail-urbanisme.gouv.fr/api/document/{p.get('gpu_doc_id')}/files", 60) if p.get('gpu_doc_id') else None
    names = [x if isinstance(x, str) else (x.get('name') or x.get('path') or '') for x in (files if isinstance(files, list) else (files or {}).get('files', []) or [])]
    r['pieces'] = [n for n in names if re.search(r'r[eè]gl|\.pdf$', n, re.I)][:60]; r['nb_pieces'] = len(names)
    nomfic = str(p.get('nomfic') or '').split('#')[0]
    cands = []
    if nomfic: cands.append(f"https://data.geopf.fr/annexes/gpu/documents/{p['partition']}/{p['gpu_doc_id']}/{nomfic}")
    for n in names:
        if re.search(r'r[eè]glement', n, re.I) and not re.search(r'graphique|plan|zonage', n, re.I) and n.lower().endswith('.pdf'):
            cands.append(f"https://data.geopf.fr/annexes/gpu/documents/{p['partition']}/{p['gpu_doc_id']}/{n}")
    if p.get('urlfic'): cands.append(p['urlfic'].split('#')[0])
    seen = []; [seen.append(u) for u in cands if u not in seen]
    r['lectures'] = [lire_pdf(u) for u in seen[:5]]
    return r
def envoyer(o):
    t = json.dumps(o, ensure_ascii=False).replace('$tu$', '').replace('\\u0000', '')
    q = "insert into public.tu_debug (k, v) values ('enquete_regl', $tu$" + t + "$tu$::jsonb)"
    rq = urllib.request.Request(f"https://api.supabase.com/v1/projects/{os.environ['REF']}/database/query", data=json.dumps({'query': q}).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + os.environ['SUPABASE_ACCESS_TOKEN'], 'Content-Type': 'application/json'})
    try: print(urllib.request.urlopen(rq, timeout=60).status)
    except urllib.error.HTTPError as e: print('::warning::', e.code, e.read()[:300])
for i in os.environ['INSEE'].split():
    try: envoyer([enquete(i)])
    except Exception as e: envoyer([{'insee': i, 'erreur': repr(e)[:300]}])
