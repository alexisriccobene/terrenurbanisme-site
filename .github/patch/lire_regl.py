import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"g[ée]otechni|L\. ?132|logement ===|logement:|\blogement\b.*schema|lieAct|K\.logement", l, re.I): print('%5d| %s' % (i + 1, l[:600]))
sys.exit(1)
