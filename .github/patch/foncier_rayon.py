"""Foncier : le rapport retient exactement les sites comptés par l'aperçu (même règle de rayon, par maille de 0,02°)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "const d = hav(q.lat, q.lon, s.lat, s.lon); if (d > q.rayon_km) return;"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
s = s.replace(a, "const d = hav(q.lat, q.lon, s.lat, s.lon);\n    const cla = Math.round(Math.round(s.lat / 0.02) * 0.02 * 100) / 100, clo = Math.round(Math.round(s.lon / 0.02) * 0.02 * 100) / 100;\n    if (hav(q.lat, q.lon, cla, clo) > q.rayon_km) return;")
open(p, 'w', encoding='utf-8').write(s); print('ok rayon')
# Mêmes critères que l'aperçu : en « terrain ou bâtiment », un bâtiment est jugé sur sa surface bâtie, un terrain sur sa surface
s = open(p, encoding='utf-8').read()
a = """    if (q.besoin === 'terrain' && !(s.kind === 'friche' || (s.kind === 'terrain' && !s.bati))) return;
    if (q.besoin === 'batiment' && !s.bati) return;
    if (q.surface && !((s.surface || 0) >= q.surface)) return;
    if (q.bati && !((s.bati || 0) >= q.bati)) return;"""
if s.count(a) != 1: print('ANCRE criteres', s.count(a)); sys.exit(1)
s = s.replace(a, """    if (q.besoin === 'terrain') { if (s.bati || !(s.kind === 'friche' || s.kind === 'terrain')) return; if (q.surface && !((s.surface || 0) >= q.surface)) return; }
    else if (q.besoin === 'batiment') { if (!s.bati) return; if (q.bati && !(s.bati >= q.bati)) return; if (q.surface && !((s.surface || 0) >= q.surface)) return; }
    else if (s.bati) { if (q.bati && !(s.bati >= q.bati)) return; }
    else if (q.surface && !((s.surface || 0) >= q.surface)) return;""")
open(p, 'w', encoding='utf-8').write(s); print('ok criteres')
