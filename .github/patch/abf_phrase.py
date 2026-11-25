"""Verdict ABF : une seule ponctuation forte dans la phrase."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
for a, b in [("'d\\'après le relief, le terrain est visible depuis le monument : l\\'accord de l\\'architecte des Bâtiments de France est à prévoir, avec des prescriptions possibles (matériaux, couleurs, volumes).'", "'le relief n\\'empêche pas de voir le terrain depuis le monument, l\\'accord de l\\'architecte des Bâtiments de France est donc à prévoir, avec des prescriptions possibles (matériaux, couleurs, volumes).'"),
             ("'d\\'après le relief, le terrain n\\'est pas visible depuis le monument : l\\'architecte des Bâtiments de France devrait rendre un avis simple, sauf si le terrain et le monument se voient ensemble depuis un autre point.'", "'le relief masque le terrain depuis le monument, l\\'architecte des Bâtiments de France devrait donc rendre un avis simple, sauf si le terrain et le monument se voient ensemble depuis un autre point.'")]:
    if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok')
