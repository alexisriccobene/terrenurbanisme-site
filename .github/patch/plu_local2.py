# Zonage communal (cartes PDF) : lecture du règlement de la zone, sous-titre du chapitre, verdict ESA nuancé quand le PLU classe en zone constructible
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable : ' + old[:70])
    s = s.replace(old, new)
rep("async function reglementFor(m) {", """async function zonageLocal(insee, pf) {
  try {
    const { data } = await admin.from('zonage_local').select('libelle,libelong,typezone,urlfic,datappro,geom,bbox').eq('insee', insee);
    const pb = turf.bbox(pf);
    return (data || []).filter(r => !(r.bbox[0] > pb[2] || r.bbox[2] < pb[0] || r.bbox[1] > pb[3] || r.bbox[3] < pb[1]))
      .filter(r => { try { return turf.booleanIntersects(pf, turf.feature(r.geom)); } catch (e) { return false; } })
      .map(r => ({ type: 'Feature', geometry: r.geom, properties: { libelle: r.libelle, libelong: r.libelong, typezone: r.typezone, urlfic: r.urlfic, datappro: r.datappro } }));
  } catch (e) { console.warn('zonage_local', e); return []; }
}
async function reglementFor(m) {""")
rep("""  const pf = turf.feature(parcel.geometry), total = turf.area(pf) || 1;
  const zs = (zj.features || []).map(""", """  const pf = turf.feature(parcel.geometry), total = turf.area(pf) || 1;
  const zfeat = (zj.features && zj.features.length) ? zj.features : await zonageLocal(m.insee, pf);
  const zs = zfeat.map(""")
rep("""  if (majorHits.length) { if (key === 'ok') key = 'cond'; if (majorHits.some(h => /ERC|ESA/.test(h.label)) && key !== 'non') key = 'non'; why += ' Elle est concernée par ' + majorHits.map(h => h.label.replace(/ du PADDUC| \\(.*\\)/g, '').toLowerCase()).join(' et ') + ' du PADDUC.'; }""",
"""  if (majorHits.length) {
    const erc = majorHits.some(h => /ERC/.test(h.label)), esa = majorHits.some(h => /ESA/.test(h.label));
    const zoneConstr = Z0 && !Z0.cc && (Z0.v === 'ok' || Z0.v === 'cond') && /^(U|AUC)$/i.test(String(Z0.tz || ''));
    if (key === 'ok') key = 'cond';
    if (erc && key !== 'non') key = 'non';
    else if (esa && !zoneConstr && key !== 'non') key = 'non';
    if (esa && zoneConstr && !erc) {
      why = why.replace(' Les constructions y sont admises dans le respect du règlement de la zone.', ' Le plan local d\\'urbanisme y admet les constructions dans le respect du règlement de la zone.');
      why += ' La parcelle est toutefois située, selon la cartographie du PADDUC, dans un espace stratégique agricole, où le PADDUC n\\'admet en principe que les constructions nécessaires à l\\'agriculture. Le PLU s\\'applique aux demandes de permis, mais la cartographie du PADDUC n\\'a pas une précision cadastrale et l\\'État peut contester un permis sur ce fondement : la constructibilité est à confirmer par un certificat d\\'urbanisme opérationnel avant tout engagement.';
    } else why += ' Elle est concernée par ' + majorHits.map(h => h.label.replace(/ du PADDUC| \\(.*\\)/g, '').toLowerCase()).join(' et ') + ' du PADDUC.';
  }""")
rep("""chapter(++CHN, 'Règles d\\'urbanisme applicables', 'Géoportail de l\\'Urbanisme : zonage, prescriptions et servitudes.');""",
    """chapter(++CHN, 'Règles d\\'urbanisme applicables', d.doc && d.doc.local ? 'Plan de zonage officiel de la commune, prescriptions et servitudes.' : 'Géoportail de l\\'Urbanisme : zonage, prescriptions et servitudes.');""")
open(p, 'w', encoding='utf-8').write(s); print('patch plu_local2 appliqué')
