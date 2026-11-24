# Accès à la voie : distance mesurée aussi depuis les points de la route jusqu'aux bords de la parcelle (et pas seulement depuis les sommets de la parcelle),
# et marge de 5 m au-delà de la demi-chaussée (trottoir, stationnement)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a)); s = s.replace(a, b)
rep("""    try { if (turf.booleanIntersects(pf, f)) d = 0; } catch (e) {}
    const pr = f.properties || {};""", """    try { if (turf.booleanIntersects(pf, f)) d = 0; } catch (e) {}
    if (d > 0 && d < 60) { try { const bl = turf.polygonToLine(pf); const LS = bl.type === 'FeatureCollection' ? bl.features : [bl]; const RC = f.geometry.type === 'MultiLineString' ? f.geometry.coordinates.flat(1) : f.geometry.coordinates; for (const c of RC) for (const L0 of LS) { const x = turf.pointToLineDistance(turf.point(c), L0, { units: 'meters' }); if (x < d) d = x; } } catch (e) {} }
    const pr = f.properties || {};""")
rep("const contact = carro.filter(x => x.d <= (x.largeur ? x.largeur / 2 : 2.5) + 3.5);", "const contact = carro.filter(x => x.d <= (x.largeur ? x.largeur / 2 : 2.5) + 5);")
open(p, 'w', encoding='utf-8').write(s); print('patch accès appliqué')
