# PADDUC : intersection exacte avec la parcelle (filtre CQL INTERSECTS, coordonnées WGS84), au lieu du filtre bbox approximatif du serveur
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index("  const hitsOf = async (id, b) => {")
b = s.index("  await Promise.all(PADDUC_LAYERS.map(async ([id, label, explain, major]) => {", a)
NEW = r"""  const wktP = (wkt && wkt.length < 1800) ? wkt : 'POLYGON((' + bb0[0] + ' ' + bb0[1] + ', ' + bb0[2] + ' ' + bb0[1] + ', ' + bb0[2] + ' ' + bb0[3] + ', ' + bb0[0] + ' ' + bb0[3] + ', ' + bb0[0] + ' ' + bb0[1] + '))';
  const hitsOf = async (id, geomWkt) => {
    const t = await (await fetch(WFS + id + '&CQL_FILTER=' + encodeURIComponent('INTERSECTS(geom,SRID=4326;' + geomWkt + ')'), { signal: AbortSignal.timeout(15000) })).text();
    const m = t.match(/numberMatched="(\d+)"/); if (!m) throw new Error('wfs'); return Number(m[1]);
  };
"""
s = s[:a] + NEW + s[b:]
for old, new in [("const n = await hitsOf(id, bb0);", "const n = await hitsOf(id, wktP);"),
                 ("try { share = (await hitsOf(id, [ct[0] - e, ct[1] - e, ct[0] + e, ct[1] + e])) > 0 ? 0.6 : 0.2; }", "try { share = (await hitsOf(id, 'POINT(' + ct[0] + ' ' + ct[1] + ')')) > 0 ? 0.6 : 0.2; }"),
                 ("'Oui, au moins en majeure partie'", "'Oui, centre de la parcelle compris'")]:
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + old[:40])
    s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s); print('patch padduc2 appliqué')
