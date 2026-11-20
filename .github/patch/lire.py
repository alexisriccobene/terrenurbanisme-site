import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"(const|function) clean\b|modere|Modere|tres faible|\bfaible\b.*\bmoyen", l): print('%5d| %s' % (i + 1, l[:400]))
for i in range(2455, 2510): print('%5d| %s' % (i + 1, L[i][:260]))
sys.exit(1)
