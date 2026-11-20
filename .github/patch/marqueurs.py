# Cartes : un repère ne dépasse plus le cadre en haut
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "if (px < x + 6 || px > x + mw - 6 || py < bottom + 6 || py > top - 14) continue;"
assert s.count(a) == 1
s = s.replace(a, "if (px < x + 8 || px > x + mw - 8 || py < bottom + 6 || py > top - 24) continue;")
open(p, 'w', encoding='utf-8').write(s); print('patch marqueurs appliqué')
