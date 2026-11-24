# Étude de sol préalable à la vente : rappel conditionné aux zones qui permettent une maison individuelle (art. L. 132-5 CCH)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "En zone d\\'argiles d\\'aléa moyen ou fort, le vendeur doit fournir une étude de sol préalable."
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "En zone d\\'argiles d\\'aléa moyen ou fort, le vendeur doit fournir une étude de sol préalable si les règles de la zone permettent d\\'y construire une maison individuelle (article L. 132-5 du Code de la construction et de l\\'habitation).")
open(p, 'w', encoding='utf-8').write(s); print('patch geotechnique2 appliqué')
