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
