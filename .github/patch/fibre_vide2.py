# Fibre : sur la carte, seulement les adresses à moins de 400 m (pas de carte sans repère)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "pts: list.slice(0, 150).map(o => [o.lon, o.lat, o.fibre ? 1 : 0]), total: list.length, cnt, source: 'commune'"
assert s.count(a) == 1
s = s.replace(a, "pts: inR.slice(0, 150).map(o => [o.lon, o.lat, o.fibre ? 1 : 0]), total: inR.length, cnt, source: 'commune'")
open(p, 'w', encoding='utf-8').write(s); print('patch fibre vide 2 appliqué')
