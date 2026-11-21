import sys
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i in range(2745, 2768): print('%5d| %s' % (i + 1, L[i][:500]))
sys.exit(1)
