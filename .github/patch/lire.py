import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for j in range(1789, 1860): print('%5d| %s' % (j + 1, L[j][:500]))
for j in range(2995, 3010): print('%5d| %s' % (j + 1, L[j][:300]))
sys.exit(1)
