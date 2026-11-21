# FRR : garder ensemble les mentions finales (exclusions, réserve, source)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "        text('Exclus : les activités agricoles,"
assert s.count(a) == 1
s = s.replace(a, "        ensure(100);\n" + a)
open(p, 'w', encoding='utf-8').write(s); print('patch zfrr2 appliqué')
