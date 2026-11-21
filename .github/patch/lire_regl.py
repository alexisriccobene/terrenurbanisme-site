import sys
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i in list(range(1712, 1760)) + list(range(1796, 1845)): print('%5d| %s' % (i + 1, L[i][:400]))
sys.exit(1)
