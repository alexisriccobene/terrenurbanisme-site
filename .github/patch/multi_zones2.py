# Titre du verdict plus court (une ligne) pour les terrains à cheval sur plusieurs zones
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "'Constructible sous conditions : seule la partie en zone ' + partiel.map(z => z.code).join(' ou ') + ' peut accueillir une construction'"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, "'Constructible uniquement sur la partie en zone ' + partiel.map(z => z.code).join(' ou ')")
open(p, 'w', encoding='utf-8').write(s); print('patch multi_zones2 appliqué')
