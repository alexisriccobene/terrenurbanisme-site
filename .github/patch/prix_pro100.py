# Pack de 100 crédits professionnels : 390 € (3,90 € le rapport) au lieu de 450 €
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
s2, n = re.subn(r"(pro100\s*:\s*\{[^}]*?amount\s*:\s*)45000\b", r"\g<1>39000", s)
if n != 1:
    for m in re.finditer(r"pro100", s): print(repr(s[m.start():m.start()+120]))
    sys.exit('pro100 introuvable : %d' % n)
open(p, 'w', encoding='utf-8').write(s2); print('prix pro100 = 390 €')
