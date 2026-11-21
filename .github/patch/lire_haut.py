import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for a, b in ((1418, 1440), (2062, 2080), (2998, 3008)):
    for i in range(a, b): print('%5d| %s' % (i + 1, L[i][:420]))
for i, l in enumerate(L):
    if re.search(r"hauteur_", l) and not any(a <= i < b for a, b in ((1418, 1440), (2062, 2080))): print('%5d| %s' % (i + 1, l.strip()[:300]))
sys.exit(1)
