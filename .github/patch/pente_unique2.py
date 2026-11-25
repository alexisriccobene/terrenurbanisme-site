"""Pente : même valeur et même appréciation partout (pente moyenne et classe du chapitre « relief »)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', c, a[:90]); sys.exit(1)
    s = s.replace(a, b)
rep("['Altitude et pente', d.alti ? fmt(d.alti.min) + ' à ' + fmt(d.alti.max) + ' m · pente estimée ' + d.alti.slope + ' %' : null],",
    "['Altitude et pente', d.alti ? fmt(d.alti.min) + ' à ' + fmt(d.alti.max) + ' m · pente moyenne ' + (d.relief && d.relief.slope != null ? d.relief.slope : d.alti.slope) + ' %' : null],")
rep("return ['Pente moyenne', sl != null ? sl + ' %' + (sl >= 15 ? ' (terrain en pente marquée)' : sl >= 5 ? ' (pente modérée)' : ' (terrain plutôt plat)') : null];",
    "return ['Pente moyenne', sl != null ? sl + ' %' + (d.relief && d.relief.cls ? ' (' + String(d.relief.cls[0]).toLowerCase() + ')' : sl >= 30 ? ' (forte pente)' : sl >= 15 ? ' (pente marquée)' : sl >= 5 ? ' (pente modérée)' : ' (terrain plutôt plat)') : null];")
rep("if (sl != null && sl >= 15) pts.push({ key: 'info', text: 'Terrain en pente marquée (pente moyenne d\\'environ ' + sl + ' %) : surcoût probable de terrassement.' }); }",
    "if (sl != null && sl >= 15) pts.push({ key: 'info', text: (sl >= 30 ? 'Terrain en forte pente' : 'Terrain en pente marquée') + ' (pente moyenne d\\'environ ' + sl + ' %) : ' + (sl >= 30 ? 'fondations et soutènements importants, étude géotechnique indispensable.' : 'surcoût probable de terrassement.') }); }")
open(p, 'w', encoding='utf-8').write(s); print('ok')
