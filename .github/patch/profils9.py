"""Un seul rapport pour tous : marché, contrôles avant l'acte, cadre technique, foncier et plan DXF dans chaque rapport complet ;
le profil n'est plus qu'une statistique. Le chapitre est placé avant « Votre projet, étape par étape »."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
TITRE = "Marché, contrôles et données techniques"
# 1. Données collectées pour tous les rapports complets
rep("  if (d.profil && d.profil !== 'particulier') { const PRO = {}; d.pro = PRO; try { await withTimeout(modulesPro(d.profil, c, d, PRO), 40000); }",
    "  if (!(meta && meta.synth)) { const PRO = {}; d.pro = PRO; try { await withTimeout(modulesPro('tous', c, d, PRO), 40000); }")
rep("  if (p === 'agent' || p === 'notaire') {\n    jobs.push(safe(coproParcelle", "  {\n    jobs.push(safe(coproParcelle")
rep("  if (p === 'agent') {\n    jobs.push(safe(loyersCommune", "  {\n    jobs.push(safe(loyersCommune")
rep("  if (p === 'moe' || p === 'geometre') {\n    if (p === 'moe') out.zclim = zoneClimatique(insee, d.alti);", "  {\n    out.zclim = zoneClimatique(insee, d.alti);")
# 2. Chapitre unique, déplacé avant « Votre projet, étape par étape »
i = s.index("  // =====================================================================\n  // 0. L'ESSENTIEL POUR VOTRE MÉTIER")
j = s.index("  // =====================================================================\n  // 1. IDENTIFICATION", i)
blk = s[i:j]; s = s[:i] + s[j:]
def b(old, new):
    global blk
    c = blk.count(old)
    if c < 1: print('ANCRE bloc', old[:100]); sys.exit(1)
    blk = blk.replace(old, new)
b("  // 0. L'ESSENTIEL POUR VOTRE MÉTIER (profil choisi à la commande)", "  // MARCHÉ, CONTRÔLES AVANT L'ACTE, CADRE TECHNIQUE, FONCIER ET PLAN DXF (tous les rapports complets)")
b("  if (d.profil && PROFIL_TITRE[d.profil]) {", "  if (d.pro) {")
b("const CLIENTV = !!(PERSO && d.profil === 'agent'), PT = CLIENTV ? 'Le bien et son marché' : PROFIL_TITRE[d.profil], P = d.pro || {}", "const PT = '" + TITRE + "', P = d.pro || {}")
b("    ABOUT[PT] = CLIENTV ? 'Prix et loyers du secteur, diagnostic énergétique, copropriété, commerces et services autour du bien.' : PROFIL_ABOUT[d.profil];",
  "    ABOUT[PT] = 'Prix et loyers du secteur, énergie, copropriété, services à proximité, points à contrôler avant la vente, cadre technique, foncier et plan du terrain au format DXF.';")
k = blk.index("    chapter(++CHN, PT, "); k2 = blk.index("\n", k)
blk = blk[:k] + "    chapter(++CHN, PT, 'Sources publiques officielles : DVF, Carte des loyers, ADEME, ANAH, Éducation nationale, Sirene, SNCF, Géorisques, IGN.');" + blk[k2:]
for old in ["    if (d.profil === 'agent') {", "    if (d.profil === 'agent' || d.profil === 'notaire') {", "    if (d.profil === 'notaire') {", "    if (d.profil === 'geometre') {", "    if (d.profil === 'moe' || d.profil === 'geometre') {", "      if (d.profil === 'moe') {"]:
    b(old, old[:old.index('if')] + "{")
b("h3('Points à contrôler avant l\\'acte');", "h3('Points à contrôler avant la vente');")
rep("  chapter(++CHN, 'Votre projet, étape par étape',", blk + "  chapter(++CHN, 'Votre projet, étape par étape',")
# 3. Version client des agences : la rubrique peut être retirée
rep("const CHAP_PERSO = ['Le bien et son marché', ", "const CHAP_PERSO = [")
rep("'Opportunités autour du terrain', 'Votre projet, étape par étape'", "'Opportunités autour du terrain', '" + TITRE + "', 'Votre projet, étape par étape'")
# 4. Pas de doublons entre « Foncier » et « Cadre technique »
for old in ["        ['Zone du document d\\'urbanisme', zc.length ? zc.join(', ') + (d.doc ? ' · ' + d.doc.typeLabel : '') : null],\n        ['Surface minimale de terrain'",
            ]:
    rep(old, "        ['Surface minimale de terrain'")
rep("        ['Recul des limites séparatives', K.rl ? String(K.rl).replace('.', ',') + ' m' : null],\n        ['Servitudes d\\'utilité publique', sup.length ?", "        ['Servitudes d\\'utilité publique', sup.length ?")
rep("        ['Servitudes d\\'utilité publique', sup.length ? sup.map(x => x.typeLabel).filter((v, i, a) => a.indexOf(v) === i).slice(0, 4).join(' ; ') : 'Aucune publiée au Géoportail de l\\'Urbanisme'],\n        ['Altitude et pente', d.alti ? fmt(d.alti.min) + ' à ' + fmt(d.alti.max) + ' m · pente estimée ' + d.alti.slope + ' %' : null]\n      ]);",
    "        ['Servitudes d\\'utilité publique', sup.length ? sup.map(x => x.typeLabel).filter((v, i, a) => a.indexOf(v) === i).slice(0, 4).join(' ; ') : 'Aucune publiée au Géoportail de l\\'Urbanisme']\n      ]);")
rep("        ['Surface du terrain', R.contenance ? fmt(R.contenance) + ' m² (cadastre)' + (R.areaCalc && Math.abs(R.areaCalc - R.contenance) / R.contenance > 0.1 ? ' · ' + fmt(R.areaCalc) + ' m² mesurés sur le plan : écart à faire lever par un géomètre' : '') : null],\n", "")
rep("      h3('Foncier du terrain');", "      h3('Foncier et division');")
rep("      h3('Division du terrain');\n", "")
open(p, 'w', encoding='utf-8').write(s); print('ok profils9')
