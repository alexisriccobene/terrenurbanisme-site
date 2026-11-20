import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    for m in re.finditer(r"gratuit|offert", l, re.I): print('%5d| %s' % (i + 1, l[max(0, m.start() - 140):m.end() + 80]))
sys.exit(1)
