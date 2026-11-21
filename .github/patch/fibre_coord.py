# Fibre : coordonnées Arcep en Web Mercator hors de Corse (elles étaient lues comme du Lambert 93) : on retient l'interprétation la plus proche du terrain
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "ll = (m[1] > 41 && m[1] < 43.5 && m[0] > 8 && m[0] < 10) ? m : l93inv(x, y);"
n = s.count(a); assert n == 2, n
s = s.replace(a, "const l2 = l93inv(x, y), dm = Math.hypot((m[0] - lon) * 111320 * k, (m[1] - lat) * 110574), dl = Math.hypot((l2[0] - lon) * 111320 * k, (l2[1] - lat) * 110574); ll = dm <= dl ? m : l2;")
open(p, 'w', encoding='utf-8').write(s); print('patch fibre coordonnées appliqué', n)
