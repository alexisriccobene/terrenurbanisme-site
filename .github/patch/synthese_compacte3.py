# Synthèse : ne retirer que les points d'information secondaires (catastrophes naturelles, zone FRR, rappel du littoral), jamais un point de vigilance
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "if (d.points[i].key === 'info' || d.points[i].key === 'ok') { k = i; break; }"
assert s.count(a) == 1
s = s.replace(a, "if (/catastrophe naturelle|France Ruralités|Commune littorale|rivage est à/.test(d.points[i].text || '')) { k = i; break; }")
open(p, 'w', encoding='utf-8').write(s); print('patch synthèse compacte 3 appliqué')
