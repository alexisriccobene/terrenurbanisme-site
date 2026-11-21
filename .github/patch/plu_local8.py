# Extrait du plan officiel : transmettre les tuiles au rapport (assemble)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "zortho: c.images.zortho, zbbox: c.images.zbbox }"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, "zortho: c.images.zortho, zbbox: c.images.zbbox, pluTiles: c.images.pluTiles, pbox: c.images.pbox }")
open(p, 'w', encoding='utf-8').write(s); print('patch plu_local8 appliqué')
