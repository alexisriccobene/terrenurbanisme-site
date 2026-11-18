# Robot TikTok TerrenUrbanisme : connexion du compte, contrôle et publication (Content Posting API)
# Les jetons TikTok sont conservés chiffrés (clé = secret TIKTOK_CLIENT_SECRET) dans .github/social/tiktok.enc
import json, os, sys, time, secrets, subprocess, urllib.request, urllib.parse, urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo
KEY, SECRET = os.environ.get('TIKTOK_CLIENT_KEY', '').strip(), os.environ.get('TIKTOK_CLIENT_SECRET', '').strip()
os.environ['TIKTOK_CLIENT_SECRET'] = SECRET  # sans espace parasite copié par erreur
MODE = os.environ.get('MODE', 'publier')
REDIRECT = 'https://terrenurbanisme.com/tiktok-retour.html'
ENC, ETAT, PLAN, DONE = '.github/social/tiktok.enc', '.github/social/tiktok_etat.json', '.github/social/plan.json', '.github/social/publie_tiktok.json'
VID = '.github/social/img/'
API = 'https://open.tiktokapis.com/v2'

def req(url, data=None, token=None, js=False):
    h = {}
    if token: h['Authorization'] = 'Bearer ' + token
    if js: h['Content-Type'] = 'application/json; charset=UTF-8'; body = json.dumps(data).encode()
    elif data is not None: h['Content-Type'] = 'application/x-www-form-urlencoded'; body = urllib.parse.urlencode(data).encode()
    else: body = None
    r = urllib.request.Request(url, data=body, headers=h, method='POST' if body is not None else 'GET')
    try:
        with urllib.request.urlopen(r, timeout=120) as x: return json.loads(x.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError('TikTok %s %s : %s' % (e.code, url.split('?')[0].replace(API, ''), e.read()[:500].decode(errors='replace')))

def sauver(tok):
    p = subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-salt', '-a', '-A', '-pass', 'env:TIKTOK_CLIENT_SECRET', '-out', ENC],
                       input=json.dumps(tok).encode(), check=True)
def charger():
    p = subprocess.run(['openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2', '-a', '-A', '-pass', 'env:TIKTOK_CLIENT_SECRET', '-in', ENC], capture_output=True, check=True)
    return json.loads(p.stdout)

def jetons(r):
    if 'access_token' not in r: raise RuntimeError('TikTok n a pas délivré de jeton : ' + json.dumps(r)[:400])
    t = time.time()
    return {'access_token': r['access_token'], 'refresh_token': r['refresh_token'], 'open_id': r.get('open_id'), 'scope': r.get('scope'),
            'access_expire': t + r.get('expires_in', 0) - 300, 'refresh_expire': t + r.get('refresh_expires_in', 0)}

def acces():
    tok = charger()
    if time.time() > tok['access_expire']:
        tok = jetons(req(API + '/oauth/token/', {'client_key': KEY, 'client_secret': SECRET, 'grant_type': 'refresh_token', 'refresh_token': tok['refresh_token']}))
        sauver(tok)
    return tok

