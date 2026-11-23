# Rapport : chapitre « Votre projet, étape par étape » dans l'ordre chronologique, avec contacts et liens à chaque étape
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable : ' + label + ' (' + str(s.count(old)) + ')')
    s = s.replace(old, new)

# 1. Retirer le bloc des étapes de sa place actuelle (après les délais d'instruction)
a = s.index("  // Les étapes de la construction, du terrain aux clés\n  {")
m = "Démarches détaillées sur service-public.fr.', { size: 8, color: C.muet });\n  }"
b = s.index(m, a) + len(m)
s = s[:a] + s[b:].lstrip('\n')

# 2. Nouveau bloc chronologique, placé juste après l'analyse
NEW = r"""  h3('Analyse');
  (d.analysis || []).forEach(a => text(a, { size: 10 }));
  // Votre projet, étape par étape (ordre chronologique, avec contacts)
  {
    const MAe = d.mairie || null;
    const mair = MAe ? (MAe.nom || '').replace(/^Mairie\s*-\s*/i, 'Mairie de ') + (MAe.tel ? ' · ' + MAe.tel : '') + (MAe.email ? ' · ' + MAe.email : '') : 'Mairie de ' + (d.ref.commune || 'la commune');
    h3('Votre projet, étape par étape');
    text('Les étapes ci-dessous suivent l\'ordre réel d\'un projet de construction, de l\'achat du terrain à la déclaration aux impôts. Les montants sont indicatifs et à confirmer par devis.', { size: 9.5 });
    const ET = [
      ['Avant d\'acheter le terrain', 'Vérifiez les règles de la zone (chapitres précédents), puis demandez un certificat d\'urbanisme opérationnel (Cerfa 13410, sans frais, réponse sous 2 mois) : il fige les règles pendant 18 mois. En zone d\'argiles d\'aléa moyen ou fort, le vendeur doit fournir une étude de sol préalable.', 'Contact : ' + mair + ' · formulaire sur service-public.fr (rechercher « Cerfa 13410 »)'],
      ['Les études', 'Étude de sol géotechnique (G2) pour dimensionner les fondations : 1 500 à 3 000 €. Étude thermique RE2020, obligatoire pour le permis : 500 à 1 500 €. Bornage par un géomètre si les limites sont incertaines. L\'étude de sol ne porte pas sur les espèces protégées : un écologue n\'intervient qu\'en cas d\'enjeu (chapitre Environnement).', (d.geometres && d.geometres.length ? 'Géomètres proches du terrain : liste à la fin de ce chapitre' : 'Géomètres : annuaire de l\'Ordre sur geometre-expert.fr')],
      ['Les plans', 'Architecte obligatoire si la surface de plancher totale dépasse 150 m². En dessous, vous pouvez dessiner les plans vous-même ou faire appel à un dessinateur ou maître d\'œuvre (environ 1 500 à 4 000 € le dossier de permis). Architecte : 3 000 à 8 000 € pour la seule mission de permis, 8 à 12 % du coût des travaux pour une mission complète avec suivi du chantier.', 'Trouver un architecte : annuaire de l\'Ordre des architectes sur architectes.org'],
      ['Déposer le permis', 'Formulaire Cerfa 13406 (maison individuelle) et pièces PCMI1 à PCMI8 : plan de situation, plan de masse, coupe, notice, plans des façades et toitures, insertion dans le paysage, photos, attestation RE2020. Dépôt en mairie ou en ligne sur le guichet numérique de la commune. La mairie a 1 mois pour réclamer une pièce manquante ; l\'instruction dure 2 mois à partir du dossier complet, plus en secteur protégé.', 'Dépôt : ' + mair + ' · formulaire sur service-public.fr (rechercher « Cerfa 13406 »)'],
      ['Affichage et recours', 'Dès l\'accord, installez le panneau de permis sur le terrain, lisible depuis la voie, pendant toute la durée du chantier. Les tiers ont 2 mois à compter du premier jour d\'affichage pour contester ; la mairie peut retirer un permis illégal pendant 3 mois. Faites constater l\'affichage par un commissaire de justice (environ 300 à 600 € pour les trois constats).', 'Commissaires de justice : annuaire sur commissaire-justice.fr'],
      ['Avant les travaux', 'Souscrivez l\'assurance dommages-ouvrage, obligatoire (souvent 2 à 4 % du coût de la construction). Signez le contrat de construction de maison individuelle ou les marchés des artisans. Déposez la déclaration d\'ouverture de chantier (Cerfa 13407) le jour du démarrage. Le permis est valable 3 ans, prorogeable deux fois d\'un an.', 'Déclaration d\'ouverture : ' + mair],
      ['Le financement', 'La banque débloque le prêt au fur et à mesure du chantier, sur présentation des factures des entreprises ou des appels de fonds du constructeur. Avec un contrat de construction de maison individuelle, l\'échéancier est encadré par la loi : 15 % à l\'ouverture du chantier, 25 % aux fondations, 40 % aux murs, 60 % hors d\'eau, 75 % hors d\'air et cloisons, 95 % aux équipements, le solde à la réception. Des intérêts intercalaires peuvent courir sur les sommes débloquées.', 'Votre banque ou votre courtier'],
      ['La fin du chantier', 'Réception des travaux avec le constructeur ou les artisans, avec réserves si nécessaire. Déposez ensuite la déclaration attestant l\'achèvement et la conformité des travaux (DAACT, Cerfa 13408), avec l\'attestation RE2020 de fin de chantier. La mairie a 3 mois pour la contester (5 mois en secteur protégé).', 'Dépôt : ' + mair],
      ['Les impôts', 'Dans les 90 jours suivant l\'achèvement, déclarez la construction sur impots.gouv.fr, espace « Gérer mes biens immobiliers ». Cette déclaration sert au calcul de la taxe d\'aménagement (payée en une fois sous 1 500 €, sinon en deux fois, estimation plus bas dans ce chapitre) et de la taxe foncière, avec une exonération possible les deux premières années selon la commune.', 'impots.gouv.fr › Espace particulier › Gérer mes biens immobiliers']
    ];
    ET.forEach((s0, i) => {
      const lines = wrap(s0[1], F, 9, CW - 30), lc = wrap(s0[2], F, 8.5, CW - 30); ensure(lines.length * 13 + lc.length * 12 + 30);
      page.drawCircle({ x: M + 9, y: y - 9, size: 9, color: C.t });
      page.drawText(String(i + 1), { x: M + 9 - tw(String(i + 1), B, 9) / 2, y: y - 12, size: 9, font: B, color: C.white });
      page.drawText(clean(s0[0]), { x: M + 28, y: y - 12, size: 10.5, font: B, color: C.ink }); y -= 18;
      lines.forEach(l => { page.drawText(l, { x: M + 28, y: y - 9, size: 9, font: F, color: C.ink }); y -= 13; });
      lc.forEach(l => { page.drawText(l, { x: M + 28, y: y - 9, size: 8.5, font: F, color: C.t }); y -= 12; });
      y -= 7;
    });
  }"""
rep("  h3('Analyse');\n  (d.analysis || []).forEach(a => text(a, { size: 10 }));", NEW, 'analyse')
rep("h3('Démarches recommandées');", "h3('Les points à vérifier pour ce terrain');", 'demarches')
rep("chapter(++CHN, 'Constructibilité et démarches', 'Ce que ces règles impliquent pour votre projet.');",
    "chapter(++CHN, 'Votre projet, étape par étape', 'De l\\'achat du terrain à la déclaration aux impôts : démarches, délais, coûts et contacts.');", 'chapitre')
open(p, 'w', encoding='utf-8').write(s); print('patch etapes2 appliqué')
