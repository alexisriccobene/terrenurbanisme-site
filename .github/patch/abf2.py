# Titres ABF sur une ligne ; zonage relu (nouvel essai, puis au centre de la parcelle) quand le Géoportail ne répond pas
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("abf === 'sur' && key === 'cond' ? 'Constructible sous conditions : accord de l\\'architecte des Bâtiments de France' : abf === 'probable' && key === 'cond' ? 'Constructible sous conditions : avis de l\\'architecte des Bâtiments de France probable'",
    "abf === 'sur' && key === 'cond' ? 'Accord de l\\'architecte des Bâtiments de France obligatoire' : abf === 'probable' && key === 'cond' ? 'Avis de l\\'architecte des Bâtiments de France probable'")
rep("  const [zj, mj, dj, pscS, pscL, pscP, infS, infL, infP, supS, supL, supP, ccj, nbj, divj] = await Promise.all([",
    "  let [zj, mj, dj, pscS, pscL, pscP, infS, infL, infP, supS, supL, supP, ccj, nbj, divj] = await Promise.all([")
rep("  const natureKeys = Object.keys(NATURE);\n",
    """  // Document publié mais zonage vide : réponse incomplète du Géoportail, on relit (parcelle puis centre de la parcelle)
  if (!(zj.features || []).length && (dj.features || []).some(f => /PLU|POS|PSMV/i.test(String((f.properties || {}).du_type || '')))) {
    for (const gg of [g, pt, g]) { const r2 = await safe(gq('/gpu/zone-urba', gg), E); if ((r2.features || []).length) { zj = r2; console.log('zonage relu au second essai'); break; } await new Promise(r => setTimeout(r, 1500)); }
  }
  const natureKeys = Object.keys(NATURE);
""")
rep("  const zj = await getJSON(`${CARTO}/gpu/zone-urba?geom=${encodeURIComponent(JSON.stringify(g))}`);\n  const pf = turf.feature(parcel.geometry), total = turf.area(pf) || 1;",
    """  let zj = await safe(retry(() => getJSON(`${CARTO}/gpu/zone-urba?geom=${encodeURIComponent(JSON.stringify(g))}`), 2), { features: [] });
  if (!(zj.features || []).length) { const c0 = turf.centroid(turf.feature(parcel.geometry)).geometry; zj = await safe(getJSON(`${CARTO}/gpu/zone-urba?geom=${encodeURIComponent(JSON.stringify(c0))}`), { features: [] }); }
  const pf = turf.feature(parcel.geometry), total = turf.area(pf) || 1;""")
rep("steps.push(['Architecte des Bâtiments de France', 'Le projet sera soumis à l\\'avis de l\\'architecte des Bâtiments de France : prévoir un projet soigné et un délai d\\'instruction majoré.']);",
    "steps.push(['Architecte des Bâtiments de France', 'Le projet sera soumis à l\\'architecte des Bâtiments de France : le rencontrer avant de dessiner le projet (rendez-vous par la mairie ou l\\'unité départementale de l\\'architecture et du patrimoine), soigner matériaux, teintes et toitures, et compter un mois de plus pour l\\'instruction.']);")
open(p, 'w', encoding='utf-8').write(s); print('patch abf2 appliqué')
