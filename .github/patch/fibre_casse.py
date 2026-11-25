"""Fibre : mise en forme du nom de voie indépendamment du numéro (casse homogène)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "return clA([n, o.voie].filter(Boolean).join(' ')) || clA(o.lieu) || 'Adresse sans nom';"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
s = s.replace(a, "const v = clA(o.voie) || clA(o.lieu); return v ? (n ? n + ' ' + v : v) : 'Adresse sans nom';")
open(p, 'w', encoding='utf-8').write(s); print('ok casse')
