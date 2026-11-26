"""Foncier : téléphone et e-mail des liquidateurs (annuaire officiel, implantation locale de l'étude)."""
import sys, os
d = os.path.dirname(__file__)
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index('// ---------- Secteur'); c = s.index('// ---------- E-mail ----------')
s = s[:a] + open(os.path.join(d, 'foncier_rapport6_secteur.ts'), encoding='utf-8').read() + open(os.path.join(d, 'foncier_rapport6.ts'), encoding='utf-8').read() + '\n' + s[c:]
open(p, 'w', encoding='utf-8').write(s); print('ok rapport6')
