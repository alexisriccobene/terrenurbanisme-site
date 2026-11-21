import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"(const|let|var)\s+K\b|K\s*=\s*[^=]|\bniv\b|hauteurs?\s*[:=]|non réglementée|plan des hauteurs", l, re.I): print('%5d| %s' % (i + 1, l.strip()[:300]))
sys.exit(1)
