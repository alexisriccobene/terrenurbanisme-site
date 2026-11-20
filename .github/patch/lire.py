import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
i = next(i for i, l in enumerate(L) if "h3('Règles nationales applicables')" in l)
for j in range(i - 12, i + 20): print('%5d| %s' % (j + 1, L[j][:600]))
sys.exit(1)
