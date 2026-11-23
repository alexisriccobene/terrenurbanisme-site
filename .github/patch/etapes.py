# Rapport : « Les étapes de votre construction, du terrain aux clés » + précision sur l'étude de sol et les espèces protégées
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + label)
    s = s.replace(old, new)

# 1. Espèces protégées : l'étude de sol ne porte pas sur la faune ; pas d'étude écologique imposée en règle générale pour une maison
rep("bullet('Faire réaliser un pré-diagnostic écologique : un écologue visite le terrain et confirme ou écarte la présence d\\'espèces protégées et de leurs habitats (haies, vieux arbres, murets, zones humides, maquis).', { size: 9 });",
    "bullet('Pour une maison individuelle, aucune étude écologique n\\'est imposée en règle générale, et l\\'étude de sol porte sur le terrain (fondations), pas sur la faune ni la flore. Vous restez cependant responsable si une espèce protégée vit sur la parcelle : en cas de doute (espèce observée tout près, vieux arbres, murets, maquis, zone humide), faites passer un écologue avant de défricher.', { size: 9 });", 'especes')
rep("text('Ordres de prix indicatifs, honoraires de bureaux d\\'études en environnement. Pour une maison sur un terrain déjà entouré de constructions, le pré-diagnostic suffit le plus souvent.', { size: 8, color: C.muet });",
    "text('Ordres de prix indicatifs, honoraires de bureaux d\\'études en environnement, si une étude est nécessaire. Pour une maison sur un terrain déjà entouré de constructions, aucune étude n\\'est le plus souvent requise.', { size: 8, color: C.muet });", 'especes prix')

# 2. Étapes de construction
ET = r"""  text('Ces délais peuvent être majorés, notamment en site classé ou inscrit, aux abords d\'un monument historique ou lorsque la consultation d\'un service extérieur est nécessaire.', { size: 8.5, color: C.muet });
  // Les étapes de la construction, du terrain aux clés
  {
    h3('Les étapes de votre construction, du terrain aux clés');
    const ET = [
      ['Avant d\'acheter le terrain', 'Vérifiez les règles de la zone (ce rapport), puis demandez un certificat d\'urbanisme opérationnel (formulaire Cerfa 13410, sans frais, réponse sous 2 mois) : il fige les règles pendant 18 mois. En zone d\'argiles d\'aléa moyen ou fort, le vendeur doit fournir une étude de sol préalable.'],
      ['Les études', 'Étude de sol géotechnique (G2) pour dimensionner les fondations : 1 500 à 3 000 €. Étude thermique RE2020, obligatoire pour le permis : 500 à 1 500 €. Bornage par un géomètre si les limites sont incertaines. L\'étude de sol ne porte pas sur les espèces protégées : un écologue n\'intervient qu\'en cas d\'enjeu (voir le chapitre Environnement).'],
      ['Les plans', 'Architecte obligatoire si la surface de plancher totale dépasse 150 m². En dessous, vous pouvez dessiner les plans vous-même ou faire appel à un dessinateur ou maître d\'œuvre (environ 1 500 à 4 000 € le dossier de permis). Architecte : 3 000 à 8 000 € pour la seule mission de permis, 8 à 12 % du coût des travaux pour une mission complète avec suivi du chantier.'],
      ['Déposer le permis vous-même', 'Formulaire Cerfa 13406 (maison individuelle) et pièces PCMI1 à PCMI8 : plan de situation, plan de masse, coupe, notice, plans des façades et toitures, insertion dans le paysage, photos. Joignez l\'attestation RE2020. Dépôt en mairie ou en ligne sur le guichet numérique de la commune. La mairie a 1 mois pour réclamer une pièce manquante ; l\'instruction dure 2 mois à partir du dossier complet, plus en secteur protégé.'],
      ['Affichage et recours', 'Dès l\'accord, installez le panneau de permis sur le terrain, lisible depuis la voie, pendant toute la durée du chantier. Les tiers ont 2 mois à compter du premier jour d\'affichage pour contester ; la mairie peut retirer un permis illégal pendant 3 mois. Faites constater l\'affichage par un commissaire de justice (environ 300 à 600 € pour les trois constats).'],
      ['Avant les travaux', 'Souscrivez l\'assurance dommages-ouvrage, obligatoire (souvent 2 à 4 % du coût de la construction). Signez le contrat de construction de maison individuelle ou les marchés des artisans. Déposez la déclaration d\'ouverture de chantier (Cerfa 13407) en mairie le jour du démarrage. Le permis est valable 3 ans, prorogeable deux fois d\'un an.'],
      ['Le financement', 'La banque débloque le prêt au fur et à mesure du chantier, sur présentation des factures des entreprises ou des appels de fonds du constructeur. Avec un contrat de construction de maison individuelle, l\'échéancier est encadré par la loi : 15 % à l\'ouverture du chantier, 25 % aux fondations, 40 % aux murs, 60 % hors d\'eau, 75 % hors d\'air et cloisons, 95 % aux équipements, le solde à la réception. Des intérêts intercalaires peuvent courir sur les sommes débloquées.'],
      ['La fin du chantier', 'Réception des travaux avec le constructeur ou les artisans, avec réserves si nécessaire. Déposez ensuite en mairie la déclaration attestant l\'achèvement et la conformité des travaux (DAACT, Cerfa 13408), avec l\'attestation RE2020 de fin de chantier. La mairie a 3 mois pour la contester (5 mois en secteur protégé).'],
      ['Les impôts', 'Dans les 90 jours suivant l\'achèvement, déclarez la construction sur impots.gouv.fr, espace « Gérer mes biens immobiliers ». Cette déclaration sert au calcul de la taxe d\'aménagement (payée en une fois sous 1 500 €, sinon en deux fois) et de la taxe foncière, avec une exonération possible les deux premières années selon la commune.']
    ];
    ET.forEach((s0, i) => {
      const lines = wrap(s0[1], F, 9, CW - 30); ensure(lines.length * 13 + 26);
      page.drawCircle({ x: M + 9, y: y - 9, size: 9, color: C.t });
      page.drawText(String(i + 1), { x: M + 9 - tw(String(i + 1), B, 9) / 2, y: y - 12, size: 9, font: B, color: C.white });
      page.drawText(clean(s0[0]), { x: M + 28, y: y - 12, size: 10.5, font: B, color: C.ink }); y -= 18;
      lines.forEach(l => { page.drawText(l, { x: M + 28, y: y - 9, size: 9, font: F, color: C.ink }); y -= 13; });
      y -= 7;
    });
    text('Montants indicatifs, hors taxes ou toutes taxes selon les professionnels, à confirmer par devis. Démarches détaillées sur service-public.fr.', { size: 8, color: C.muet });
  }"""
rep("  text('Ces délais peuvent être majorés, notamment en site classé ou inscrit, aux abords d\\'un monument historique ou lorsque la consultation d\\'un service extérieur est nécessaire.', { size: 8.5, color: C.muet });", ET, 'etapes')
open(p, 'w', encoding='utf-8').write(s); print('patch etapes appliqué')
