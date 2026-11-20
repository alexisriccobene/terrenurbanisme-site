import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
i = next(i for i, l in enumerate(L) if re.search(r"^async function reglement\(", l))
for j in range(i, i + 120): print('%5d| %s' % (j + 1, L[j][:420]))
sys.exit(1)
