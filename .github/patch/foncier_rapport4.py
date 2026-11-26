"""Foncier : rapport recentré (terrains vides, hangars vides, biens de sociétés en liquidation), avis et explications par site,
fiches des sociétés (siège, dirigeants), liquidateurs, marche à suivre pour racheter un bien en liquidation."""
import sys, os
d = os.path.dirname(__file__)
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index('// ---------- Secteur'); b = s.index('// ---------- PDF ----------'); c = s.index('// ---------- E-mail ----------')
s = s[:a] + open(os.path.join(d, 'foncier_rapport4_secteur.ts'), encoding='utf-8').read() + open(os.path.join(d, 'foncier_rapport4.ts'), encoding='utf-8').read() + '\n' + s[c:]
old = "    if (s.v >= 2 && !s.dispo) return;"
if s.count(old) != 1: print('ANCRE keep'); sys.exit(1)
s = s.replace(old, old + "\n    if (s.kind === 'friche' || /^\\s*(1|5|9)\\b/.test(String(s.groupe || '')) || /\\bETAT\\b|MINISTERE|ARMEE|DEFENSE|MILITAIRE|GENDARMERIE|CONSERVATOIRE|SNCF|RESEAU FERRE|AEROPORT|GRAND PORT|PORT AUTONOME|CENTRE HOSPITALIER|OFFICE PUBLIC|HABITAT/i.test(s.proprio || '')) return;")
open(p, 'w', encoding='utf-8').write(s); print('ok rapport4')
