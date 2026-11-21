# Sonde rapide d'adresses : statut, type, taille, pages et début du texte (PDF), liens (HTML)
import json, os, re, subprocess, urllib.request, urllib.error
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
out = []
for u in os.environ['URLS'].split():
    r = {'url': u}
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=240) as x:
            b = x.read(); r['http'] = x.status; r['type'] = x.headers.get('Content-Type', ''); r['final'] = x.geturl()
    except urllib.error.HTTPError as e: r['http'] = e.code; b = b''
    except Exception as e: r['err'] = repr(e)[:200]; b = b''
    r['mo'] = round(len(b) / 1048576, 2)
    if b[:5] == b'%PDF-':
        open('/tmp/x.pdf', 'wb').write(b)
        info = subprocess.run(['pdfinfo', '/tmp/x.pdf'], capture_output=True, text=True).stdout
        r['pages'] = next((l.split(':', 1)[1].strip() for l in info.splitlines() if l.startswith('Pages')), None)
        t = subprocess.run(['pdftotext', '-l', '3', '/tmp/x.pdf', '-'], capture_output=True, text=True).stdout
        r['debut'] = re.sub(r'[\x00-\x1f]', ' ', re.sub(r'\s+', ' ', t[:700]))
    elif b:
        h = b[:400000].decode('utf-8', 'replace')
        if h.lstrip().startswith(('{', '[')):
            try:
                J = json.loads(h)
                if isinstance(J, dict) and isinstance(J.get('data'), list) and J['data'] and isinstance(J['data'][0], dict) and 'title' in J['data'][0]:
                    r['jeux'] = [{'t': d.get('title'), 'slug': d.get('slug') or d.get('id'), 'org': (d.get('organization') or {}).get('name'), 'maj': d.get('last_update') or d.get('last_modified'), 'res': [(x.get('title'), x.get('url'), x.get('format')) for x in (d.get('resources') or [])][:8]} for d in J['data']]
                    J = None
                r['json'] = '' if J is None else json.dumps([{k: d.get(k) for k in ('id', 'status', 'effectiveStatus', 'legalStatus', 'uploadDate', 'originalName')} for d in J], ensure_ascii=False)[:6000] if isinstance(J, list) and J and isinstance(J[0], dict) and 'status' in J[0] else h[:6000]
            except Exception: r['json'] = h[:6000]
            if '"idu"' in h: r['idus'] = re.findall(r'"idu":"([0-9A-Z]+)"', h)[:5]
        else: r['liens'] = sorted(set(re.findall(r'href=["\']([^"\']+)', h)))[:300]; r['titre'] = (re.findall(r'<title>([^<]*)', h) or [''])[0][:120]
    out.append(r)
q = "insert into public.tu_debug (k, v) values ('sonde_urls', $tu$" + json.dumps(out, ensure_ascii=False).replace('$tu$', '') + "$tu$::jsonb)"
rq = urllib.request.Request(f"https://api.supabase.com/v1/projects/{os.environ['REF']}/database/query", data=json.dumps({'query': q}).encode(), method='POST',
    headers={'Authorization': 'Bearer ' + os.environ['SUPABASE_ACCESS_TOKEN'], 'Content-Type': 'application/json'})
try: print(urllib.request.urlopen(rq, timeout=60).status)
except urllib.error.HTTPError as e: print(e.code, e.read()[:300])
