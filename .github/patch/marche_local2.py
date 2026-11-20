# Distances des ventes en mètres (le voisinage est désormais à moins de 1 km)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "    const dk = v => (v / 1000).toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' km';"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, "    const dk = v => v < 1000 ? (v < 50 ? '< 50 m' : Math.round(v / 10) * 10 + ' m') : (v / 1000).toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' km';")
open(p, 'w', encoding='utf-8').write(s); print('patch marche_local2 appliqué')
