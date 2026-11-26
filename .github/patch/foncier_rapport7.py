"""Foncier : note de contrôle déplacée dans la partie détail (synthèse sur une page), contrôle des terrains plus long sur le serveur GitHub."""
import sys, os
d = os.path.dirname(__file__)
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
b = s.index('// ---------- PDF ----------'); c = s.index('// ---------- E-mail ----------')
s = s[:b] + open(os.path.join(d, 'foncier_rapport7.ts'), encoding='utf-8').read() + '\n' + s[c:]
o = "budget = Deno.env.get('TU_LOCAL') ? 420000 : 45000, cible = 420;"
if s.count(o) != 1: print('ANCRE budget'); sys.exit(1)
s = s.replace(o, "budget = Deno.env.get('TU_LOCAL') ? 780000 : 45000, cible = 600;")
open(p, 'w', encoding='utf-8').write(s); print('ok rapport7')
