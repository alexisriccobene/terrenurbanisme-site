import sys
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i in range(1125, 1200): print('%5d| %s' % (i + 1, L[i][:330]))
sys.exit(1)
