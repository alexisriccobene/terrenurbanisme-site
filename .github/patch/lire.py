# Lecture seule : affiche des extraits de la source puis s'arrête (aucun déploiement)
import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
print('LIGNES', len(L))
for i, l in enumerate(L):
    if re.search(r"Fibre et internet|chap\(|^\s*h2\(|fibreP\s*=|fibre:\s|handleFibre\(|Promise\.all\(\[|async function (collect|gather|donnees|analyse)", l):
        print('%5d| %s' % (i + 1, l[:300]))
def ctx(p, n=25, k=2):
    c = 0
    for i, l in enumerate(L):
        if re.search(p, l):
            print('==== %s @%d' % (p, i + 1))
            for j in range(max(0, i - 3), min(len(L), i + n)): print('%5d| %s' % (j + 1, L[j][:700]))
            c += 1
            if c >= k: break
ctx(r"Fibre et internet", 40, 3)
sys.exit(1)
