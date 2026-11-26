# Grille particuliers rétablie (26/11/2026) : 19,90 / 29,80 / 38,70 (les ventes s'étaient arrêtées à 29,90). Pros inchangés.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
R = [("unit: { mode: 'payment', amount: 2990,", "unit: { mode: 'payment', amount: 1990,"),
     ("pack2: { mode: 'payment', amount: 4980,", "pack2: { mode: 'payment', amount: 2980,"),
     ("pack3: { mode: 'payment', amount: 5970,", "pack3: { mode: 'payment', amount: 3870,")]
for a, b in R:
    if s.count(a) != 1: print('ANCRE', a); sys.exit(1)
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('grille particuliers 19,90 rétablie')
