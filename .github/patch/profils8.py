"""Présentation professionnelle : plus aucune mention « préparé pour » ; titres neutres selon le contenu du chapitre."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
rep("const PROFIL_TITRE = { agent: 'L\\'essentiel pour l\\'agent immobilier', notaire: 'L\\'essentiel pour le notaire', moe: 'L\\'essentiel pour le maître d\\'œuvre', geometre: 'L\\'essentiel pour le géomètre' };",
    "const PROFIL_TITRE = { agent: 'Le bien et son marché', notaire: 'Points de contrôle avant l\\'acte', moe: 'Cadre technique du projet', geometre: 'Foncier et division du terrain' };")
rep("(d.profil && d.profil !== 'particulier' && !(d.perso) ? ' · PRÉPARÉ POUR : ' + PROFILS[d.profil].toUpperCase() : '')", "''")
rep("CLIENTV ? 'Sources publiques officielles : ventes (DVF), Carte des loyers, ADEME, registre des copropriétés, Éducation nationale, Sirene.' : 'Rapport préparé pour : ' + PROFILS[d.profil] + '. Les chapitres suivants détaillent chaque point ; aucune information réglementaire n\\'est retirée.'",
    "({ agent: 'Sources publiques officielles : ventes (DVF), Carte des loyers, ADEME, registre des copropriétés, Éducation nationale, Sirene.', notaire: 'Synthèse des vérifications ; chaque point est détaillé dans le chapitre indiqué.', moe: 'Données techniques du terrain, pièces du permis et plan au format DXF.', geometre: 'Données cadastrales, règles de division et plan au format DXF.' })[d.profil] || ''")
open(p, 'w', encoding='utf-8').write(s); print('ok profils8')
