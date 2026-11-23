"""Contrôle en ligne : parcelle de Lecci (sans PLU) et de Corte (PLU non publié) — texte du diagnostic."""
import subprocess, sys, time, json, requests
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'playwright'], check=True)
subprocess.run([sys.executable, '-m', 'playwright', 'install', '--with-deps', 'chromium'], check=True, capture_output=True)
from playwright.sync_api import sync_playwright
time.sleep(json.load(open('.github/plu-demande.json')).get('attente', 0))
def une_parcelle(insee):
    r = requests.get('https://apicarto.ign.fr/api/cadastre/parcelle', params={'code_insee': insee, '_limit': 50}, timeout=60).json()
    f = sorted(r['features'], key=lambda f: -f['properties'].get('contenance', 0))[10]['properties']
    return f['section'], f['numero']
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(**pw.devices['iPhone 13']); p = ctx.new_page(); err = []; p.on('pageerror', lambda e: err.append(str(e)[:150]))
    for insee, nom in (('2A139', 'Lecci'), ('2B096', 'Corte'), ('2A300', 'San-Gavino-di-Carbini')):
        s, n = une_parcelle(insee)
        p.goto('https://terrenurbanisme.com/?n=' + str(time.time()), wait_until='networkidle')
        print(nom, 'version', p.evaluate("[...document.scripts].map(s=>s.src).filter(s=>s.includes('app.js')).join()"))
        p.click('#com'); p.keyboard.type(nom, delay=50); time.sleep(2.5)
        li = p.locator('#com-ac li[role=option]')
        if li.count(): li.first.tap()
        p.fill('#sec', s); p.fill('#num', str(int(n))); p.tap('#go'); time.sleep(12)
        t = p.evaluate("(document.getElementById('result')||{}).innerText||''")
        print(nom, s, n, '::', t[:900].replace('\n', ' / '))
        p.screenshot(path=f'/tmp/out/{nom}.png', full_page=False)
    print('erreurs', err)
