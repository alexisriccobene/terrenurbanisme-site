"""Profil « Géomètre » (chapitre foncier et division, plan DXF) ; écoles : établissement principal plutôt que ses sections ; Sirene : rythme d'appel plus lent."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
rep("notaire: 'Notaire', moe: 'Maître d\\'œuvre ou architecte' };", "notaire: 'Notaire', moe: 'Maître d\\'œuvre ou architecte', geometre: 'Géomètre' };")
rep("moe: 'L\\'essentiel pour le maître d\\'œuvre' };", "moe: 'L\\'essentiel pour le maître d\\'œuvre', geometre: 'L\\'essentiel pour le géomètre' };")
rep("  moe: 'Le cadre technique du projet :", "  geometre: 'Le foncier du terrain : surfaces cadastrale et calculée, voisinage, surface minimale, servitudes, règles de division et plan du terrain au format DXF.',\n  moe: 'Le cadre technique du projet :")
rep("if (/archi|oeuvre|moe|geometre|construct|promot/.test(s)) return 'moe';", "if (/geometre/.test(s)) return 'geometre'; if (/archi|oeuvre|moe|construct|promot/.test(s)) return 'moe';")
rep(": /architecte|geometre|constructeur|promoteur/.test(t) ? 'moe' : null;", ": /geometre/.test(t) ? 'geometre' : /architecte|constructeur|promoteur/.test(t) ? 'moe' : null;")
rep("  if (p === 'moe') {\n    out.zclim = zoneClimatique(insee, d.alti);\n    if (!/^97/.test(depOf(insee))) jobs.push(",
    "  if (p === 'moe' || p === 'geometre') {\n    if (p === 'moe') out.zclim = zoneClimatique(insee, d.alti);\n    if (!/^97/.test(depOf(insee))) jobs.push(")
# Chapitre géomètre, inséré avant le chapitre maître d'œuvre ; le plan DXF est commun
GEO = r'''    if (d.profil === 'geometre') {
      const K = d.calc || {}, sup = d.sups || [];
      h3('Foncier du terrain');
      const ec = R.contenance && R.areaCalc ? Math.round((R.areaCalc - R.contenance) / R.contenance * 100) : null;
      kvn([
        ['Identifiant cadastral', R.idu + (R.feuille ? ' · feuille ' + R.feuille : '')],
        ['Surface cadastrale', R.contenance ? fmt(R.contenance) + ' m² (contenance inscrite au cadastre)' : null],
        ['Surface calculée', R.areaCalc ? fmt(R.areaCalc) + ' m² sur le plan cadastral' + (ec != null ? ' (écart ' + (ec > 0 ? '+' : '') + ec + ' %)' : '') + ' · périmètre ' + fmt(R.perimeter) + ' m' : null],
        ['Parcelles voisines', (d.neighbors || []).length ? d.neighbors.join(', ') : null],
        ['Zone du document d\'urbanisme', zc.length ? zc.join(', ') + (d.doc ? ' · ' + d.doc.typeLabel : '') : null],
        ['Surface minimale de terrain', K.minTerrain ? fmt(K.minTerrain) + ' m² exigés par le règlement de la zone' : 'Aucune surface minimale relevée dans le règlement de la zone'],
        ['Recul des limites séparatives', K.rl ? String(K.rl).replace('.', ',') + ' m' : null],
        ['Servitudes d\'utilité publique', sup.length ? sup.map(x => x.typeLabel).filter((v, i, a) => a.indexOf(v) === i).slice(0, 4).join(' ; ') : 'Aucune publiée au Géoportail de l\'Urbanisme'],
        ['Altitude et pente', d.alti ? fmt(d.alti.min) + ' à ' + fmt(d.alti.max) + ' m · pente estimée ' + d.alti.slope + ' %' : null]
      ]);
      if (ec != null && Math.abs(ec) > 10) note('Écart de ' + Math.abs(ec) + ' % entre la contenance cadastrale et la surface du plan : la contenance est une donnée fiscale ; seul un bornage fixe les limites et la surface réelle.', 'cond');
      h3('Division du terrain');
      ['Division en vue de bâtir : déclaration préalable, ou permis d\'aménager si elle crée ou aménage des voies, espaces ou équipements communs (code de l\'urbanisme, art. R. 421-19 et R. 421-23).',
       'Chaque lot doit disposer d\'un accès à une voie et pouvoir être raccordé aux réseaux : voir le chapitre « Le terrain : accès, relief et réseaux ».',
       K.minTerrain ? 'Chaque lot destiné à bâtir doit respecter la surface minimale de ' + fmt(K.minTerrain) + ' m² relevée dans le règlement.' : 'Le règlement relevé n\'impose pas de surface minimale : la taille des lots dépend des reculs, de l\'emprise au sol et de l\'accès.',
       'Terrain en zone agricole ou naturelle : la division et la vente peuvent être soumises au droit de préemption de la SAFER (voir « Conditions de vente du terrain » le cas échéant).'].forEach(t2 => bullet(t2, { size: 9.5 }));
    }
'''
rep("    if (d.profil === 'moe') {\n      const K = d.calc || {}, an = d.reglement && d.reglement.analysis;", GEO + "    if (d.profil === 'moe' || d.profil === 'geometre') {\n      const K = d.calc || {}, an = d.reglement && d.reglement.analysis;")
# Le cadre technique et les pièces du permis restent propres au maître d'œuvre ; le DXF est commun
rep("      h3('Cadre technique du terrain');", "      if (d.profil === 'moe') {\n      h3('Cadre technique du terrain');")
rep("      h3('Plan du terrain au format DXF');", "      }\n      h3('Plan du terrain au format DXF');")
# Écoles : on écarte les sections (SEGPA, SEP) au profit de l'établissement
rep("&limit=1&select=nom_etablissement,position,statut_public_prive`;\n      const j = await getJSON(u, 10000);\n      const r = j && j.results && j.results[0];",
    "&limit=6&select=nom_etablissement,position,statut_public_prive`;\n      const j = await getJSON(u, 10000);\n      const L0 = (j && j.results || []), r = L0.find(x => !/^section/i.test(String(x.nom_etablissement || ''))) || L0[0];")
# Sirene : pauses plus longues (limite de débit)
rep("else await new Promise(z => setTimeout(z, 400 * (k + 1))); } catch (e) { await new Promise(z => setTimeout(z, 400)); } }",
    "else await new Promise(z => setTimeout(z, 1200 * (k + 1))); } catch (e) { await new Promise(z => setTimeout(z, 1200)); } }")
rep("    try { await sirene(lab, naf); } catch (e) {", "    await new Promise(z => setTimeout(z, 350));\n    try { await sirene(lab, naf); } catch (e) {")
open(p, 'w', encoding='utf-8').write(s); print('ok profils6')
