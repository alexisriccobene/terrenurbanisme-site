"""Version client d'une agence : le chapitre métier devient « Le bien et son marché » (sans mention « préparé pour l'agent »), et peut être retiré comme les autres rubriques."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
rep("const PT = PROFIL_TITRE[d.profil], P = d.pro || {}", "const CLIENTV = !!(PERSO && d.profil === 'agent'), PT = CLIENTV ? 'Le bien et son marché' : PROFIL_TITRE[d.profil], P = d.pro || {}")
rep("    ABOUT[PT] = PROFIL_ABOUT[d.profil];\n    chapter(++CHN, PT, 'Rapport préparé pour : ' + PROFILS[d.profil] + '. Les chapitres suivants détaillent chaque point ; aucune information réglementaire n\\'est retirée.');",
    "    ABOUT[PT] = CLIENTV ? 'Prix et loyers du secteur, diagnostic énergétique, copropriété, commerces et services autour du bien.' : PROFIL_ABOUT[d.profil];\n    chapter(++CHN, PT, CLIENTV ? 'Sources publiques officielles : ventes (DVF), Carte des loyers, ADEME, registre des copropriétés, OpenStreetMap.' : 'Rapport préparé pour : ' + PROFILS[d.profil] + '. Les chapitres suivants détaillent chaque point ; aucune information réglementaire n\\'est retirée.');")
rep("(d.profil && d.profil !== 'particulier' ? ' · PRÉPARÉ POUR : '", "(d.profil && d.profil !== 'particulier' && !(d.perso) ? ' · PRÉPARÉ POUR : '")
rep("const CHAP_PERSO = ['Identification de la parcelle',", "const CHAP_PERSO = ['Le bien et son marché', 'Identification de la parcelle',")
open(p, 'w', encoding='utf-8').write(s); print('ok profils4')
