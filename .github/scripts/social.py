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

def publish_fb(p):
    ids = [api('POST', '/%s/photos' % PAGE, url=RAW + f, published='false')['id'] for f in p['images']]
    params = {'message': p['texte_facebook']}
    for i, m in enumerate(ids): params['attached_media[%d]' % i] = json.dumps({'media_fbid': m})
    return api('POST', '/%s/feed' % PAGE, **params)['id']

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
    print('::notice::Connexion Meta OK : page « %s », Instagram %s' % (me.get('name'), ig)); sys.exit(0)

plan = json.load(open(PLAN, encoding='utf-8'))
done = json.load(open(DONE, encoding='utf-8')) if os.path.exists(DONE) else {}
now = datetime.now(ZoneInfo('Europe/Paris'))
changed, errors = False, []
for p in plan:
    when = datetime.fromisoformat(p['date']).replace(tzinfo=ZoneInfo('Europe/Paris'))
    if when > now: continue
    if (now - when).total_seconds() > 6 * 3600: continue  # trop ancien : on ne publie pas en retard de plus de 6 h
    d = done.setdefault(p['id'], {})
    for net, fn in (('instagram', lambda: publish_ig(ig, p)), ('facebook', lambda: publish_fb(p))):
        if net not in p.get('reseaux', ['instagram', 'facebook']) or d.get(net): continue
        try:
            d[net] = fn(); changed = True; print('::notice::%s publié sur %s (%s)' % (p['id'], net, d[net]))
        except Exception as e:
            errors.append('%s %s : %s' % (p['id'], net, e)); print('::error::%s %s : %s' % (p['id'], net, str(e)[:600]))
if changed: json.dump(done, open(DONE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.exit(1 if errors else 0)
