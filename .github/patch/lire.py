import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for j in range(1396, 1470): print('%5d| %s' % (j + 1, L[j][:400]))
for i, l in enumerate(L):
    if re.search(r"^async function viaProxy|^const AI_PROXY|^const AI_KEY", l): print('%5d| %s' % (i + 1, l[:400]))
sys.exit(1)
