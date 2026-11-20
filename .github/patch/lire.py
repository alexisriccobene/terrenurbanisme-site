import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
i = next(i for i, l in enumerate(L) if re.search(r"^async function (acces|access|voirie)\w*\(", l))
for j in range(i, i + 45): print('%5d| %s' % (j + 1, L[j][:420]))
for k, l in enumerate(L):
    if 'Accès direct à une voie' in l or "'Non identifié'" in l: print('%5d| %s' % (k + 1, l[:420]))
sys.exit(1)
