import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"code: p\.libelle \|\| p\.typezone|p\.libelle \|\| p\.typezone|z\.p\.libelle \|\| z\.p\.typezone", l): print('%5d| %s' % (i + 1, l[:300]))
sys.exit(1)
