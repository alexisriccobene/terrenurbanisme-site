# Lecture seule : affiche des extraits de la source puis s'arrête (aucun déploiement)
import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
print('LIGNES', len(L))
pats = [r'function text\(', r'function ensure\(', r'function chapter\(', r'function note\(', r'function bullet\(', r'function newPage', r'function h3\(', r'Recommandation de l', r'reco\.', r'perso\.photos|P\.photos|photos\.', r'exclure', r'function table\(', r'const footer|function footer', r'apercu_dossier', r"action === 'personnaliser'|action == 'personnaliser'"]
for p in pats:
    for i, l in enumerate(L):
        if re.search(p, l):
            print('==== %s @%d' % (p, i + 1))
            for j in range(max(0, i - 2), min(len(L), i + 40)): print('%5d| %s' % (j + 1, L[j][:400]))
            break
sys.exit(1)
