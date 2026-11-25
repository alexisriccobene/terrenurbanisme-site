"""Synthèse : le tableau des règles ne répète plus la hauteur, l'emprise et le recul déjà chiffrés juste au-dessus."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "      tableZ(RG.analysis, RG.zone);\n      text('Valeurs relevées dans le règlement de la zone"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
b = """      { const lab = rows.map(r => r[0]).join(' | '), hasH = /Hauteur/.test(lab), hasE = /Surface au sol|Emprise/.test(lab), hasL = /limites s/.test(lab);
        const rg = regles(RG.analysis).filter(r => !(hasH && /hauteur/i.test(r.critere)) && !(hasE && /emprise/i.test(r.critere)) && !(hasL && /limites s[ée]paratives/i.test(r.critere)));
        if (rg.length) table([{ label: 'RÈGLE' + (RG.zone ? ' (ZONE ' + RG.zone + ')' : ''), w: 0.3, bold: true }, { label: 'CE QUE DIT LE RÈGLEMENT', w: 0.7 }], rg.map(r => [r.critere, cut(r.regle, 160)]), { size: 8.3 }); }
      text('Valeurs relevées dans le règlement de la zone"""
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok')
