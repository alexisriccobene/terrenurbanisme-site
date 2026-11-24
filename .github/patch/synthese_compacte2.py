# Synthèse : si les points d'attention ne tiennent pas sur la page même resserrés, on retire d'abord les points d'information
# (catastrophes naturelles, zone FRR, rappel du littoral...), qui restent détaillés dans leurs chapitres
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "    const PT0 = d.points.map(pt => pt.text), szP = (y - hb(PT0, 10) < 72 && y - hb(PT0, 8.8) >= 72) ? 8.8 : 10;"
assert s.count(a) == 1
s = s.replace(a, """    { let guard = 0; while (y - hb(d.points.map(pt => pt.text), 8.8) < 72 && guard++ < 12) { let k = -1; for (let i = d.points.length - 1; i >= 0; i--) if (d.points[i].key === 'info' || d.points[i].key === 'ok') { k = i; break; } if (k < 0) break; d.points.splice(k, 1); } }
    const PT0 = d.points.map(pt => pt.text), szP = (y - hb(PT0, 10) < 72 && y - hb(PT0, 8.8) >= 72) ? 8.8 : 10;""")
open(p, 'w', encoding='utf-8').write(s); print('patch synthèse compacte 2 appliqué')
