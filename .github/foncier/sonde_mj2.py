# Sonde 2 : pages mandataires des cours d'appel via le plan du site (sitemap)
import requests, re, html, os
H = {'User-Agent': 'Mozilla/5.0 (TerrenUrbanisme; contact@terrenurbanisme.com)'}
B = 'https://www.cours-appel.justice.fr'
os.makedirs('/tmp/out/mj', exist_ok=True)
urls = set()
for p in range(1, 40):
    try:
        r = requests.get(f'{B}/sitemap.xml?page={p}', headers=H, timeout=40)
    except Exception as e:
        print('sitemap err', p, e); break
    l = re.findall(r'<loc>([^<]+)</loc>', r.text)
    print('sitemap', p, r.status_code, len(l), flush=True)
    if not l: break
    new = set(l) - urls
    if not new: break
    urls |= new
sub = [u for u in urls if 'sitemap' in u or u.endswith('.xml')]
print('sous-plans', len(sub), sub[:5])
for sm in sub:
    try:
        for q in range(1, 30):
            r = requests.get(sm + (('&' if '?' in sm else '?') + f'page={q}' if q > 1 else ''), headers=H, timeout=40)
            l = re.findall(r'<loc>([^<]+)</loc>', r.text)
            new = set(l) - urls
            if not new: break
            urls |= new
    except Exception as e: print('err', sm, e)
print('total urls', len(urls), flush=True)
CA = ['agen','aix-en-provence','amiens','angers','bastia','besancon','bordeaux','bourges','caen','chambery','colmar','dijon','douai','grenoble','limoges','lyon','metz','montpellier','nancy','nimes','orleans','paris','pau','poitiers','reims','rennes','riom','rouen','toulouse','versailles','basse-terre','fort-de-france','cayenne','saint-denis-de-la-reunion']
SL = ['les-mandataires-judiciaires','les-administrateurs-et-mandataires-judiciaires','les-administrateurs-et-mandataires-judiciaires-droit-commercial','administrateurs-et-mandataires-judiciaires','mandataires-judiciaires','liste-des-mandataires-judiciaires','les-mandataires-judiciaires-droit-commercial']
for ca in CA:
    for sl in SL:
        u = f'{B}/{ca}/{sl}'
        try:
            r = requests.get(u, headers=H, timeout=30, allow_redirects=True)
            if r.status_code == 200: urls.add(r.url); print('ok', r.url, flush=True)
        except Exception: pass
mj = sorted(u for u in urls if re.search(r'mandataire|administrateur', u, re.I))
print('pages mandataires', len(mj))
for u in mj: print(' ', u)
for u in mj:
    try:
        t = requests.get(u, headers=H, timeout=40).text
        m = re.search(r'<main.*?</main>', t, re.S)
        tx = html.unescape(re.sub(r'<[^>]+>', '\n', m.group(0) if m else t))
        tx = re.sub(r'\n\s*\n+', '\n', tx)
        f = re.sub(r'\W+', '_', u.replace(B, ''))[:120]
        open(f'/tmp/out/mj/{f}.txt', 'w').write(u + '\n' + tx)
        print(u, len(tx), 'tel', len(re.findall(r'0\d(?:[\s.]?\d\d){4}', tx)), 'mail', len(re.findall(r'[\w.-]+@[\w-]+\.\w+', tx)), flush=True)
    except Exception as e:
        print('ERR', u, e)
