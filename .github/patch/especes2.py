# Espèces protégées : nom français principal seul, protection des habitats d'après le code de l'arrêté, colonne observations plus lisible
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable ou multiple : ' + label)
    s = s.replace(old, new)
rep("x.fr = fr ? fr.vernacularName.charAt(0).toUpperCase() + fr.vernacularName.slice(1) : null;",
    "const v0 = fr ? String(fr.vernacularName).split(/[,;]/)[0].trim() : ''; x.fr = v0 ? v0.charAt(0).toUpperCase() + v0.slice(1) : null;", 'nom')
rep("const hab = x.st.some(e => /article 2|article 3/i.test(e[4] || '') && e[0] === 'PN');",
    "const hab = x.st.some(e => e[0] === 'PN' && (/O3$|(AR|M|I|MO|A|R)2$/.test(e[3] || '') || /article\\s*[23]\\b/i.test(e[4] || '')));", 'habitat')
rep("table([{ label: 'ESPÈCE', w: 0.40, bold: true }, { label: 'GROUPE', w: 0.14 }, { label: 'PROTECTION', w: 0.26 }, { label: 'OBSERVATIONS', w: 0.20 }],\n        SP.liste.map(s => [s.fr ? s.fr + ' (' + s.sci + ')' : s.sci, s.groupe, s.prot, fmt(s.n) + (s.der ? ' · dernière en ' + s.der : '')]));",
    "table([{ label: 'ESPÈCE', w: 0.40, bold: true }, { label: 'GROUPE', w: 0.13 }, { label: 'PROTECTION', w: 0.29 }, { label: 'VUE EN', w: 0.18 }],\n        SP.liste.map(s => [s.fr ? s.fr + ' (' + s.sci + ')' : s.sci, s.groupe, s.prot, (s.der ? String(s.der) : '-') + ' · ' + fmt(s.n) + ' obs.']));", 'table')
open(p, 'w', encoding='utf-8').write(s); print('patch especes2 appliqué')
