"""Terrain à cheval sur plusieurs zones : potentiel (emprise, plancher, implantation) calculé sur la seule partie située dans la zone principale."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', c, a[:90]); sys.exit(1)
    s = s.replace(a, b)
rep("  const zoneShapes = zsrc.map(z => {",
"""  let mainZoneGeom = null;
  try {
    if (zones.length > 1 && zones[0].share < 0.97 && zf.length) {
      const k0 = String(zones[0].code || '?').toUpperCase();
      for (const z of zf) {
        if (String(zlib(z.properties || {}) || '?').toUpperCase() !== k0 || !z.geometry) continue;
        const it = turf.intersect(pf, turf.feature(z.geometry));
        if (it) mainZoneGeom = mainZoneGeom ? (turf.union(mainZoneGeom, it) || mainZoneGeom) : it;
      }
      if (mainZoneGeom && turf.area(mainZoneGeom) < 20) mainZoneGeom = null;
    }
  } catch (e) { mainZoneGeom = null; }
  const zoneShapes = zsrc.map(z => {""")
rep("    props, zones, zoneShapes, prescriptions,", "    props, zones, zoneShapes, mainZoneGeom, prescriptions,")
rep("      d.calc = computeBuildable(c.parcelGeom, ch, c.acces, d.ref.contenance || d.ref.areaCalc);",
"""      const MZ = c.mainZoneGeom && c.mainZoneGeom.geometry ? c.mainZoneGeom : null;
      d.calc = computeBuildable(MZ ? MZ.geometry : c.parcelGeom, ch, c.acces, MZ ? Math.round(turf.area(MZ)) : (d.ref.contenance || d.ref.areaCalc));
      if (d.calc && MZ) { d.calc.partZone = String((d.zones && d.zones[0] && d.zones[0].code) || ''); d.calc.partArea = Math.round(turf.area(MZ)); }""")
rep("['Emprise au sol maximale', K.empPct != null ? K.empPct + ' % du terrain, soit ' + fmt(K.empMax) + ' m²' : 'Non fixée par le règlement'],",
    "['Emprise au sol maximale', K.empPct != null ? K.empPct + (K.partArea ? ' % de la partie en zone ' + K.partZone + ' (' + fmt(K.partArea) + ' m²)' : ' % du terrain') + ', soit ' + fmt(K.empMax) + ' m²' : 'Non fixée par le règlement'],")
open(p, 'w', encoding='utf-8').write(s); print('ok')
s = open(p, encoding='utf-8').read()
def rep2(a, b):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE2', c, a[:90]); sys.exit(1)
    s = s.replace(a, b)
# « sur ce terrain » -> « sur la partie en zone X » quand le terrain est à cheval
rep2("note('En clair : le règlement autorise au maximum ' + fmt(K.footprint) + ' m² de construction au sol sur ce terrain (emprise de ' + K.empPct + ' %)'",
     "note('En clair : le règlement autorise au maximum ' + fmt(K.footprint) + ' m² de construction au sol ' + (K.partArea ? 'sur la partie du terrain en zone ' + K.partZone : 'sur ce terrain') + ' (emprise de ' + K.empPct + ' %)'")
# Points d'attention : minuscule après les deux-points
rep2("majorHits.forEach(h => pts.push({ key: 'non', text: h.label + ' : ' + h.explain }));",
     "majorHits.forEach(h => pts.push({ key: 'non', text: h.label + ' : ' + String(h.explain || '').replace(/^Les /, 'les ') }));")
# Libellés longs de zone : coquille répétée du Géoportail (« périphériphérique »)
rep2("function zlong(p) { return String((p && p.libelong) || '')", "function zlong(p) { return String((p && p.libelong) || '').replace(/(phéri)(?:phéri)+/gi, '$1')")
# Points de vigilance : on retire ceux qui ne font que répéter les règles déjà présentées
rep2("if (A.points_vigilance && A.points_vigilance.length) { h3(ZP('Points de vigilance pour votre projet')); A.points_vigilance.forEach(t => bullet(t, { size: 9.5, color: C.cond })); }",
     "if (A.points_vigilance && A.points_vigilance.length) { const W = t => String(t || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').match(/[a-z0-9]{5,}/g) || []; const base = new Set(W(JSON.stringify({ ...A, points_vigilance: null }))); const PV = A.points_vigilance.filter(t => { const w = W(t).filter(x => !/^(verifier|parcelle|terrain|projet|possible|eventuel\\w*)$/.test(x)); if (!w.length) return false; return w.filter(x => base.has(x)).length / w.length < 0.75; }); if (PV.length) { h3(ZP('Points de vigilance pour votre projet')); PV.forEach(t => bullet(t, { size: 9.5, color: C.cond })); } }")
open(p, 'w', encoding='utf-8').write(s); print('ok2')
