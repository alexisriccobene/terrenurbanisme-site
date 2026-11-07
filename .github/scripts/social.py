# Publication automatique Instagram + Facebook (API Graph de Meta) depuis .github/social/plan.json
# Chaque publication part à son heure (Europe/Paris). Les publications faites sont notées dans .github/social/publie.json.
import json, os, sys, time, urllib.request, urllib.parse, urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo

G = 'https://graph.facebook.com/v26.0'
TOKEN = os.environ.get('META_PAGE_TOKEN', '')
PAGE = os.environ.get('FB_PAGE_ID', '')
RAW = 'https://raw.githubusercontent.com/' + os.environ['GITHUB_REPOSITORY'] + '/main/.github/social/img/'
MODE = os.environ.get('MODE', 'publier')
PLAN, DONE = '.github/social/plan.json', '.github/social/publie.json'

def api(method, path, **params):
    params['access_token'] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = G + path + ('?' + data.decode() if method == 'GET' else '')
    req = urllib.request.Request(url, data=None if method == 'GET' else data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError('Meta %s %s : %s' % (e.code, path.split('?')[0], e.read()[:400].decode(errors='replace')))

def ig_id():
    r = api('GET', '/' + PAGE, fields='instagram_business_account,name')
    if not r.get('instagram_business_account'): raise RuntimeError('aucun compte Instagram professionnel relié à la page ' + r.get('name', PAGE))
    return r['instagram_business_account']['id']

def ig_wait(cid):
    for _ in range(30):
        s = api('GET', '/' + cid, fields='status_code').get('status_code')
        if s == 'FINISHED': return
        if s == 'ERROR': raise RuntimeError('Instagram a refusé un média')
        time.sleep(5)
    raise RuntimeError('Instagram : média trop long à traiter')

def publish_ig(ig, p):
    urls = [RAW + f for f in p['images']]
    if len(urls) == 1:
        c = api('POST', '/%s/media' % ig, image_url=urls[0], caption=p['texte_instagram'])['id']
    else:
        kids = []
        for u in urls[:10]:
            k = api('POST', '/%s/media' % ig, image_url=u, is_carousel_item='true')['id']; ig_wait(k); kids.append(k)
        c = api('POST', '/%s/media' % ig, media_type='CAROUSEL', children=','.join(kids), caption=p['texte_instagram'])['id']
    ig_wait(c)
    return api('POST', '/%s/media_publish' % ig, creation_id=c)['id']

def publish_ig_story(ig, p):
    c = api('POST', '/%s/media' % ig, image_url=RAW + p['images'][0], media_type='STORIES')['id']
    ig_wait(c)
    return api('POST', '/%s/media_publish' % ig, creation_id=c)['id']

def publish_fb_story(p):
    ph = api('POST', '/%s/photos' % PAGE, url=RAW + p['images'][0], published='false')['id']
    r = api('POST', '/%s/photo_stories' % PAGE, photo_id=ph)
    return r.get('post_id') or r.get('id') or 'ok'

def publish_fb(p):
    ids = [api('POST', '/%s/photos' % PAGE, url=RAW + f, published='false')['id'] for f in p['images']]
    params = {'message': p['texte_facebook']}
    for i, m in enumerate(ids): params['attached_media[%d]' % i] = json.dumps({'media_fbid': m})
    return api('POST', '/%s/feed' % PAGE, **params)['id']


# ---------- LinkedIn (page entreprise, Community Management API) ----------
LI_TOKEN = os.environ.get('LINKEDIN_TOKEN', '')
LI_REFRESH = os.environ.get('LINKEDIN_REFRESH', '')
LI_CID, LI_SECRET = os.environ.get('LINKEDIN_CLIENT_ID', ''), os.environ.get('LINKEDIN_CLIENT_SECRET', '')
LI_ORG = ''.join(ch for ch in os.environ.get('LINKEDIN_ORG', '') if ch.isdigit())
LI_VERSIONS = ['202609', '202606', '202603', '202512', '202510']
LI = {'token': LI_TOKEN, 'version': None, 'refreshed': False}

def li_refresh():
    if LI['refreshed'] or not (LI_REFRESH and LI_CID and LI_SECRET): return False
    LI['refreshed'] = True
    data = urllib.parse.urlencode({'grant_type': 'refresh_token', 'refresh_token': LI_REFRESH, 'client_id': LI_CID, 'client_secret': LI_SECRET}).encode()
    req = urllib.request.Request('https://www.linkedin.com/oauth/v2/accessToken', data=data, method='POST', headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=60) as r: LI['token'] = json.loads(r.read())['access_token']
    print('jeton LinkedIn renouvelé'); return True

def li(method, path, body=None, raw=None, headers=None, full=False):
    versions = [LI['version']] if LI['version'] else LI_VERSIONS
    last = None
    for v in versions:
        h = {'Authorization': 'Bearer ' + LI['token'], 'LinkedIn-Version': v, 'X-Restli-Protocol-Version': '2.0.0'}
        if body is not None: h['Content-Type'] = 'application/json'
        h.update(headers or {})
        req = urllib.request.Request(path if path.startswith('http') else 'https://api.linkedin.com/rest' + path,
                                     data=raw if raw is not None else (json.dumps(body).encode() if body is not None else None), method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                LI['version'] = v; txt = r.read()
                return (r, json.loads(txt) if txt else {}) if full else (json.loads(txt) if txt else {})
        except urllib.error.HTTPError as e:
            msg = e.read()[:400].decode(errors='replace'); last = 'LinkedIn %s %s : %s' % (e.code, path.split('?')[0][-60:], msg)
            if e.code == 401 and li_refresh(): return li(method, path, body, raw, headers, full)
            if e.code == 426 or 'NONEXISTENT_VERSION' in msg or 'VERSION_MISSING' in msg: continue
            raise RuntimeError(last)
    raise RuntimeError(last or 'LinkedIn : aucune version d\'API acceptée')

def li_text(t):
    import re
    t = re.sub(r'([\\|{}@\[\]()<>#*_~])', r'\\\1', t)
    return re.sub(r'\\#(\w+)', r'{hashtag|\\#|\1}', t)

def li_image(fname):
    r = li('POST', '/images?action=initializeUpload', {'initializeUploadRequest': {'owner': 'urn:li:organization:' + LI_ORG}})['value']
    data = open('.github/social/img/' + fname, 'rb').read()
    req = urllib.request.Request(r['uploadUrl'], data=data, method='PUT', headers={'Authorization': 'Bearer ' + LI['token'], 'Content-Type': 'application/octet-stream'})
    urllib.request.urlopen(req, timeout=120).read()
    return r['image']


def jpg_size(b):
    i = 2
    while i < len(b):
        if b[i] != 0xFF: i += 1; continue
        m = b[i + 1]
        if m in (0xC0, 0xC1, 0xC2): return int.from_bytes(b[i + 7:i + 9], 'big'), int.from_bytes(b[i + 5:i + 7], 'big')
        i += 2 + int.from_bytes(b[i + 2:i + 4], 'big')
    raise RuntimeError('taille JPEG introuvable')

def jpgs_to_pdf(files):
    # PDF minimal : une page par image JPEG (sans bibliothèque externe). Objets : 1 catalogue, 2 pages, puis page/image/contenu
    objs, kids = [], []
    for f in files:
        b = open('.github/social/img/' + f, 'rb').read(); w, h = jpg_size(b)
        pn = 3 + len(objs)
        kids.append(pn)
        objs.append(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] /Resources << /XObject << /Im0 %d 0 R >> >> /Contents %d 0 R >>' % (w, h, pn + 1, pn + 2))
        objs.append(b'<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n' % (w, h, len(b)) + b + b'\nendstream')
        cs = b'q %d 0 0 %d 0 0 cm /Im0 Do Q' % (w, h)
        objs.append(b'<< /Length %d >>\nstream\n' % len(cs) + cs + b'\nendstream')
    allobjs = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [' + b' '.join(b'%d 0 R' % k for k in kids) + b'] /Count %d >>' % len(kids)] + objs
    out, offs = bytearray(b'%PDF-1.4\n'), []
    for i, o in enumerate(allobjs, 1):
        offs.append(len(out)); out += b'%d 0 obj\n' % i + o + b'\nendobj\n'
    x = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(allobjs) + 1) + b''.join(b'%010d 00000 n \n' % o for o in offs)
    out += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF' % (len(allobjs) + 1, x)
    return bytes(out)

def publish_li(p):
    if len(p['images']) == 1:
        content = {'media': {'id': li_image(p['images'][0]), 'altText': p.get('theme', '')[:120]}}
    else:  # carrousel : document PDF (format carrousel natif de LinkedIn)
        r = li('POST', '/documents?action=initializeUpload', {'initializeUploadRequest': {'owner': 'urn:li:organization:' + LI_ORG}})['value']
        req = urllib.request.Request(r['uploadUrl'], data=jpgs_to_pdf(p['images'][:20]), method='PUT', headers={'Authorization': 'Bearer ' + LI['token'], 'Content-Type': 'application/octet-stream'})
        urllib.request.urlopen(req, timeout=120).read()
        doc = r['document']
        for _ in range(24):
            st = li('GET', '/documents/' + urllib.parse.quote(doc, safe='')).get('status')
            if st == 'AVAILABLE': break
            if st == 'PROCESSING_FAILED': raise RuntimeError('LinkedIn : document refusé')
            time.sleep(5)
        content = {'media': {'title': p.get('theme', 'TerrenUrbanisme')[:200], 'id': doc}}
    body = {'author': 'urn:li:organization:' + LI_ORG, 'commentary': li_text(p.get('texte_linkedin') or p.get('texte_facebook') or p.get('texte_instagram', '')),
            'visibility': 'PUBLIC', 'distribution': {'feedDistribution': 'MAIN_FEED', 'targetEntities': [], 'thirdPartyDistributionChannels': []},
            'content': content, 'lifecycleState': 'PUBLISHED', 'isReshareDisabledByAuthor': False}
    r, _ = li('POST', '/posts', body, full=True)
    return r.headers.get('x-restli-id') or r.headers.get('x-linkedin-id') or 'ok'
LI_ON = bool(LI_TOKEN and LI_ORG)

if not TOKEN or not PAGE:
    print('::warning::Publication automatique non configurée (secrets META_PAGE_TOKEN et FB_PAGE_ID manquants)'); sys.exit(0)
def alerte_expiration():
    # Une fois par jour (vers 9 h) : si l'autorisation Meta expire dans moins de 15 jours, ouvre une alerte GitHub (e-mail au propriétaire du dépôt)
    try:
        d = api('GET', '/debug_token', input_token=TOKEN).get('data', {})
    except Exception as e:
        print('contrôle expiration impossible :', str(e)[:200]); return
    exp = [t for t in (d.get('expires_at'), d.get('data_access_expires_at')) if t]
    if not exp: return
    jours = (min(exp) - time.time()) / 86400
    print('autorisation Meta valable encore %.0f jours' % jours)
    if jours > 15: return
    gh = os.environ.get('GITHUB_TOKEN'); repo = os.environ['GITHUB_REPOSITORY']
    if not gh: return
    titre = 'Renouveler l autorisation Meta (Instagram et Facebook)'
    h = {'Authorization': 'Bearer ' + gh, 'Accept': 'application/vnd.github+json'}
    q = urllib.request.Request('https://api.github.com/repos/%s/issues?state=open&per_page=50' % repo, headers=h)
    if any(i.get('title') == titre for i in json.loads(urllib.request.urlopen(q, timeout=30).read())): return
    body = ("L'autorisation qui permet de publier sur Instagram et Facebook expire dans %d jours.\n\n"
            "Ouvrez la conversation Claude TerrenUrbanisme et écrivez : « renouveler Meta ». Cela prend 2 minutes.") % max(0, jours)
    r = urllib.request.Request('https://api.github.com/repos/%s/issues' % repo, data=json.dumps({'title': titre, 'body': body}).encode(), headers=h, method='POST')
    urllib.request.urlopen(r, timeout=30); print('::warning::' + titre + ' : expire dans %d jours' % jours)

ig = ig_id()
_n = datetime.now(ZoneInfo('Europe/Paris'))
if MODE == 'verifier' or (_n.hour == 9 and _n.minute < 15): alerte_expiration()
if MODE == 'verifier':
    me = api('GET', '/' + PAGE, fields='name')
    print('::notice::Connexion Meta OK : page « %s », Instagram %s' % (me.get('name'), ig))
    etat = {'page': me.get('name'), 'instagram': ig, 'controle': datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='minutes')}
    done0 = json.load(open(DONE, encoding='utf-8')) if os.path.exists(DONE) else {}
    for k, v in list(done0.items())[-3:]:
        for net, mid in v.items():
            try:
                if net == 'instagram': etat[k + ' instagram'] = api('GET', '/' + mid, fields='media_type,timestamp,permalink')
                else: etat[k + ' facebook'] = api('GET', '/' + mid, fields='id,created_time,permalink_url')
            except Exception as e: etat[k + ' ' + net] = 'erreur : ' + str(e)[:300]
    try: etat['stories facebook de la page'] = api('GET', '/%s/stories' % PAGE).get('data', [])[:5]
    except Exception as e: etat['stories facebook de la page'] = 'erreur : ' + str(e)[:300]
    if LI_ON:
        try:
            o = li('GET', '/organizations/' + LI_ORG)
            etat['linkedin'] = {'page': (o.get('localizedName') or o.get('vanityName')), 'version_api': LI['version'], 'jeton_renouvele': LI['refreshed']}
            print('::notice::Connexion LinkedIn OK : page « %s »' % etat['linkedin']['page'])
        except Exception as e: etat['linkedin'] = 'erreur : ' + str(e)[:400]; print('::error::LinkedIn : ' + str(e)[:400])
    else: etat['linkedin'] = 'non configuré'
    json.dump(etat, open('.github/social/etat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(0)

plan = json.load(open(PLAN, encoding='utf-8'))
done = json.load(open(DONE, encoding='utf-8')) if os.path.exists(DONE) else {}
now = datetime.now(ZoneInfo('Europe/Paris'))
changed, errors = False, []
for p in plan:
    when = datetime.fromisoformat(p['date']).replace(tzinfo=ZoneInfo('Europe/Paris'))
    if when > now: continue
    if (now - when).total_seconds() > 20 * 3600: continue  # filet de sécurité : au-delà de 20 h de retard, on ne publie plus
    d = done.setdefault(p['id'], {})
    story = p.get('type') == 'story'
    jobs = (('instagram', lambda: publish_ig_story(ig, p) if story else publish_ig(ig, p)),
            ('facebook', lambda: publish_fb_story(p) if story else publish_fb(p)),
            ('linkedin', lambda: publish_li(p)))
    for net, fn in jobs:
        if net not in p.get('reseaux', ['instagram', 'facebook']) or d.get(net): continue
        if net == 'linkedin' and (story or not LI_ON): continue
        if d.get(net + '_echecs', 0) >= 2: continue  # deux échecs : on n'insiste pas (évite les alertes en boucle)
        try:
            d[net] = fn(); changed = True; print('::notice::%s publié sur %s (%s)' % (p['id'], net, d[net]))
        except Exception as e:
            d[net + '_echecs'] = d.get(net + '_echecs', 0) + 1; changed = True
            errors.append('%s %s : %s' % (p['id'], net, e)); print('::error::%s %s : %s' % (p['id'], net, str(e)[:600]))
if changed: json.dump(done, open(DONE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.exit(1 if errors else 0)
