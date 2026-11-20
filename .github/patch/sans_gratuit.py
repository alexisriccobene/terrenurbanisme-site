# Vocabulaire : pas de « gratuit » dans les rapports
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "certificat d\\'urbanisme d\\'information, gratuit."
n = s.count(a); s = s.replace(a, "certificat d\\'urbanisme d\\'information, délivré sans frais.")
print('remplacements', n, 'reste gratuit :', len(re.findall(r"gratuit", s)))
open(p, 'w', encoding='utf-8').write(s); print('patch sans gratuit appliqué')
