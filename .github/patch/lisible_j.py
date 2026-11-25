"""Commerces : préférence au nom commercial jusqu'à 500 m d'écart ; présentation du chapitre 10 à jour."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "if (os && os.d <= E[0].d + 150)"
if s.count(a) != 1: print('ANCRE tol'); sys.exit(1)
s = s.replace(a, "if (os && os.d <= E[0].d + 500)")
b = "ABOUT[PT] = 'Prix et loyers du secteur, énergie, copropriété, services à proximité, points à contrôler avant la vente, cadre technique, foncier et plan du terrain au format DXF.';"
if s.count(b) != 1: print('ANCRE about'); sys.exit(1)
s = s.replace(b, "ABOUT[PT] = 'Loyers du secteur, points à contrôler avant la vente, écoles et commerces avec leurs coordonnées, foncier, données techniques pour l\\'architecte et plan du terrain au format DXF.';")
open(p, 'w', encoding='utf-8').write(s); print('ok J')
s = open(p, encoding='utf-8').read()
a = "  const riskPresent = RK.naturels.filter(r => r.present || (!RK.addressLevel && /existant/i.test(r.commune)));"
if s.count(a) != 1: print('ANCRE riskPresent'); sys.exit(1)
s = s.replace(a, "  const riskPresent = RK.naturels.filter(r => r.present || (!RK.addressLevel && /existant/i.test(r.commune))).filter(r => !(r.key === 'seisme' && Number((String(RK.sismique || '').match(/\\d/) || [])[0]) === 1));")
open(p, 'w', encoding='utf-8').write(s); print('ok J2')
