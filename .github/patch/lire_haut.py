import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i in range(2985, 3012): print('%5d| %s' % (i + 1, L[i][:400]))
for i, l in enumerate(L):
    if re.search(r"\bK\s*=|K\.H\s*=|\bH\s*:|chiffresCles|extraitChiffres|niv\s*:", l) and not (2985 <= i <= 3012): print('%5d| %s' % (i + 1, l.strip()[:400]))
sys.exit(1)
