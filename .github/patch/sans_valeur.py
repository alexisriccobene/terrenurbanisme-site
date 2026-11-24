# Retrait du chapitre « Valeur de marché » (fourchette calculée jugée non fiable) ; l'avis de valeur de l'agence reste possible
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "    if (VS.surf && !VS.none) {"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, "    if (false && VS.surf && !VS.none) {")
open(p, 'w', encoding='utf-8').write(s); print('patch sans_valeur appliqué')
