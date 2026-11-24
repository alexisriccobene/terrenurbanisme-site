"""Ventes : uniquement le rayon de 500 m (chapitre « Prix de vente autour du terrain ») ; le tableau élargi « Ventes de terrains autour de la parcelle » n'apparaît plus qu'en l'absence de ce chapitre."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "  if (DV && DV.sales && DV.sales.length && !AGRI) {\n    ensure(140); h3('Ventes de terrains autour de la parcelle');"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
s = s.replace(a, "  if (DV && DV.sales && DV.sales.length && !AGRI && !MK) {\n    ensure(140); h3('Ventes de terrains autour de la parcelle');")
open(p, 'w', encoding='utf-8').write(s); print('ok')
