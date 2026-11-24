"""OSM : délais plus longs et journalisation."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "try { x = await fetch(host + '?data=' + encodeURIComponent(q), { headers: { 'User-Agent': 'TerrenUrbanisme/1.0' }, signal: AbortSignal.timeout(12000) }); if (x.ok) break; } catch (e) { x = null; }"
if s.count(a) != 1: print('ANCRE fetch', s.count(a)); sys.exit(1)
s = s.replace(a, "const t1 = Date.now(); try { x = await fetch(host + '?data=' + encodeURIComponent(q), { headers: { 'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)' }, signal: AbortSignal.timeout(20000) }); console.log('OSM', host, x.status, Date.now() - t1, 'ms'); if (x.ok) break; } catch (e) { console.warn('OSM', host, String(e && e.message || e).slice(0, 60), Date.now() - t1, 'ms'); x = null; }")
b = "const OSM = await Promise.race([osmP, new Promise(z => setTimeout(() => z(null), 8000))]);"
if s.count(b) != 1: print('ANCRE race'); sys.exit(1)
s = s.replace(b, "const OSM = await Promise.race([osmP, new Promise(z => setTimeout(() => z(null), 22000))]);")
open(p, 'w', encoding='utf-8').write(s); print('ok H')
