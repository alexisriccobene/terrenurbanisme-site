# Date d'approbation SuDocUH au format JJ/MM/AAAA
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "String(SDU['Approbation DU en vigueur']).slice(0, 10).replace(/-/g, '') : ''),"
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "String(SDU['Approbation DU en vigueur']).slice(0, 10).split('-').reverse().join('/') : ''),")
open(p, 'w', encoding='utf-8').write(s); print('patch sudocuh_doc3 appliqué')
