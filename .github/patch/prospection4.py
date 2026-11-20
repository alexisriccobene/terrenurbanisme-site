# Prospection : adresse propre du rapport d'exemple agence
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "'https://nmoigruxnhsidrhqtzid.supabase.co/storage/v1/object/public/exemples/rapport-exemple-agence.pdf'"; assert s.count(a) == 3, s.count(a)
s = s.replace(a, "'https://terrenurbanisme.com/exemple-rapport-agence.pdf'")
open(p, 'w', encoding='utf-8').write(s); print('patch prospection 4 appliqué')
