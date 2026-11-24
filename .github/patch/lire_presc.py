import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"Aucune prescription graphique|zLocalSrc|zLocalF|zlocal|locale?\b.*=.*zonage_local|isLocal|\.local\b", l): print('%5d| %s' % (i + 1, l.strip()[:330]))
sys.exit(1)