def etat(extra):
    e = json.load(open(ETAT, encoding='utf-8')) if os.path.exists(ETAT) else {}
    e.update(extra); e['controle'] = datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='minutes')
    json.dump(e, open(ETAT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def createur(tok):
    return req(API + '/post/publish/creator_info/query/', {}, tok['access_token'], js=True).get('data', {})


# --- Zernio (publication publique sur TikTok, sans attendre la validation de notre application) ---
ZKEY = os.environ.get('ZERNIO_API_KEY', '').strip(); ZAPI = 'https://zernio.com/api/v1'
def zreq(path, data=None, method=None):
    h = {'Authorization': 'Bearer ' + ZKEY, 'Content-Type': 'application/json'}
    r = urllib.request.Request(ZAPI + path, data=json.dumps(data).encode() if data is not None else None, headers=h, method=method or ('POST' if data is not None else 'GET'))
    for essai in range(6):
        try:
            with urllib.request.urlopen(r, timeout=120) as x: return json.loads(x.read() or b'{}')
        except urllib.error.HTTPError as e:
            txt = e.read()[:500].decode(errors='replace')
            if e.code == 429 and essai < 5:
                try: w = int(json.loads(txt).get('details', {}).get('retryAfterSeconds', 5))
                except Exception: w = 5
                time.sleep(min(w, 65) + 1); continue
            raise RuntimeError('Zernio %s %s : %s' % (e.code, path, txt))
ZACC = {}
def zcompte():
    if ZACC: return ZACC['v']
    r = zreq('/accounts')
    L = (r.get('accounts') or r.get('data') or []) if isinstance(r, dict) else r
    for a in L or []:
        if str(a.get('platform', '')).lower() == 'tiktok': ZACC['v'] = (a.get('_id') or a.get('id'), a); return ZACC['v']
    raise RuntimeError('Aucun compte TikTok connecté dans Zernio : ' + json.dumps(r)[:300])
def publier_zernio(p, quand=None):
    acc, _ = zcompte()
    f = VID + (p.get('video_tiktok') or p['video']); n = os.path.getsize(f)
    pre = zreq('/media/presign', {'filename': os.path.basename(f), 'contentType': 'video/mp4', 'size': n})
    up = urllib.request.Request(pre['uploadUrl'], data=open(f, 'rb').read(), method='PUT', headers={'Content-Type': 'video/mp4'})
    urllib.request.urlopen(up, timeout=300).read()
    body = {'content': (p.get('texte_tiktok') or p.get('texte_instagram') or p.get('theme', ''))[:2200],
            'mediaItems': [{'type': 'video', 'url': pre['publicUrl']}], 'platforms': [{'platform': 'tiktok', 'accountId': acc}],
            'tiktokSettings': {'privacy_level': 'PUBLIC_TO_EVERYONE', 'allow_comment': True, 'allow_duet': True, 'allow_stitch': True,
                               'content_preview_confirmed': True, 'express_consent_given': True}}
    if quand: body.update({'scheduledFor': quand, 'timezone': 'Europe/Paris'})
    else: body['publishNow'] = True
    r = zreq('/posts', body); post = r.get('post', r)
    st = [x.get('status') for x in post.get('platforms', [])]
    if any(x in ('failed', 'error') for x in st): raise RuntimeError('Zernio a refusé la vidéo : ' + json.dumps(post)[:400])
    return {'id': post.get('_id'), 'mode': ('programmé dans Zernio pour ' + quand) if quand else 'publication publique (Zernio)', 'statut': post.get('status') or ','.join(map(str, st))}

if ZKEY and MODE == 'zernio_stats':
    # Statistiques des publications Zernio -> .github/social/zernio_stats.json (dépôt public : seuls des champs sûrs sont gardés)
    NUM = ('view', 'like', 'comment', 'share', 'save', 'impression', 'reach', 'play', 'engagement', 'click', 'watch', 'duration', 'follower')
    TXT = ('_id', 'id', 'status', 'platform', 'publishedAt', 'scheduledFor', 'createdAt', 'platformPostUrl', 'postUrl', 'url', 'errorMessage', 'error', 'content', 'lastUpdated', 'syncedAt')
    def tri(x, prof=0):
        if prof > 6: return None
        if isinstance(x, list): return [y for y in (tri(v, prof + 1) for v in x[:150]) if y not in (None, {}, [])]
        if not isinstance(x, dict): return None
        o = {}
        for k, v in x.items():
            kl = k.lower()
            if any(w in kl for w in ('token', 'secret', 'key', 'password', 'email', 'cookie')): continue
            if isinstance(v, (int, float)) and not isinstance(v, bool) and any(w in kl for w in NUM): o[k] = v
            elif isinstance(v, str) and k in TXT: o[k] = v[:90] if k == 'content' else v[:200]
            elif isinstance(v, (dict, list)):
                t = tri(v, prof + 1)
                if t not in (None, {}, []): o[k] = t
        return o
    out = {'genere': datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='minutes')}
    for nom, chemin in (('posts', '/posts?limit=100&page=1'), ('posts_p2', '/posts?limit=100&page=2'),
                        ('analytics', '/analytics?platform=tiktok&limit=100'), ('analytics_p2', '/analytics?platform=tiktok&limit=100&page=2')):
        try: out[nom] = tri(zreq(chemin))
        except Exception as e: out[nom + '_erreur'] = str(e)[:300]
    json.dump(out, open('.github/social/zernio_stats.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(0)

if ZKEY and MODE == 'zernio':
    try: i, a = zcompte(); etat({'zernio': 'OK', 'zernio_compte': a.get('username') or a.get('displayName') or i})
    except Exception as e: etat({'zernio': 'échec : ' + str(e)[:300]}); print('::error::' + str(e)[:400]); sys.exit(1)
    sys.exit(0)

if ZKEY and MODE in ('zernio_planifier', 'zernio_replanifier'):
    # Programme dans Zernio toutes les vidéos TikTok à venir (visibles dans le calendrier Zernio)
    plan = json.load(open(PLAN, encoding='utf-8')); done = json.load(open(DONE, encoding='utf-8')) if os.path.exists(DONE) else {}
    now = datetime.now(ZoneInfo('Europe/Paris')); n = 0; err = []
    if MODE == 'zernio_replanifier':
        # Annule d'abord dans Zernio les publications listées dans tiktok_demande.json (« annuler » : identifiants du plan)
        for pid in json.load(open('.github/social/tiktok_demande.json')).get('annuler', []):
            t = done.get(pid, {}).get('tiktok')
            if not t or not t.get('id'): continue
            try:
                zreq('/posts/' + t['id'], method='DELETE'); done[pid]['tiktok_annule'] = t; del done[pid]['tiktok']; print('annulé', pid, flush=True)
                json.dump(done, open(DONE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            except Exception as e: err.append('annulation %s : %s' % (pid, e)); print('::error::' + str(e)[:400])
    for p in sorted(plan, key=lambda x: x['date']):
        if 'tiktok' not in p.get('reseaux', []) or not p.get('video'): continue
        when = datetime.fromisoformat(p['date']).replace(tzinfo=ZoneInfo('Europe/Paris'))
        if when < now + __import__('datetime').timedelta(minutes=10): continue
        d = done.setdefault(p['id'], {})
        if d.get('tiktok'): continue
        try:
            d['tiktok'] = publier_zernio(p, p['date'][:16] + ':00'); n += 1; print('programmé', p['id'], p['date'], flush=True)
            json.dump(done, open(DONE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        except Exception as e: err.append('%s : %s' % (p['id'], e)); print('::error::' + str(e)[:400])
    etat({'zernio_programmees': n, 'zernio_erreurs': err[:5]})
    sys.exit(1 if err else 0)

if (not KEY or not SECRET) and not ZKEY:
    print('::warning::TikTok non configuré (secrets TIKTOK_CLIENT_KEY et TIKTOK_CLIENT_SECRET manquants)'); sys.exit(0)

if MODE == 'page':
    # Lien d'autorisation : il contient la clé publique de l'application (client key), jamais le secret
    url = 'https://www.tiktok.com/v2/auth/authorize/?' + urllib.parse.urlencode({'client_key': KEY, 'scope': 'user.info.basic,video.upload,video.publish',
          'response_type': 'code', 'redirect_uri': REDIRECT, 'state': secrets.token_hex(8)})
    etat({'lien_connexion': url}); print(url); sys.exit(0)

if MODE == 'jeton':
    code = os.environ.get('TIKTOK_CODE', '').strip() or (json.load(open('.github/social/tiktok_demande.json')).get('code', '') if os.path.exists('.github/social/tiktok_demande.json') else '')
    if not code: print('::error::secret TIKTOK_CODE vide'); sys.exit(1)
    try:
        tok = jetons(req(API + '/oauth/token/', {'client_key': KEY, 'client_secret': SECRET, 'code': urllib.parse.unquote(code),
                                                 'grant_type': 'authorization_code', 'redirect_uri': REDIRECT}))
        sauver(tok)
        u = req(API + '/user/info/?fields=open_id,display_name', token=tok['access_token']).get('data', {}).get('user', {})
        c = createur(tok)
        etat({'connexion': 'OK', 'compte': c.get('creator_username'), 'nom': u.get('display_name') or c.get('creator_nickname'), 'scopes': tok.get('scope'),
              'confidentialite_possible': c.get('privacy_level_options'), 'duree_video_max_s': c.get('max_video_post_duration_sec'),
              'reconnexion_avant': datetime.fromtimestamp(tok['refresh_expire'], ZoneInfo('Europe/Paris')).strftime('%d/%m/%Y')})
        print('::notice::TikTok connecté : @%s' % c.get('creator_username'))
    except Exception as e:
        etat({'connexion': 'échec : ' + str(e)[:400]}); print('::error::' + str(e)[:600]); sys.exit(1)
    sys.exit(0)

if not ZKEY:
    if not os.path.exists(ENC): print('TikTok pas encore connecté'); sys.exit(0)
    tok = acces()

def publier_video(p):
    c = createur(tok)
    priv = 'PUBLIC_TO_EVERYONE' if os.path.exists('.github/social/tiktok_public') and 'PUBLIC_TO_EVERYONE' in c.get('privacy_level_options', []) else 'SELF_ONLY'  # privé tant que l'application n'est pas validée par TikTok
    info = {'title': (p.get('texte_tiktok') or p.get('texte_instagram') or p.get('theme', ''))[:2200], 'privacy_level': priv, 'disable_comment': False, 'disable_duet': False, 'disable_stitch': False,
            'video_cover_timestamp_ms': p.get('vignette_ms', 1000), 'brand_content_toggle': False, 'brand_organic_toggle': True}
    # Envoi direct du fichier (FILE_UPLOAD) : pas de dépendance au site, un seul bloc jusqu'à 64 Mo
    f = VID + (p.get('video_tiktok') or p['video']); n = os.path.getsize(f)  # version TikTok (accroche propre, sans musique) si elle existe
    src = {'source': 'FILE_UPLOAD', 'video_size': n, 'chunk_size': n, 'total_chunk_count': 1}
    mode = 'publication directe'
    try:
        if os.path.exists('.github/social/tiktok_brouillon'): raise RuntimeError('unaudited_client (brouillon demandé)')
        r = req(API + '/post/publish/video/init/', {'post_info': info, 'source_info': src}, tok['access_token'], js=True)
    except RuntimeError as e:
        if 'unaudited_client' not in str(e): raise
        # Application pas encore validée par TikTok : la vidéo part dans la boîte de réception TikTok (brouillon à publier d'un geste)
        r = req(API + '/post/publish/inbox/video/init/', {'source_info': src}, tok['access_token'], js=True); mode = 'brouillon dans TikTok'
    pid = r['data']['publish_id']
    up = urllib.request.Request(r['data']['upload_url'], data=open(f, 'rb').read(), method='PUT',
                                headers={'Content-Type': 'video/mp4', 'Content-Length': str(n), 'Content-Range': 'bytes 0-%d/%d' % (n - 1, n)})
    try: urllib.request.urlopen(up, timeout=300).read()
    except urllib.error.HTTPError as e: raise RuntimeError('TikTok envoi vidéo %s : %s' % (e.code, e.read()[:300]))
    for _ in range(60):
        s = req(API + '/post/publish/status/fetch/', {'publish_id': pid}, tok['access_token'], js=True).get('data', {})
        if s.get('status') in ('PUBLISH_COMPLETE', 'SEND_TO_USER_INBOX'): return {'id': pid, 'mode': mode, 'statut': s.get('status')}
        if s.get('status') == 'FAILED': raise RuntimeError('TikTok a refusé la vidéo : ' + str(s.get('fail_reason')))
        time.sleep(10)
    return {'id': pid, 'mode': mode, 'statut': 'en cours'}

if MODE == 'verifier':
    c = createur(tok); etat({'connexion': 'OK', 'compte': c.get('creator_username'), 'confidentialite_possible': c.get('privacy_level_options')})
    if os.environ.get('TIKTOK_TEST'):  # essai de publication demandé
        p = next(x for x in json.load(open(PLAN, encoding='utf-8')) if x['id'] == os.environ['TIKTOK_TEST'])
        try: etat({'essai ' + p['id']: publier_video(p)})
        except Exception as e: etat({'essai ' + p['id']: 'échec : ' + str(e)[:500]})
    sys.exit(0)

def avis_brouillon(p):
    # Brouillon déposé dans TikTok : le texte à coller arrive en notification GitHub (ticket assigné au propriétaire)
    corps = ('La vidéo « %s » est dans vos brouillons TikTok (notifications TikTok, ou Profil > Brouillons).\n\n'
             '1. Ouvrez le brouillon et touchez « Sons » : choisissez un son tendance (la vidéo n\'a volontairement pas de musique).\n'
             '2. Collez le texte ci-dessous.\n3. Vérifiez « Tout le monde peut voir cette publication », puis publiez.\n\n```\n%s\n```'
             % (p.get('theme', ''), p.get('texte_tiktok') or p.get('texte_instagram', '')))
    try: subprocess.run(['gh', 'issue', 'create', '--title', 'TikTok à publier : ' + p.get('theme', '')[:80], '--assignee', os.environ.get('GITHUB_REPOSITORY', 'x/x').split('/')[0], '--body', corps], check=False, timeout=60)
    except Exception as e: print('::warning::avis brouillon non créé : %s' % e)

# Publication des contenus TikTok arrivés à échéance
plan = json.load(open(PLAN, encoding='utf-8')); done = json.load(open(DONE, encoding='utf-8')) if os.path.exists(DONE) else {}
now = datetime.now(ZoneInfo('Europe/Paris')); changed = False; errors = []
for p in plan:
    if 'tiktok' not in p.get('reseaux', []) or not p.get('video'): continue
    when = datetime.fromisoformat(p['date']).replace(tzinfo=ZoneInfo('Europe/Paris'))
    if when > now or (now - when).total_seconds() > 20 * 3600: continue
    d = done.setdefault(p['id'], {})
    if d.get('tiktok') or d.get('tiktok_echecs', 0) >= 2: continue
    try:
        d['tiktok'] = publier_zernio(p) if ZKEY else publier_video(p); changed = True
        print('::notice::%s publié sur TikTok' % p['id'])
        if 'brouillon' in d['tiktok'].get('mode', ''): avis_brouillon(p)
    except Exception as e:
        d['tiktok_echecs'] = d.get('tiktok_echecs', 0) + 1; changed = True; errors.append('%s : %s' % (p['id'], e)); print('::error::' + str(e)[:600])
if changed: json.dump(done, open(DONE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if not ZKEY and time.time() > charger()['refresh_expire'] - 15 * 86400: errors.append('La connexion TikTok expire dans moins de 15 jours : écrivez « reconnecter TikTok » à Claude dans la conversation TerrenUrbanisme.')
if errors:
    print('\n'.join(errors)); sys.exit(1)
