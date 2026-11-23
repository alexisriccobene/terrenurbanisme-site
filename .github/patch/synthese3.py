# Rapport synthétique : quand le règlement n'est pas encore lu, on explique la zone au lieu de renvoyer à la mairie
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "    else text('Le règlement de la zone n\\'a pas pu être lu automatiquement : il est à consulter en mairie.', { size: 9.5 });"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, "    else if (zl.length) zl.forEach(z => { if (MULTI) h4('Zone ' + z.code + ' · ' + z.verdictWord.toLowerCase(), 60); text((MULTI ? '' : 'Zone ' + z.code + ' (' + z.typeLabel.toLowerCase() + ') : ' + z.verdictWord.toLowerCase() + '. ') + (z.explain || ''), { size: 9.5 }); });\n    else text('Le règlement de la zone n\\'a pas pu être lu automatiquement : il est à consulter en mairie.', { size: 9.5 });")
open(p, 'w', encoding='utf-8').write(s); print('patch synthese3 appliqué')
