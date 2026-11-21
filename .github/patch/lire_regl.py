import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for a, b in ((1262, 1292), (3078, 3125)):
    for i in range(a, b): print('%5d| %s' % (i + 1, L[i][:330]))
sys.exit(1)
