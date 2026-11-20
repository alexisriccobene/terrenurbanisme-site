# Fibre : lecture des données préparées par commune (foncier/fibre/INSEE.json) ; si absentes hors Corse, préparation sur serveur GitHub puis attente ; pas de carte vide
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:90], s.count(a))
    s = s.replace(a, b)
a = "  const R = Math.min(800, Number(r) || 400), [X, Y] = l93(lon, lat), k = Math.cos(lat * Math.PI / 180);\n"
rep(a, a + """  // Données préparées par commune (serveur GitHub) : lecture directe, sans parcourir le fichier du département
  if (inseeTag) {
    let cache = await fibreCache(inseeTag);
    if (!cache && !/^(2A|2B|20)$/.test(String(dep))) {
      if (await dispatchFibre(inseeTag)) for (let i = 0; i < 10 && !cache; i++) { await new Promise(rs => setTimeout(rs, 10000)); cache = await fibreCache(inseeTag); }
    }
    if (cache && Array.isArray(cache.rows)) {
      const list = [];
      for (const r0 of cache.rows) {
        const x = Number(r0[0]), y = Number(r0[1]); if (!x || !y) continue;
        let ll;
        if (Math.abs(x) < 200) ll = [x, y];
        else { const m = [x / 6378137 * 180 / Math.PI, (2 * Math.atan(Math.exp(y / 6378137)) - Math.PI / 2) * 180 / Math.PI]; ll = (m[1] > 41 && m[1] < 43.5 && m[0] > 8 && m[0] < 10) ? m : l93inv(x, y); }
        const d = Math.hypot((ll[0] - lon) * 111320 * k, (ll[1] - lat) * 110574); if (d > R) continue;
        const techs = (Array.isArray(r0[7]) ? r0[7] : []).map(String).filter(Boolean);
        list.push({ lon: +ll[0].toFixed(6), lat: +ll[1].toFixed(6), d: Math.round(d), num: r0[2] || '', voie: r0[3] || '', lieu: r0[4] || '', logts: Number(r0[5]) || 0, type: r0[6] || '', techs, fibre: techs.some(isFibre) });
      }
      if (list.length) {
        list.sort((a1, b1) => a1.d - b1.d);
        const cnt = { n100: list.filter(x => x.d <= 100).length, f100: list.filter(x => x.d <= 100 && x.fibre).length, n400: list.length, f400: list.filter(x => x.fibre).length };
        return new Response(JSON.stringify({ list: list.slice(0, 60), pts: list.slice(0, 150).map(o => [o.lon, o.lat, o.fibre ? 1 : 0]), total: list.length, cnt, source: 'commune' }), { headers: { 'content-type': 'application/json' } });
      }
    }
  }
""")
a = "async function handleFibre(req) {\n"
rep(a, """async function fibreCache(insee) {
  try {
    const { data: blob } = await admin.storage.from('foncier').download('fibre/' + insee + '.json');
    if (!blob) return null;
    const j = JSON.parse(await blob.text());
    if (j && j.gen && (Date.now() - Date.parse(j.gen)) > 120 * 864e5) dispatchFibre(insee).catch(() => {});
    return j;
  } catch (e) { return null; }
}
async function dispatchFibre(insee) {
  const tok = Deno.env.get('GITHUB_TOKEN'); if (!tok) { console.warn('fibre GitHub : secret GITHUB_TOKEN absent'); return false; }
  try {
    const r = await fetch(`https://api.github.com/repos/${GH_REPO()}/dispatches`, { method: 'POST', headers: { Authorization: 'Bearer ' + tok, Accept: 'application/vnd.github+json', 'User-Agent': 'TerrenUrbanisme', 'content-type': 'application/json' }, body: JSON.stringify({ event_type: 'fibre_commune', client_payload: { insee } }) });
    if (!r.ok) { console.warn('fibre GitHub : déclenchement ' + r.status); return false; }
    return true;
  } catch (e) { console.warn('fibre GitHub', String(e && e.message || e).slice(0, 120)); return false; }
}
""" + a)
rep("        if (fimg) mapBox([{ img: fimg }], FM.bbox, { h: 300, title: 'Points fibrés autour du terrain'",
    "        if (fimg && ok && (FB.pts || []).some(p => p[2] || p[3])) mapBox([{ img: fimg }], FM.bbox, { h: 300, title: 'Points fibrés autour du terrain'")
open(p, 'w', encoding='utf-8').write(s); print('patch fibre cache appliqué')
