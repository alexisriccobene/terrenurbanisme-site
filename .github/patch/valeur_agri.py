# Terrain en zone agricole ou naturelle : plus de fourchette de prix (trompeuse), remplacée par les règles de vente (SAFER, preneur en place, contrôle des structures, barème officiel)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable : ' + label + ' (' + str(s.count(old)) + ')')
    s = s.replace(old, new)
rep("""  // VALEUR DE MARCHÉ : estimation du terrain à partir des ventes DVF du secteur
  // =====================================================================
  try {""", """  // VALEUR DE MARCHÉ : estimation du terrain à partir des ventes DVF du secteur
  // =====================================================================
  const AGRI = !!(d.zones && d.zones[0] && d.zones[0].v === 'non');
  if (AGRI) {
    const Z = d.zones[0];
    chapter(++CHN, 'Conditions de vente du terrain', 'Terrain situé en zone ' + (Z.code || 'agricole ou naturelle') + ' : vente encadrée par le code rural et de la pêche maritime.');
    h3('Pourquoi aucune fourchette de prix n\\'est donnée');
    text('La parcelle est classée en zone ' + (Z.code ? Z.code + ' (' + String(Z.typeLabel || '').toLowerCase() + ')' : 'non constructible') + ', où les constructions nouvelles ne sont en principe pas admises. Sa valeur ne se déduit pas des ventes de terrains à bâtir du secteur : elle dépend de l\\'usage agricole ou naturel du sol, de sa qualité, de son accès, de l\\'eau disponible et de l\\'existence éventuelle d\\'un bail rural. Une estimation automatique serait trompeuse : la valeur doit être établie au cas par cas par un notaire ou un expert foncier et agricole.', { size: 9.5 });
    h3('Le droit de préemption de la SAFER');
    kv([
      ['Principe', 'La vente d\\'un terrain agricole ou naturel est en principe soumise au droit de préemption de la SAFER (articles L. 143-1 et suivants du code rural et de la pêche maritime). Une surface minimale, fixée par département, peut en exclure les plus petites parcelles.'],
      ['Information obligatoire', 'Le notaire informe la SAFER du projet de vente au moins deux mois avant la signature : prix, conditions et identité de l\\'acquéreur.'],
      ['Ce que peut faire la SAFER', 'Renoncer, acheter au prix et aux conditions notifiés, ou proposer un prix inférieur si elle estime le prix exagéré. Le vendeur peut alors accepter, retirer son terrain de la vente ou demander au tribunal judiciaire de fixer le prix.'],
      ['Pourquoi elle intervient', 'Installation de jeunes agriculteurs, consolidation des exploitations, protection de l\\'environnement et des paysages, lutte contre la spéculation foncière.']
    ], { lw: 0.3 });
    h3('Les autres règles à connaître');
    kv([
      ['Fermier en place', 'Si le terrain est loué par bail rural, l\\'exploitant en place bénéficie d\\'un droit de préemption prioritaire, avant la SAFER.'],
      ['Autorisation d\\'exploiter', 'Un acquéreur qui souhaite exploiter le terrain peut devoir obtenir une autorisation d\\'exploiter auprès de la DDT(M), selon le schéma directeur régional des exploitations agricoles.'],
      ['Espace naturel sensible', 'Dans un espace naturel sensible, le département peut également disposer d\\'un droit de préemption.'],
      ['Constructions', 'Seules les constructions nécessaires à l\\'exploitation agricole ou forestière, ou à des équipements collectifs, sont en règle générale admises : l\\'achat ne donne pas de droit à bâtir une habitation.']
    ], { lw: 0.3 });
    h3('Repère officiel de prix');
    text('Le ministère de l\\'Agriculture publie chaque année le barème indicatif de la valeur vénale moyenne des terres agricoles, par région agricole et par nature de culture (arrêté publié au Journal officiel). C\\'est la référence à consulter, avec l\\'avis d\\'un notaire ou d\\'un expert foncier et agricole, avant de fixer un prix.', { size: 9.5 });
    note('Avant toute mise en vente, rapprochez-vous de votre notaire : il notifie la vente à la SAFER, vérifie l\\'existence d\\'un bail et sécurise le calendrier de la transaction.', 'cond');
  }
  if (!AGRI) try {""", 'debut valeur')
rep("""  } catch (e) { console.error('valeur de marché', e); }""", """  } catch (e) { console.error('valeur de marché', e); }
  // (fin valeur de marché)""", 'fin valeur')
# Ventes rurales (RNU, carte sans zonage) : rappel SAFER sous la fourchette
rep("""(VS.kind === 'nat' ? ' La parcelle étant en zone non constructible, seules les ventes de terrains agricoles ou naturels sont retenues.' : '')""",
    """(VS.kind === 'nat' ? ' Seules les ventes de terrains agricoles ou naturels sont retenues ; une telle vente est en principe soumise au droit de préemption de la SAFER, qui peut proposer un prix inférieur si elle l\\'estime exagéré.' : '')""", 'texte nat')
# Chapitre Environnement : pas de prix de terrains pour une parcelle agricole ou naturelle
rep("""    if (MK.terrainAB.count) rowsS.push(""", """    if (MK.terrainAB.count && !AGRI) rowsS.push(""", 'terrainAB')
rep("""    if (MK.terrain.count) rowsS.push(""", """    if (MK.terrain.count && !AGRI) rowsS.push(""", 'terrain')
rep("""    if (TS.count) { ensure(120);""", """    if (TS.count && !AGRI) { ensure(120);""", 'TS')
rep("""  if (DV && DV.sales && DV.sales.length) {
    ensure(140); h3('Ventes de terrains autour de la parcelle');""", """  if (DV && DV.sales && DV.sales.length && !AGRI) {
    ensure(140); h3('Ventes de terrains autour de la parcelle');""", 'DV')
rep("""  } else if (!MK) text('Aucune vente de terrain exploitable""", """  } else if (!MK && !AGRI) text('Aucune vente de terrain exploitable""", 'DV else')
# Descriptions du chapitre (intro et sommaire)
rep("""    'Valeur de marché': 'Ce que vaut le terrain d\\'après les ventes réelles du secteur : fourchette de prix, positionnement d\\'un prix de vente, évolution du marché et potentiel du terrain.',""",
    """    'Valeur de marché': 'Ce que vaut le terrain d\\'après les ventes réelles du secteur : fourchette de prix, positionnement d\\'un prix de vente, évolution du marché et potentiel du terrain.',
    'Conditions de vente du terrain': 'Terrain agricole ou naturel : droit de préemption de la SAFER, fermier en place, autorisation d\\'exploiter et repère officiel de prix.',""", 'desc chapitre')
rep("""      'Valeur de marché': 'La fourchette de prix du terrain d\\'après les ventes réelles du secteur.',""",
    """      'Valeur de marché': 'La fourchette de prix du terrain d\\'après les ventes réelles du secteur.',
      'Conditions de vente du terrain': 'Terrain agricole ou naturel : SAFER, fermier en place et repère officiel de prix.',""", 'sommaire')
open(p, 'w', encoding='utf-8').write(s); print('patch valeur_agri appliqué')
