"""Géomètres : nom du cabinet replié sur deux lignes (ne passe plus sous le bouton). Implantation : distance nulle affichée « en bordure de voie »."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(a, b, label):
    global s
    n = s.count(a)
    if n != 1: print('ANCRE', label, n); sys.exit(1)
    s = s.replace(a, b)
one("const lines = wrap(g.adresse || '', F, 8.5, CW - 190), h = 30 + lines.length * 11; ensure(h + 6);",
    "const nl = wrap(clean(g.nom), B, 10, CW - 190).slice(0, 2), lines = wrap(g.adresse || '', F, 8.5, CW - 190), h = 30 + (nl.length - 1) * 12 + lines.length * 11; ensure(h + 6);", 'h')
one("page.drawText(clean(g.nom).slice(0, 60), { x: M + 56, y: y - 16, size: 10, font: B, color: C.ink });",
    "nl.forEach((l, i) => page.drawText(l, { x: M + 56, y: y - 16 - i * 12, size: 10, font: B, color: C.ink }));", 'nom')
one("lines.forEach((l, i) => page.drawText(l, { x: M + 56, y: y - 29 - i * 11, size: 8.5, font: F, color: C.muet }));",
    "lines.forEach((l, i) => page.drawText(l, { x: M + 56, y: y - 29 - (nl.length - 1) * 12 - i * 11, size: 8.5, font: F, color: C.muet }));", 'adr')
one("['Distance à la voie', IP.dRoad != null ? 'environ ' + fmt(IP.dRoad) + ' m' : null],",
    "['Distance à la voie', IP.dRoad != null ? (IP.dRoad < 1 ? 'en bordure de voie (à l\\'alignement)' : 'environ ' + fmt(IP.dRoad) + ' m') : null],", 'voie')
open(p, 'w', encoding='utf-8').write(s); print('ok geom')
