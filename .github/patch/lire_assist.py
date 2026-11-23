import sys
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i in range(5506, 5562): print('%5d| %s' % (i + 1, L[i][:900]))
sys.exit(1)
