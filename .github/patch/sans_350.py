# Dernière page du rapport : prix pro réaliste (5 € le rapport dès 50 crédits) au lieu de « dès 3,50 € »
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = 'Crédits professionnels sans abonnement dès 3,50 € le rapport'
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, 'Crédits professionnels sans abonnement, 5 € le rapport dès 50 crédits')
open(p, 'w', encoding='utf-8').write(s); print('patch sans_350 appliqué')
