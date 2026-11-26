"""Foncier : rapport PDF, friches sans doublon ni code en titre, procédures limitées aux liquidations et cessions, mise en page resserrée."""
import sys, os
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
bloc = open(os.path.join(os.path.dirname(__file__), 'foncier_rapport3.ts'), encoding='utf-8').read()
a = s.index('// ---------- PDF ----------'); b = s.index('// ---------- E-mail ----------')
s = s[:a] + bloc + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('ok rapport3')
