# RNU : références d'articles inversées (limites séparatives = R. 111-17 ; voies = R. 111-16)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "sans être inférieure à 3 m.', 'R. 111-16'],"
b = "au moins égale à la différence d\\'altitude.', 'R. 111-17'],"
assert s.count(a) == 1 and s.count(b) == 1, (s.count(a), s.count(b))
s = s.replace(a, "sans être inférieure à 3 m.', 'R. 111-17'],").replace(b, "au moins égale à la différence d\\'altitude.', 'R. 111-16'],")
open(p, 'w', encoding='utf-8').write(s); print('patch RNU articles appliqué')
