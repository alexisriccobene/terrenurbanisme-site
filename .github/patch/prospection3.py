# Prospection : le bouton « Voir un exemple de rapport » (agences, mandataires, experts) ouvre le rapport d'exemple Agence Dupont
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
PDF = "'https://nmoigruxnhsidrhqtzid.supabase.co/storage/v1/object/public/exemples/rapport-exemple-agence.pdf'"
n = 0
for c in ['agences', 'mandataires', 'experts']:
    a = "utm('https://terrenurbanisme.com/exemple.html', '%s')" % c
    assert s.count(a) == 1, c
    s = s.replace(a, PDF); n += 1
open(p, 'w', encoding='utf-8').write(s); print('patch prospection 3 appliqué', n)
