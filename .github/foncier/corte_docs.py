"""Liste les documents téléchargeables du PLU de Corte (mairie-corte.fr, module Downloads) autour des numéros connus."""
import requests, re, os
os.makedirs('/tmp/out', exist_ok=True)
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0'
for lid in range(1440, 1520):
    u = 'https://www.mairie-corte.fr/modules.php?name=Downloads&d_op=getit&lid=%d' % lid
    try:
        r = S.get(u, timeout=60, stream=True, allow_redirects=True)
        cd = r.headers.get('content-disposition', ''); ct = r.headers.get('content-type', ''); n = r.headers.get('content-length', '?')
        print(lid, r.status_code, ct[:30], n, cd[:120], r.url[-90:]); r.close()
    except Exception as e: print(lid, 'erreur', str(e)[:80])
for q in ['https://www.mairie-corte.fr/modules.php?name=Downloads', 'https://www.mairie-corte.fr/modules.php?name=Downloads&d_op=viewdownload&cid=1']:
    try:
        t = S.get(q, timeout=60).text
        for m in re.finditer(r'lid=(\d+)[^>]*>([^<]{3,120})<', t): print('PAGE', m.group(1), m.group(2).strip())
        for m in re.finditer(r'cid=(\d+)[^>]*>([^<]{3,120})<', t): print('CAT', m.group(1), m.group(2).strip())
    except Exception as e: print('page erreur', e)
