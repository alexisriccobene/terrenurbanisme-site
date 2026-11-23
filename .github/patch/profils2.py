"""Rapport par profil, corrections après les premiers tests : services à proximité (serveurs OpenStreetMap de secours), DPE d'immeuble,
ordre du chapitre notaire, zone agricole partielle, plan DXF plus léger."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
# 1. Services à proximité : rayons resserrés, sans limite de nombre (la limite d'Overpass ne trie pas par distance), serveurs de secours
rep("""  const q = `[out:json][timeout:20];(nwr${A(3000)}["amenity"~"^(school|pharmacy|doctors|kindergarten)$"];nwr${A(3000)}["shop"~"^(supermarket|bakery|convenience)$"];nwr${A(8000)}["railway"="station"];nwr${A(1500)}["highway"="bus_stop"];);out center tags 400;`;
  const r = await fetch('https://overpass-api.de/api/interpreter', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'TerrenUrbanisme (contact@terrenurbanisme.com)' }, body: 'data=' + encodeURIComponent(q), signal: AbortSignal.timeout(22000) });
  if (!r.ok) throw new Error('overpass ' + r.status);
  const j = await r.json();""", """  const q = `[out:json][timeout:18];(nwr${A(2000)}["amenity"~"^(school|pharmacy|doctors|kindergarten)$"];nwr${A(2000)}["shop"~"^(supermarket|bakery|convenience)$"];nwr${A(8000)}["railway"="station"]["station"!="subway"];nwr${A(800)}["highway"="bus_stop"];);out tags center qt;`;
  let j = null, why = '';
  for (const ep of ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter', 'https://overpass.private.coffee/api/interpreter']) {
    try {
      const r = await fetch(ep, { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'TerrenUrbanisme (contact@terrenurbanisme.com)' }, body: 'data=' + encodeURIComponent(q), signal: AbortSignal.timeout(20000) });
      if (r.ok) { j = await r.json(); if (j && Array.isArray(j.elements)) break; }
      why += ep.split('/')[2] + ' ' + r.status + ' ; ';
    } catch (e) { why += ep.split('/')[2] + ' ' + String(e && e.message || e).slice(0, 60) + ' ; '; }
    j = null;
  }
  if (!j) throw new Error('services à proximité : ' + why);""")
rep("text('Distances à vol d\\'oiseau depuis le centre de la parcelle, dans un rayon de 1,5 km (arrêts de bus), 3 km (commerces, écoles, santé) et 8 km (gares).",
    "text('Distances à vol d\\'oiseau depuis le centre de la parcelle, dans un rayon de 800 m (arrêts de bus), 2 km (commerces, écoles, santé) et 8 km (gares).")
# 2. Loyers : fourchette sans répéter l'unité
rep("m2e(LY.mai.m2) + ' (' + m2e(LY.mai.lo) + ' à ' + m2e(LY.mai.hi) + ')'", "m2e(LY.mai.m2) + ' (fourchette ' + String(Math.round(LY.mai.lo * 10) / 10).replace('.', ',') + ' à ' + m2e(LY.mai.hi) + ')'")
rep("m2e(LY.app.m2) + ' (' + m2e(LY.app.lo) + ' à ' + m2e(LY.app.hi) + ')'", "m2e(LY.app.m2) + ' (fourchette ' + String(Math.round(LY.app.lo * 10) / 10).replace('.', ',') + ' à ' + m2e(LY.app.hi) + ')'")
# 3. DPE : sur un immeuble, chaque logement a le sien
rep("kvn([['Dernier DPE enregistré', [", "kvn([['Dernier DPE enregistré sur la parcelle', [")
rep("text((d.dpe.length - 1) + ' autre(s) DPE enregistré(s) à cette adresse : voir le chapitre « Opportunités autour du terrain » ou la base de l\\'ADEME.', { size: 9 });",
    "text((d.dpe.length - 1) + (d.dpe.length - 1 > 1 ? ' autres DPE sont enregistrés' : ' autre DPE est enregistré') + ' sur cette parcelle (base de l\\'ADEME). Dans un immeuble, chaque logement a son propre DPE : retenir celui du lot vendu.', { size: 9 });")
# 4. Notaire : points de contrôle en premier ; zone agricole partielle ; accords
i = s.index("    if (d.profil === 'notaire') {\n      h3('Points à contrôler avant l\\'acte');")
j = s.index("    if (d.profil === 'moe') {", i)
blk = s[i:j]; s = s[:i] + s[j:]
rep("    if (d.profil === 'agent' || d.profil === 'notaire') {\n      h3('Copropriété');", blk + "    if (d.profil === 'agent' || d.profil === 'notaire') {\n      h3('Copropriété');")
rep("const sup = d.sups || [], agri = (d.zones || []).some(z => /^(A|N)/i.test(String(z.code || '')));",
    "const sup = d.sups || [], zAN = (d.zones || []).filter(z => /^(A|N)/i.test(String(z.code || ''))), agri = zAN.length > 0, agriPart = agri && zAN.length < (d.zones || []).length;")
rep("agri ? 'Terrain en zone agricole ou naturelle : préemption SAFER à examiner'", "agri ? (agriPart ? 'Terrain en partie en zone agricole ou naturelle (' + zAN.map(z => z.code).join(', ') + ') : préemption SAFER à examiner' : 'Terrain en zone agricole ou naturelle : préemption SAFER à examiner')")
rep("sup.length ? sup.length + ' servitude(s) : '", "sup.length ? (sup.length > 1 ? sup.length + ' servitudes : ' : '1 servitude : ')")
rep("(RKp.catnat || []).length + ' arrêté(s) de reconnaissance dans la commune'", "(RKp.catnat || []).length + ((RKp.catnat || []).length > 1 ? ' arrêtés de reconnaissance' : ' arrêté de reconnaissance') + ' dans la commune'")
rep("P.copro.length + ' copropriété(s) immatriculée(s) sur la parcelle'", "(P.copro.length > 1 ? P.copro.length + ' copropriétés immatriculées' : '1 copropriété immatriculée') + ' sur la parcelle'")
rep("RKp.ppr.length + ' plan(s) ou atlas de risques · '", "(RKp.ppr.length > 1 ? RKp.ppr.length + ' plans ou atlas de risques · ' : '1 plan ou atlas de risques · ')")
rep("'Ce chapitre']", "'Ci-dessous']")
# 5. Plan DXF plus léger (calcul borné)
rep("const b0 = turf.bbox(turf.buffer(pf, 60, { units: 'meters' })), box", "const b0 = turf.bbox(turf.buffer(pf, 40, { units: 'meters' })), box")
rep("typeNames=BDTOPO_V3:batiment&outputFormat=application/json&count=800&bbox=${b0[1]}", "typeNames=BDTOPO_V3:batiment&outputFormat=application/json&count=300&bbox=${b0[1]}")
open(p, 'w', encoding='utf-8').write(s); print('ok profils2')
