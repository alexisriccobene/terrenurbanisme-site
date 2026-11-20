import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"function reglement|plusieurs fascicules|nomfic|urlfic", l): print('%5d| %s' % (i + 1, l[:300]))
sys.exit(1)
