"""Capture du site en ligne (téléphone) : carte avec plan IGN, contour de commune, parcours sans numéro de parcelle."""
import subprocess, sys, time
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'playwright'], check=True)
subprocess.run([sys.executable, '-m', 'playwright', 'install', '--with-deps', 'chromium'], check=True, capture_output=True)
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(**pw.devices['iPhone 13']); p = ctx.new_page()
    err = []; p.on('pageerror', lambda e: err.append(str(e)))
    p.goto('https://terrenurbanisme.com/?nocache=' + str(int(time.time())), wait_until='networkidle')
    for t in ('Tout refuser', 'Refuser'):
        try: p.click('text=' + t, timeout=2000); break
        except Exception: pass
    print('v', p.evaluate("[...document.scripts].map(s=>s.src).filter(s=>s.includes('app.js')).join()"))
    print('aide', p.locator('.aide-parcelle').count(), 'boutons', p.evaluate("[...document.querySelectorAll('.fond-ctl button')].map(b=>b.textContent+(b.classList.contains('on')?'*':'')).join()"))
    p.locator('#map').scroll_into_view_if_needed(); time.sleep(3); p.screenshot(path='/tmp/out/1_accueil.png')
    p.click('#com'); p.keyboard.type('Sotta', delay=80); time.sleep(3)
    p.screenshot(path='/tmp/out/2_liste.png')
    li = p.locator('#com-ac li[role=option]')
    print('propositions', li.count(), li.first.inner_text() if li.count() else '')
    if li.count(): li.first.click()
    time.sleep(4); p.locator('#map').scroll_into_view_if_needed(); time.sleep(2); p.screenshot(path='/tmp/out/3_commune.png')
    p.click('#go'); time.sleep(6); p.screenshot(path='/tmp/out/4_carte_commune.png', full_page=False)
    print('panneau', p.evaluate("(document.getElementById('result')||{}).innerText||''")[:200])
    p.evaluate("document.getElementById('bigmap').scrollIntoView()"); time.sleep(1)
    # zoom près du terrain : bascule photo
    p.evaluate("window.scrollBy(0,-60)")
    for i in range(4):
        p.locator('#bigmap .leaflet-control-zoom-in').click(); time.sleep(1.5)
    time.sleep(3); p.screenshot(path='/tmp/out/5_zoom.png')
    print('fond', p.evaluate("[...document.querySelectorAll('#bigmap .fond-ctl button')].map(b=>b.textContent+(b.classList.contains('on')?'*':'')).join()"))
    print('erreurs', err)
    b.close()
