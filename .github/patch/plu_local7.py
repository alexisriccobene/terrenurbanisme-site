# Zonages communaux : pas d'annexe recopiée du règlement communal (le lien officiel suffit ; évite le dépassement de calcul)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "      try { res = await analyseReglement(zone, u, commune, main); }"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, "      try { res = await analyseReglement(zone, u, commune, main && !p.copie); }")
open(p, 'w', encoding='utf-8').write(s); print('patch plu_local7 appliqué')
