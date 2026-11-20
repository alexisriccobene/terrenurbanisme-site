import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
print('LIGNES', len(L))
c = 0
for i, l in enumerate(L):
    if re.search(r"R\.insee|const R = d\.ref|ref: R\b|const R = \{|R = \{ ?insee|^async function (render|buildPdf|makePdf)", l):
        print('%5d| %s' % (i + 1, l[:260])); c += 1
        if c > 25: break
for i in range(2683, 2700): print('%5d| %s' % (i + 1, L[i][:200]))
for i in range(1925, 1935): print('%5d| %s' % (i + 1, L[i][:200]))
sys.exit(1)
