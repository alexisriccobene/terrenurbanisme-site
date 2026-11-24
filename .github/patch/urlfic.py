# Règlement : le lien de la collectivité suivi d'une ancre de page (#page=80) est désormais utilisé
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "p.urlfic && /\\.pdf($|\\?)/i.test(p.urlfic) ? p.urlfic : ''"
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "p.urlfic && /\\.pdf($|\\?|#)/i.test(p.urlfic) ? p.urlfic.split('#')[0] : ''")
open(p, 'w', encoding='utf-8').write(s); print('patch urlfic appliqué')
