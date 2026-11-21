import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if 'fin des chapitres' in l:
        for j in range(i - 3, min(len(L), i + 70)): print('%5d| %s' % (j + 1, L[j][:260]))
sys.exit(1)
