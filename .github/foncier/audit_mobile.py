"""Parcours complet sur téléphone, sur le site en ligne : carte d'accueil, recherche par référence, commune seule + clic sur la carte, adresse, assistant, tarifs."""
import subprocess, sys, time, json
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'playwright'], check=True)
subprocess.run([sys.executable, '-m', 'playwright', 'install', '--with-deps', 'chromium'], check=True, capture_output=True)
from playwright.sync_api import sync_playwright
D = json.load(open('.github/plu-demande.json')); attente = D.get('attente', 0); time.sleep(attente)
def largeur(p): return p.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
def refuse(p):
    for t in ('Tout refuser', 'Refuser'):
        try: p.click('text=' + t, timeout=1500); return
        except Exception: pass
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for nom, dev in (('iphone', pw.devices['iPhone 13']), ('android', pw.devices['Galaxy S9+'])):
        ctx = b.new_context(**dev); p = ctx.new_page(); err = []; p.on('pageerror', lambda e: err.append(str(e)[:150]))
        p.goto('https://terrenurbanisme.com/?n=' + str(time.time()), wait_until='networkidle'); refuse(p)
        print(nom, 'version', p.evaluate("[...document.scripts].map(s=>s.src).filter(s=>s.includes('app.js')).join()"), 'largeur', largeur(p))
        p.locator('#map').scroll_into_view_if_needed(); time.sleep(3); p.screenshot(path=f'/tmp/out/{nom}_1_accueil.png')
        # 1. référence cadastrale
        p.evaluate("window.scrollTo(0,0)"); p.click('#com'); p.keyboard.type('Lucciana', delay=60); time.sleep(2.5)
        li = p.locator('#com-ac li[role=option]'); print(nom, 'liste', li.count(), li.first.inner_text() if li.count() else '')
        if li.count(): li.first.tap()
        p.fill('#sec', 'AN'); p.fill('#num', '2007'); p.tap('#go'); time.sleep(10)
        print(nom, 'résultat', p.evaluate("(document.getElementById('result')||{}).innerText||''")[:300].replace('\n', ' / '))
        p.screenshot(path=f'/tmp/out/{nom}_2_resultat.png')
        bt = p.locator('#result button, #result a.btn').first
        if bt.count(): bb = bt.bounding_box(); print(nom, 'bouton', bt.inner_text()[:40], bb and [round(bb['x']), round(bb['width'])], 'écran', p.viewport_size['width'])
        p.evaluate("window.scrollBy(0, 500)"); time.sleep(1); p.screenshot(path=f'/tmp/out/{nom}_3_resultat_bas.png')
        print(nom, 'largeur après résultat', largeur(p))
        # 2. commune seule puis clic sur la carte
        p.goto('https://terrenurbanisme.com/?n=' + str(time.time()), wait_until='networkidle')
        p.click('#com'); p.keyboard.type('Sotta', delay=60); time.sleep(2.5)
        li = p.locator('#com-ac li[role=option]')
        if li.count(): li.first.tap()
        time.sleep(1); p.tap('#go'); time.sleep(4)
        for i in range(5):
            try: p.locator('#bigmap .leaflet-control-zoom-in').tap(timeout=3000); time.sleep(1.2)
            except Exception as e: print(nom, 'zoom', str(e)[:80]); break
        time.sleep(3); p.locator('#bigmap').scroll_into_view_if_needed(); p.screenshot(path=f'/tmp/out/{nom}_4_carte_zoom.png')
        print(nom, 'fond', p.evaluate("[...document.querySelectorAll('#bigmap .fond-ctl button')].map(b=>b.textContent+(b.classList.contains('on')?'*':'')).join()"))
        bx = p.locator('#bigmap').bounding_box(); p.mouse.click(bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2); time.sleep(10)
        print(nom, 'clic carte', p.evaluate("(document.getElementById('result')||{}).innerText||''")[:200].replace('\n', ' / '))
        p.screenshot(path=f'/tmp/out/{nom}_5_clic.png')
        # 3. adresse
        p.goto('https://terrenurbanisme.com/?n=' + str(time.time()), wait_until='networkidle')
        p.tap('#tab-adr'); p.click('#adr'); p.keyboard.type('2 cours Napoleon Ajaccio', delay=50); time.sleep(3)
        a = p.locator('#adr-list li'); print(nom, 'adresses', a.count(), a.first.inner_text()[:60] if a.count() else '')
        p.screenshot(path=f'/tmp/out/{nom}_6_adresse.png')
        # 4. assistant
        p.locator('.tu-bot-btn').tap(); time.sleep(1); p.fill('.tu-bot-f input', 'prix pour 5 rapports'); p.locator('.tu-bot-f button').tap(); time.sleep(2)
        p.screenshot(path=f'/tmp/out/{nom}_7_assistant.png')
        print(nom, 'assistant', p.evaluate("[...document.querySelectorAll('.tu-bot-m.bot p')].pop().innerText")[:160])
        # 5. tarifs
        p.goto('https://terrenurbanisme.com/tarifs.html', wait_until='networkidle'); time.sleep(1); p.screenshot(path=f'/tmp/out/{nom}_8_tarifs.png'); print(nom, 'tarifs largeur', largeur(p))
        print(nom, 'erreurs', err); ctx.close()
    b.close()
