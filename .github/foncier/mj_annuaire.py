# Annuaire officiel CNAJMJ (robots.txt : tout autorisé) : coordonnées professionnelles publiques des mandataires et administrateurs judiciaires.
# Lecture polie : agent identifié, une page par seconde, liste des profils tirée du plan du site.
import requests, re, html, json, time
S = requests.Session()
S.headers.update({'User-Agent': 'TerrenUrbanismeBot/1.0 (+https://terrenurbanisme.com; contact@terrenurbanisme.com)'})
def get(u):
    for t in range(3):
        try:
            r = S.get(u, timeout=40)
            if r.status_code == 200: return r.text
            print('http', r.status_code, u, flush=True)
            if r.status_code in (403, 429): time.sleep(10)
        except Exception as e:
            print('err', u, e, flush=True)
        time.sleep(3)
    return ''
idx = get('https://www.cnajmj.fr/sitemap_index.xml')
sms = re.findall(r'<loc>([^<]+)</loc>', idx)
print('plans', len(sms), [s for s in sms if 'ajmj' in s], flush=True)
links = []
for sm in sms:
    if 'ajmj' not in sm: continue
    links += re.findall(r'<loc>(https://www\.cnajmj\.fr/ajmj/[^<]+)</loc>', get(sm))
links = sorted(set(links))
print('profils', len(links), flush=True)
out = []
for i, u in enumerate(links):
    t = get(u)
    if not t: continue
    m = re.search(r'<main.*?</main>', t, re.S) or re.search(r'<body.*?</body>', t, re.S)
    raw = re.sub(r'<(script|style|nav|footer|header).*?</\1>', '', m.group(0) if m else t, flags=re.S)
    tx = html.unescape(re.sub(r'<[^>]+>', '\n', raw))
    tx = re.sub(r'[ \t\xa0]+', ' ', re.sub(r'\n\s*\n+', '\n', tx)).strip()
    mails = sorted(set(x.lower() for x in re.findall(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', tx) if 'cnajmj' not in x.lower()))
    hrefs = [h for h in re.findall(r'href="(https?://[^"]+)"', raw) if not re.search(r'cnajmj|facebook|linkedin|twitter|instagram|youtube|google|wordpress|w\.org|maps\.', h)]
    tels = list(dict.fromkeys(re.sub(r'\D', '', x)[-9:] for x in re.findall(r'(?:\+33\s?(?:\(0\)\s?)?|0)[1-9](?:[\s.-]?\d\d){4}', tx)))
    out.append({'url': u, 'tels': tels[:3], 'mails': mails[:4], 'sites': list(dict.fromkeys(hrefs))[:3], 'texte': tx[:1800]})
    if i < 2: print(json.dumps(out[-1], ensure_ascii=False)[:2000], flush=True)
    if i % 100 == 0: print('...', i, flush=True)
    time.sleep(1)
json.dump(out, open('/tmp/out/mj.json', 'w'), ensure_ascii=False)
print('fini', len(out), 'tel', sum(1 for o in out if o['tels']), 'mail', sum(1 for o in out if o['mails']), 'site', sum(1 for o in out if o['sites']))
