import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
print('LIGNES', len(L))
for i, l in enumerate(L):
    s = l.strip()
    if re.match(r'^(async )?function \w+', l) or re.search(r"motif|profil|\bversion_client|\bisPro\b|est_pro|clientVersion|rubriques", s) or re.search(r"chapitre\(|chap\(|section\(['\"]|<h1|titreChap|sommaire", s):
        print('%6d| %s' % (i + 1, s[:200]))
sys.exit(1)
