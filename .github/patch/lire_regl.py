import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i in range(1136, 1165): print('%5d| %s' % (i + 1, L[i][:300]))
for i, l in enumerate(L):
    if re.search(r"zLocal|zonage_local|plu/.*t/|tuiles|planZonage|extraitPlan", l) and not (1136 <= i <= 1165): print('%5d| %s' % (i + 1, l.strip()[:300]))
sys.exit(1)
