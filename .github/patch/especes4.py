# Espèces protégées : pas de mention « habitat » pour les plantes ; précision sur les plantes cultivées
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + label)
    s = s.replace(old, new)
rep("return { sci: x.sp.canonicalName, fr: x.fr, groupe: groupeEsp(x.sp), prot: types.map(lab).join(' + ') + (hab ? ' (espèce et habitat)' : ''), n: x.n, der: x.der };",
    "const grp = groupeEsp(x.sp); return { sci: x.sp.canonicalName, fr: x.fr, groupe: grp, prot: types.map(lab).join(' + ') + (hab && grp !== 'Plante' ? ' (espèce et habitat)' : ''), n: x.n, der: x.der };", 'plante')
rep("L\\'infraction est punie de 3 ans d\\'emprisonnement et 150 000 € d\\'amende.', 'cond');",
    "L\\'infraction est punie de 3 ans d\\'emprisonnement et 150 000 € d\\'amende.', 'cond');\n      if (SP.liste.some(s => s.groupe === 'Plante')) text('Pour les plantes, la protection vise les populations sauvages : un spécimen planté dans un jardin n\\'est pas concerné.', { size: 8.5, color: C.muet });", 'note plante')
open(p, 'w', encoding='utf-8').write(s); print('patch especes4 appliqué')
