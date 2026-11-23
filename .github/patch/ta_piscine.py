# Taxe d'aménagement : valeur piscine affichée depuis la donnée (251 € en 2026) au lieu de 250 € écrit en dur
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "(250 € par m² de bassin pour une piscine)"
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "(' + fmt(TA.piscine) + ' € par m² de bassin pour une piscine)")
open(p, 'w', encoding='utf-8').write(s); print('patch piscine appliqué')
