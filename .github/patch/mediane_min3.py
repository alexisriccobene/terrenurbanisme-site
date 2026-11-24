"""Marché 500 m : pas de médiane sous 3 ventes, seulement les prix extrêmes."""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "    const rowsS = [];\n    if (MK.maison.count) rowsS.push(['Maisons'"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
s = s.replace(a, "    const rowsS = [];\n    const rS = (l, q) => q.count >= 3 ? [l, String(q.count), eur(q.medPrice), m2(q.median), fmt(q.p10) + ' à ' + fmt(q.p90) + ' €/m²'] : [l, String(q.count), '–', '–', q.count === 1 ? fmt(q.median) + ' €/m²' : fmt(q.p10) + ' à ' + fmt(q.p90) + ' €/m²'];\n    if (MK.maison.count) rowsS.push(['Maisons'")
n = 0
for key, lab in [('maison', 'Maisons'), ('appartement', 'Appartements'), ('terrainAB', 'Terrains à bâtir'), ('terrain', 'Tous terrains nus')]:
    pat = "rowsS.push(['" + lab + "', String(MK." + key + ".count), eur(MK." + key + ".medPrice), m2(MK." + key + ".median), fmt(MK." + key + ".p10) + ' à ' + fmt(MK." + key + ".p90) + ' €/m²']);"
    c = s.count(pat)
    if c != 1: print('ANCRE', lab, c); sys.exit(1)
    s = s.replace(pat, "rowsS.push(rS('" + lab + "', MK." + key + "));"); n += 1
b = "    if (rowsS.length) table([{ label: 'TYPE DE BIEN', w: 0.22, bold: true }, { label: 'VENTES', w: 0.11 }, { label: 'PRIX MÉDIAN', w: 0.2 }, { label: '€/M² MÉDIAN', w: 0.2, bold: true }, { label: 'FOURCHETTE (80 %)', w: 0.27 }], rowsS, { size: 8.5 });"
if s.count(b) != 1: print('ANCRE T', s.count(b)); sys.exit(1)
s = s.replace(b, b + "\n    if (rowsS.some(r => r[2] === '–')) text('Moins de 3 ventes : aucune médiane n\\'est calculée, la fourchette indique le prix le plus bas et le plus haut.', { size: 8, color: C.muet });")
open(p, 'w', encoding='utf-8').write(s); print('ok', n)
