"""Cartes des risques : titre jamais seul en bas de page, superposition plus transparente."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "if (okm.length) { h3('Les risques sur la carte');"
if s.count(a) != 1: print('ANCRE h3', s.count(a)); sys.exit(1)
s = s.replace(a, "if (okm.length) { ensure(300); h3('Les risques sur la carte');")
a = "{ img: await img(g.ov, true), opacity: 0.85 }"
if s.count(a) != 1: print('ANCRE op', s.count(a)); sys.exit(1)
s = s.replace(a, "{ img: await img(g.ov, true), opacity: 0.65 }")
open(p, 'w', encoding='utf-8').write(s); print('ok mep')
