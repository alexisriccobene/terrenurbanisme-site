# Formulaire offre personnalisée : table dédiée demandes_offre (demandes_pro sert à l'annuaire des cabinets)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
i = s.index('async function demandePro(req) {'); j = s.index('async function handle(req) {', i)
f = s[i:j]; assert f.count("from('demandes_pro')") == 3, f.count("from('demandes_pro')")
f = f.replace("from('demandes_pro')", "from('demandes_offre')")
a = "await admin.from('demandes_offre').insert(r);"; assert f.count(a) == 1
f = f.replace(a, "{ const { error: ie } = await admin.from('demandes_offre').insert(r); if (ie) console.error('demande offre', ie.message); }")
s = s[:i] + f + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('patch demande offre appliqué')
