# Lecture seule : affiche des extraits de la source puis s'arrête (aucun déploiement)
import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
print('LIGNES', len(L))
for i, l in enumerate(L):
    if re.search(r"h3\('|chapter\(|newChapter|sectionTitle\(|tocAdd|^\s*(async )?function (h1|h2|h3|note|kvn|para|chap)\b", l):
        print('%5d| %s' % (i + 1, l[:220]))
def ctx(p, a=3, n=25, k=1):
    c = 0
    for i, l in enumerate(L):
        if re.search(p, l):
            print('==== %s @%d' % (p, i + 1))
            for j in range(max(0, i - a), min(len(L), i + n)): print('%5d| %s' % (j + 1, L[j][:500]))
            c += 1
            if c >= k: break
ctx(r"h3\('Taxe d", 5, 30)
ctx(r"^function note\(|const note = ", 0, 12)
ctx(r"^function kvn\(|const kvn = ", 0, 12)
sys.exit(1)
