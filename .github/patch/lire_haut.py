import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"Non précisée|hauteurMax|Hauteur maximale|hMax|hauteur_max", l): print('%5d| %s' % (i + 1, l.strip()[:400]))
sys.exit(1)
