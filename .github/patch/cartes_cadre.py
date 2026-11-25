"""Cartes des risques : cadrage adapté aux grandes parcelles."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "const rb = frameC(487 / 190, 0.011);"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
s = s.replace(a, "const rb = frameC(487 / 190, Math.max(0.011, I.bbox ? (I.bbox[3] - I.bbox[1]) * 0.9 : 0));")
open(p, 'w', encoding='utf-8').write(s); print('ok cadre')
