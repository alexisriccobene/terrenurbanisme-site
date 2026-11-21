import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"[ée]tude de sol|ELAN|G1\b|vendeur doit fournir", l, re.I): print('%5d| %s' % (i + 1, l[:500]))
sys.exit(1)
