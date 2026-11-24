"""Cadre technique : hauteur lue dans les chiffres du règlement (même valeur que la synthèse), jamais « non réglementée » quand une hauteur est fixée."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "['Hauteur', (() => { try { const h = typeof hauteurTexte === 'function' ? hauteurTexte(d) : null;"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
b = "['Hauteur', (() => { try { const chh = (d.reglement && d.reglement.analysis && d.reglement.analysis.chiffres) || {}, hf = Number(chh.hauteur_facade_max_m) || 0, hft = Number(chh.hauteur_faitage_max_m) || 0; if (hf > 0 || hft > 0) return hf > 0 ? String(hf).replace('.', ',') + ' m à l\\'égout ou à l\\'acrotère' + (hft > hf ? ', ' + String(hft).replace('.', ',') + ' m au faîtage' : '') : String(hft).replace('.', ',') + ' m au faîtage'; const h = typeof hauteurTexte === 'function' ? hauteurTexte(d) : null;"
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok')
s = open(p, encoding='utf-8').read()
a = "table([{ label: 'PARCELLE', w: 0.17, bold: true }, { label: 'ADRESSE', w: 0.29 }, { label: 'CLASSE', w: 0.08 }, { label: 'LOGEMENT', w: 0.13 },"
if s.count(a) != 1: print('ANCRE2', s.count(a)); sys.exit(1)
s = s.replace(a, "table([{ label: 'PARCELLE', w: 0.13, bold: true }, { label: 'ADRESSE', w: 0.29 }, { label: 'CLASSE', w: 0.08 }, { label: 'LOGEMENT', w: 0.17 },")
open(p, 'w', encoding='utf-8').write(s); print('ok2')
