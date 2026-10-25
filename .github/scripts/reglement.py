# Lecture d'un règlement de PLU trop volumineux pour une fonction Supabase :
# téléchargement, texte page par page, repérage du chapitre de la zone (par la fonction), envoi du texte utile pour analyse.
import json, os, re, subprocess, sys, urllib.request

P = json.loads(os.environ['PAYLOAD'])
print('::notice::commune=%s zone=%s doc=%s url=%s' % (P.get('commune'), P.get('zone'), P.get('doc_key'), P.get('url')))
def fail(msg):
    print('::error::' + str(msg)[:900]); sys.exit(1)
FN = 'https://nmoigruxnhsidrhqtzid.supabase.co/functions/v1/stripe-webhook'
KEY = os.environ['TU_ADMIN_KEY']
url, zone = P['url'], P['zone']
if not re.match(r'^https://data\.geopf\.fr/', url): fail('adresse refusée : ' + url)

import time, urllib.error
def post(op, body, timeout=300):
    last = None
    for k in range(3):
        req = urllib.request.Request(FN + '?regjob=' + op, data=json.dumps(body).encode(), headers={'content-type': 'application/json', 'x-tu-admin': KEY}, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read() or b'{}')
        except urllib.error.HTTPError as e:
            last = 'HTTP %s %s' % (e.code, e.read()[:300])
        except Exception as e:
            last = repr(e)
        print('essai', k + 1, op, last); time.sleep(10 * (k + 1))
    fail('appel ' + op + ' en échec : ' + str(last))

rc = subprocess.run(['curl', '-sSL', '--fail', '--retry', '3', '-A', 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)', '-o', 'r.pdf', url]).returncode
if rc: fail('téléchargement du règlement impossible (curl %d)' % rc)
print('taille', os.path.getsize('r.pdf'))
if subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', 'r.pdf', 'r.txt']).returncode: fail('PDF illisible (taille %d octets)' % os.path.getsize('r.pdf'))
pages = open('r.txt', encoding='utf-8', errors='replace').read().split('\f')
if pages and not pages[-1].strip(): pages = pages[:-1]
n = len(pages); print('pages', n)

rx = re.compile(r'(?<![A-Za-z0-9])' + re.escape(zone) + r'(?![A-Za-z0-9])')
hits = []
for i, t in enumerate(pages):
    c = len(rx.findall(t))
    if c:
        first = next((l.strip() for l in t.splitlines() if l.strip()), '')
        hits.append([i, c, first[:90]])
if len(hits) > 500:  # garde les pages les plus denses, dans l'ordre
    keep = sorted(sorted(hits, key=lambda h: -h[1])[:500], key=lambda h: h[0]); hits = keep
toc = '\n\n'.join('[Page %d]\n%s' % (i + 1, re.sub(r'[ \t]+', ' ', pages[i]).strip()) for i in range(min(n, 45)))
print('occurrences sur', len(hits), 'pages')

loc = post('locate', {'zone': zone, 'n': n, 'toc': toc[:150000], 'hits': hits})
want = [p for p in loc.get('pages') or [] if 0 <= p < n][:110]
print('pages retenues', (want[0] + 1, want[-1] + 1) if want else None)
if not want: fail('chapitre de la zone introuvable (pages %d, occurrences %d)' % (n, len(hits)))
zr = loc.get('zone')
body = {'doc_key': P['doc_key'], 'zone': zone, 'typeLabel': P.get('typeLabel', ''), 'commune': P.get('commune', ''), 'n': n, 'zoneRange': zr,
        'pages': [{'p': p, 't': re.sub(r'[ \t]+', ' ', pages[p]).strip()} for p in want]}
print(post('analyse', body))
