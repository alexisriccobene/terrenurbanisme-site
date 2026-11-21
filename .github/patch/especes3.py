# Espèces protégées : retour aux largeurs de colonnes d'origine (la version étroite bloquait la mise en page)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "table([{ label: 'ESPÈCE', w: 0.40, bold: true }, { label: 'GROUPE', w: 0.13 }, { label: 'PROTECTION', w: 0.29 }, { label: 'VUE EN', w: 0.18 }],\n        SP.liste.map(s => [s.fr ? s.fr + ' (' + s.sci + ')' : s.sci, s.groupe, s.prot, (s.der ? String(s.der) : '-') + ' · ' + fmt(s.n) + ' obs.']));"
new = "table([{ label: 'ESPÈCE', w: 0.40, bold: true }, { label: 'GROUPE', w: 0.14 }, { label: 'PROTECTION', w: 0.26 }, { label: 'OBSERVATIONS', w: 0.20 }],\n        SP.liste.map(s => [s.fr ? s.fr + ' (' + s.sci + ')' : s.sci, s.groupe, s.prot, fmt(s.n) + (s.der ? ' · dernière en ' + s.der : '')]));"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, new); open(p, 'w', encoding='utf-8').write(s); print('patch especes3 appliqué')
