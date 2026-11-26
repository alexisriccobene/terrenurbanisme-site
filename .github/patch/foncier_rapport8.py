"""Foncier : page méthode resserrée (plus de page presque vide)."""
import sys, os
d = os.path.dirname(__file__)
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
b = s.index('// ---------- PDF ----------'); c = s.index('// ---------- E-mail ----------')
s = s[:b] + open(os.path.join(d, 'foncier_rapport8.ts'), encoding='utf-8').read() + '\n' + s[c:]
open(p, 'w', encoding='utf-8').write(s); print('ok rapport8')
