# Lecture seule : affiche des extraits de la source puis s'arrête (aucun déploiement)
import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
print('LIGNES', len(L))
pats = [r"action === .espace.", r"action === .demo_lien.", r"async function handleVille|function handleVille", r"logo_path.*villes|villes.*logo"]
for p in pats:
    for i, l in enumerate(L):
        if re.search(p, l):
            print('==== %s @%d' % (p, i + 1))
            for j in range(max(0, i - 2), min(len(L), i + 16)): print('%5d| %s' % (j + 1, L[j][:1600]))
            n_=globals().setdefault('n_',{}); n_[p]=n_.get(p,0)+1
            if n_[p]>=4: break
sys.exit(1)
