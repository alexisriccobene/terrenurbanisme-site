import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
a = next(i for i, l in enumerate(L) if re.search(r"^async function analyseHuge\(", l))
b = next(i for i, l in enumerate(L) if re.search(r"^async function reglementFor\(", l))
for j in range(a, b): print('%5d| %s' % (j + 1, L[j][:330]))
sys.exit(1)
