"""Synthèse : le recul par rapport aux voies n'est plus résumé en chiffre (le règlement le compte tantôt depuis l'axe, tantôt depuis l'alignement) ; le texte exact reste dans le tableau."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "        if (K.rv) rows.push(['Recul par rapport aux voies', nb(K.rv) + ' m minimum']);\n"
assert s.count(a) == 1
s = s.replace(a, "")
open(p, 'w', encoding='utf-8').write(s); print('ok synthese3')
