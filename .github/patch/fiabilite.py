# Fiabilité : relance automatique des sources publiques (erreurs 5xx, 429, coupures) ; fibre : préparation GitHub en arrière-plan, sans attente
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:90], s.count(a))
    s = s.replace(a, b)
rep("""async function getJSON(url, ms = 15000, h1 = false) {
  const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), ms);
  try { const o = { headers: UA, signal: ctl.signal }; const r = await fetch(url, o); if (!r.ok) throw new Error('HTTP ' + r.status + ' ' + url.slice(0, 120)); return await r.json(); }
  finally { clearTimeout(t); }
}""", """async function getJSON(url, ms = 15000, h1 = false) {
  let last;
  for (let a = 0; a < 3; a++) {
    if (a) await new Promise(rs => setTimeout(rs, a === 1 ? 800 : 2500));
    const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), ms);
    try {
      const r = await fetch(url, { headers: UA, signal: ctl.signal });
      if (!r.ok) {
        last = new Error('HTTP ' + r.status + ' ' + url.slice(0, 120));
        try { await r.body?.cancel(); } catch (_) {}
        if (r.status >= 500 || r.status === 429) continue;
        throw last;
      }
      return await r.json();
    } catch (e) {
      last = e;
      if (/^HTTP 4/.test(String(e && e.message))) throw e;
      if (e && e.name === 'AbortError' && a >= 1) throw new Error('délai dépassé ' + url.slice(0, 120));
    } finally { clearTimeout(t); }
  }
  throw last;
}""")
rep("""    if (!cache && !/^(2A|2B|20)$/.test(String(dep))) {
      if (await dispatchFibre(inseeTag)) for (let i = 0; i < 10 && !cache; i++) { await new Promise(rs => setTimeout(rs, 10000)); cache = await fibreCache(inseeTag); }
    }""", """    if (!cache && !/^(2A|2B|20)$/.test(String(dep))) dispatchFibre(inseeTag).catch(() => {});""")
open(p, 'w', encoding='utf-8').write(s); print('patch fiabilité appliqué')
