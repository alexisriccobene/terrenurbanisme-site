"""Lisibilité A : servitudes et prescriptions expliquées ; implantation réaliste ; chapitre risques réduit aux risques présents et expliqué."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag, n=1):
    global s
    c = s.count(a)
    if c != n: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)
def cut(start, end, new, tag):
    global s
    i = s.find(start); j = s.find(end, i + 1)
    if i < 0 or j < 0 or s.count(start) != 1: print('ANCRE', tag, i, j, s.count(start)); sys.exit(1)
    s = s[:i] + new + s[j:]

# ---------- Chapitre 2 : explications ----------
rep("const SUP = {\n", r"""const PSC_ALL = { '01': 'Espace boisé classé', '02': 'Limitation de la constructibilité (environnement, risques, intérêt général)', '03': 'Secteur avec règles de reconstruction ou de démolition', '04': 'Obligations de stationnement liées aux transports', '05': 'Emplacement réservé', '07': 'Patrimoine bâti ou paysager protégé', '08': 'Terrain cultivé ou non bâti protégé en zone urbaine', '13': 'Zone aménagée pour le ski', '14': 'Secteur de plan de masse', '15': 'Règle d\'implantation des constructions', '16': 'Secteur réservé aux équipements collectifs', '17': 'Secteur de mixité sociale', '18': 'Orientation d\'aménagement et de programmation (OAP)', '19': 'Secteur protégé pour la richesse du sol ou du sous-sol', '20': 'Secteur de transfert de constructibilité', '22': 'Diversité commerciale protégée', '23': 'Taille minimale des logements', '24': 'Voie ou chemin à conserver ou à créer', '25': 'Continuité écologique (trame verte et bleue)', '26': 'Secteur de performance énergétique', '27': 'Secteur d\'aménagement numérique', '28': 'Conditions de desserte', '29': 'Densité minimale de construction', '30': 'Majoration des volumes constructibles', '31': 'Espace remarquable du littoral', '34': 'Espace montagnard à préserver', '35': 'Terres agricoles, pastorales ou forestières à préserver', '36': 'Mixité des destinations', '37': 'Règles différentes au rez-de-chaussée et aux étages', '38': 'Règle particulière d\'emprise au sol', '39': 'Règle particulière de hauteur', '40': 'Règle particulière de volume', '41': 'Règle particulière d\'aspect extérieur', '42': 'Coefficient de biotope', '43': 'Espaces libres et plantations à réaliser', '44': 'Règle particulière de stationnement', '45': 'Zone d\'aménagement concerté (ZAC)', '47': 'Desserte par les réseaux', '48': 'Limitation de l\'imperméabilisation des sols', '49': 'Opération d\'ensemble imposée', '50': 'Activités ou destinations interdites', '51': 'Activités ou destinations autorisées sous conditions', '99': 'Prescription particulière' };
const PSC_EXPL = { '01': 'Les arbres de cette partie sont protégés : défrichement interdit et construction impossible sur l\'espace boisé ; une coupe d\'arbres demande une déclaration en mairie.', '02': 'Sur cette partie, la construction est interdite ou limitée pour un motif de risque, d\'environnement ou d\'intérêt général : la règle exacte figure au règlement.', '03': 'Des règles particulières s\'appliquent en cas de démolition ou de reconstruction (permis de démolir, reconstruction encadrée).', '04': 'Le nombre de places de stationnement exigé est adapté à la desserte en transports en commun.', '05': 'Cette partie est réservée pour un futur équipement public (route, élargissement, parking, école...) : on ne peut pas y construire autre chose. Le propriétaire peut demander à la collectivité de l\'acheter (droit de délaissement).', '07': 'Un bâtiment, un mur, un arbre ou un paysage est protégé : le démolir demande un permis, le modifier une déclaration, et le projet doit le préserver.', '08': 'Jardin ou espace vert protégé en ville : on ne peut pas y construire.', '13': 'Secteur réservé aux aménagements de pistes de ski.', '14': 'L\'emplacement et le volume des constructions sont fixés par un plan précis : le projet doit le respecter.', '15': 'Les constructions doivent respecter un recul ou un alignement particulier par rapport à l\'élément cité (voie, cours d\'eau...) : la distance exacte figure au règlement et sur le plan de zonage.', '16': 'Secteur réservé aux équipements et services publics.', '17': 'Un programme de logements doit comporter une part de logements sociaux, fixée par le règlement.', '18': 'Le projet doit être compatible avec les orientations d\'aménagement prévues pour ce secteur (accès, implantation, densité, espaces verts) : document à consulter avant de dessiner le projet.', '19': 'Secteur protégé pour ses ressources du sol ou du sous-sol : constructions limitées.', '20': 'Les droits à construire peuvent être transférés vers un autre secteur.', '22': 'Les commerces en rez-de-chaussée sont protégés : leur transformation en logement est limitée.', '23': 'Les logements créés doivent respecter une surface minimale.', '24': 'Un tracé de voie ou de chemin est à conserver ou à créer : le projet doit le respecter.', '25': 'Haie, boisement, cours d\'eau ou passage pour la faune à préserver : le projet doit l\'éviter ou le maintenir.', '26': 'Les constructions doivent atteindre une performance énergétique renforcée.', '27': 'Les constructions doivent prévoir les fourreaux pour la fibre.', '28': 'Des conditions particulières d\'accès et de desserte par les voies s\'appliquent.', '29': 'Une densité minimale de construction est imposée.', '30': 'Le règlement autorise un volume de construction supplémentaire sous conditions.', '31': 'Espace remarquable du littoral : seuls des aménagements légers sont admis, pas de maison.', '34': 'Paysage ou milieu montagnard à préserver : constructions très limitées.', '35': 'Terres agricoles, pastorales ou forestières à préserver : constructions limitées aux besoins de ces activités.', '36': 'Le secteur impose un mélange d\'usages (logement, commerce, bureaux...).', '37': 'Les règles diffèrent entre le rez-de-chaussée et les étages.', '38': 'Une emprise au sol particulière s\'applique sur cette partie, à la place de la règle générale de la zone.', '39': 'Une hauteur particulière s\'applique sur cette partie, à la place de la règle générale de la zone.', '40': 'Un volume particulier s\'applique sur cette partie, à la place de la règle générale de la zone.', '41': 'Des règles d\'aspect particulières (façades, toitures, couleurs) s\'appliquent sur cette partie.', '42': 'Une part minimale du terrain doit rester végétalisée ou perméable.', '43': 'Des espaces verts, plantations ou aires de jeux doivent être réalisés.', '44': 'Une règle de stationnement particulière s\'applique.', '45': 'Le terrain est dans une zone d\'aménagement concerté : surfaces et usages sont fixés par l\'aménageur.', '47': 'Des conditions particulières de raccordement aux réseaux s\'appliquent.', '48': 'Il faut limiter les surfaces imperméables et gérer les eaux de pluie sur le terrain.', '49': 'On ne peut construire que dans le cadre d\'une opération d\'ensemble (lotissement, groupe de maisons), pas au coup par coup.', '50': 'Certaines activités ou destinations sont interdites sur ce secteur.', '51': 'Certaines activités ou destinations ne sont autorisées que sous conditions.', '99': 'Prescription particulière : la règle figure au règlement du PLU.' };
const SUP_EXPL = { a1: 'Forêt relevant du régime forestier, gérée par l\'Office national des forêts : défrichement et construction très encadrés.', a4: 'Une bande le long du cours d\'eau doit rester accessible pour son entretien : clôtures et constructions y sont limitées.', a5: 'Une canalisation publique d\'eau ou d\'assainissement est enterrée : bande à laisser libre et accessible pour l\'entretien.', ac1: 'Le terrain est aux abords d\'un monument historique : l\'architecte des Bâtiments de France donne son avis sur le projet (voir plus bas).', ac2: 'Site protégé pour son paysage : les travaux sont soumis à l\'architecte des Bâtiments de France (site inscrit) ou à une autorisation spéciale (site classé).', ac3: 'Réserve naturelle : les travaux y sont très encadrés, souvent interdits.', ac4: 'Site patrimonial remarquable : règles patrimoniales strictes et accord de l\'architecte des Bâtiments de France.', as1: 'Périmètre de protection d\'un captage d\'eau potable : certaines activités et constructions sont interdites ou réglementées (assainissement, stockages, forages).', el7: 'Plan d\'alignement : une bande du terrain peut servir à élargir la voie ; pas de construction nouvelle sur cette bande.', el9: 'Servitude de passage des piétons le long du littoral : une bande de 3 m doit rester libre.', el11: 'Pas d\'accès direct du terrain sur cette route express ou cette déviation.', i3: 'Une canalisation de gaz passe à proximité : constructions limitées dans une bande de sécurité et travaux à déclarer avant de creuser.', i4: 'Une ligne électrique traverse ou surplombe le terrain : droit de passage et d\'élagage pour le gestionnaire, distances de sécurité pour construire.', int1: 'Proximité d\'un cimetière : la construction d\'habitations et de puits à proximité est soumise à autorisation.', pm3: 'Plan de prévention des risques technologiques autour d\'un site industriel : selon la zone, constructions interdites ou renforcées.', pt1: 'Protection d\'une station de télécommunications contre les perturbations électriques : sans effet pour une maison courante.', pt2: 'Protection des faisceaux hertziens : la hauteur des constructions peut être limitée.', pt3: 'Câble de télécommunications : bande à laisser accessible.', t1: 'Voie ferrée à proximité : distances à respecter pour construire, planter ou clôturer.', t4: 'Balisage aéronautique : certaines constructions hautes doivent être balisées.', t5: 'Abords d\'un aérodrome : la hauteur des constructions est limitée.', t7: 'Les constructions de grande hauteur sont soumises à l\'avis de l\'aviation civile.' };
function supExpl(code, label) {
  if (code === 'pm1') { const t = String(label || ''); const r = /PPRIF|incendie|feu/i.test(t) ? 'd\'incendie de forêt' : /PPRI\b|inond/i.test(t) ? 'd\'inondation' : /mouvement|PPRMT|glissement|éboul/i.test(t) ? 'de mouvement de terrain' : /littora|submersion/i.test(t) ? 'littoraux' : 'naturels'; return 'La commune a un plan de prévention des risques ' + r + '. Selon la zone du plan où se trouve le terrain, la construction est interdite ou soumise à conditions : demandez en mairie la carte de zonage et le règlement du plan.'; }
  return SUP_EXPL[code] || 'Servitude d\'utilité publique : ses effets figurent dans les annexes du PLU.';
}
const SUP = {
""", 'consts')
rep(".map(p => ({ label: p.libelle || p.txt || 'Prescription', typeLabel: PSC[String(p.typepsc || '').padStart(2, '0')] || ('Prescription du PLU' + (p.typepsc ? ' (type ' + p.typepsc + ')' : '')) })), x => x.label + x.typeLabel);",
    ".map(p => { const cd = String(p.typepsc || '').padStart(2, '0'); return { code: cd, label: p.libelle || p.txt || 'Prescription', typeLabel: PSC_ALL[cd] || PSC[cd] || 'Prescription du PLU' }; }), x => x.label + x.typeLabel);", 'psc')
rep("    table([{ label: 'PRESCRIPTION', w: 0.62 }, { label: 'TYPE', w: 0.38 }], d.prescriptions.map(p => [p.label, p.typeLabel]));",
    "    table([{ label: 'PRESCRIPTION', w: 0.4, bold: true }, { label: 'CE QUE CELA VEUT DIRE', w: 0.6 }], d.prescriptions.map(p => [p.typeLabel + (p.label && p.label !== p.typeLabel && p.label !== 'Prescription' ? ' : ' + p.label : ''), PSC_EXPL[p.code] || 'La règle figure au règlement du PLU.']), { size: 8.5 });", 'pscT')
rep("    table([{ label: 'CODE', w: 0.12, bold: true }, { label: 'SERVITUDE', w: 0.48 }, { label: 'DÉTAIL', w: 0.40 }], d.sups.map(s => [s.code.toUpperCase(), s.typeLabel, s.label]));",
    "    text('Les servitudes d\\'utilité publique sont des contraintes fixées par l\\'État ou un service public (monument, risque, réseau...). Elles s\\'ajoutent aux règles du PLU.', { size: 9 });\n    table([{ label: 'SERVITUDE', w: 0.4, bold: true }, { label: 'CE QUE CELA VEUT DIRE', w: 0.6 }], d.sups.map(s => [s.typeLabel + (s.label ? ' : ' + s.label : '') + ' (' + s.code.toUpperCase() + ')', supExpl(s.code, s.label)]), { size: 8.5 });", 'supT')

# ---------- Chapitre 3 : implantation réaliste ----------
rep("  if (maxFoot >= 120) gabarits.push({ type: 'Maison de plain-pied', w: 13.5, l: 9, niv: 1 });",
    "  if (maxFoot >= 180 && (K.zArea || 0) >= 1500) gabarits.push({ type: 'Villa de plain-pied', w: 18, l: 10, niv: 1 });\n  if (maxFoot >= 150 && (K.zArea || 0) >= 900) gabarits.push({ type: 'Maison de plain-pied', w: 15, l: 10, niv: 1 });\n  if (maxFoot >= 120) gabarits.push({ type: 'Maison de plain-pied', w: 13.5, l: 9, niv: 1 });", 'gab')
i = s.find("  if (hz) { const xs = hz.map(p => p[0]), ys = hz.map(p => p[1]); outer:")
j = s.find("\n", i)
if i < 0: print('ANCRE pool'); sys.exit(1)
s = s[:i] + """  if (hz) {
    // Piscine accolée à la maison : côté jardin (sud) en priorité, à 3 m de la façade
    const ca = Math.cos(best.a), sa = Math.sin(best.a), Wd = G.w, Ld = G.l, cands = [];
    const sides = [[0, 1, Ld / 2], [0, -1, Ld / 2], [1, 0, Wd / 2], [-1, 0, Wd / 2]];
    for (const [ux, uy, half] of sides) {
      const nx = ux * ca - uy * sa, ny = ux * sa + uy * ca; // normale du côté, en coordonnées locales
      const along = ux === 0 ? Wd : Ld, pw = ux === 0 ? 8 : 4, pl = ux === 0 ? 4 : 8;
      const tx = ux === 0 ? ca : -sa, ty = ux === 0 ? sa : ca;
      for (const off of [0, -(along - 8) / 2, (along - 8) / 2]) {
        const dist = half + 3 + 2; const cx = best.cx + nx * dist + tx * off, cy = best.cy + ny * dist + ty * off;
        const P = rect(cx, cy, pw, pl, best.a);
        if (fits(P, hz) && !P.some(q => inPoly(q, best.R))) cands.push({ P, sc: -ny * 2 + (off === 0 ? 0.5 : 0) });
      }
    }
    cands.sort((u, v) => v.sc - u.sc); if (cands.length) piscine = cands[0].P;
  }""" + s[j:]

# ---------- Chapitre 5 : risques ----------
new5 = r"""  const RKX = {
    inondation: 'Le terrain est en zone inondable connue : selon le plan de prévention, construction interdite ou soumise à des règles (plancher surélevé, pas de sous-sol).',
    remonteeNappe: 'L\'eau souterraine peut remonter près de la surface : éviter les sous-sols et les caves, prévoir un drainage ; à faire vérifier par l\'étude de sol.',
    risqueCotier: 'Exposition à la submersion marine : construction interdite ou soumise à des règles renforcées selon le plan de prévention.',
    reculTraitCote: 'Le rivage recule à cet endroit : la commune peut interdire ou limiter les constructions dans la zone exposée.',
    mouvementTerrain: 'Des glissements, chutes de blocs ou effondrements sont recensés : l\'étude de sol (G2) doit adapter les fondations et les murs de soutènement.',
    avalanche: 'Zone exposée aux avalanches : constructions interdites ou renforcées selon le plan de prévention.',
    eruptionVolcanique: 'Zone exposée au risque volcanique : consignes de sécurité à connaître ; règles fixées par le plan de prévention s\'il existe.',
    cyclone: 'Zone exposée aux cyclones : toiture, fixations et ouvertures doivent respecter les règles paracycloniques.',
    feuForet: 'Terrain exposé aux feux de forêt : débroussaillement obligatoire autour des constructions (en général sur 50 m) ; un terrain boisé peut demander une autorisation de défrichement avant de construire.',
    icpe: 'Une installation industrielle classée est proche : nuisances possibles (bruit, trafic, odeurs) ; pas de règle de construction sauf plan de prévention technologique.',
    nucleaire: 'Le terrain est proche d\'une installation nucléaire : un plan d\'intervention fixe les consignes en cas d\'accident.',
    canalisationsMatieresDangereuses: 'Une canalisation de gaz ou d\'hydrocarbures passe à proximité : constructions limitées dans une bande de sécurité, travaux à déclarer avant de creuser.',
    pollutionSols: 'Une activité passée a pu polluer le sol : un diagnostic de pollution est conseillé avant d\'acheter, et obligatoire pour construire dans un secteur d\'information sur les sols.',
    ruptureBarrage: 'Le terrain est dans la zone qui serait inondée en cas de rupture d\'un barrage : consignes d\'alerte, pas de règle de construction particulière.',
    risqueMinier: 'D\'anciennes mines peuvent provoquer des affaissements : constructions encadrées par le plan de prévention minier s\'il existe.'
  };
  const rkLvl = r => { const t = String(r.adresse || r.commune || '').replace(/^\s*(risque\s+)?existant\s*[-–]?\s*/i, '').trim(); return t ? t.charAt(0).toUpperCase() + t.slice(1) : 'Oui'; };
  const rkExpl = r => {
    if (r.key === 'seisme') { const z = Number((String(RK.sismique || '').match(/\d/) || [])[0]) || null; return z ? (z >= 3 ? 'Zone de sismicité ' + z + ' : les règles de construction parasismiques s\'appliquent à une maison (attestation à joindre au permis).' : 'Zone de sismicité ' + z + ' : aucune règle parasismique n\'est imposée pour une maison individuelle.') : 'Règles parasismiques selon la zone de sismicité.'; }
    if (r.key === 'retraitGonflementArgile') { const t = String(r.adresse || r.commune || ''); return /moyen|fort/i.test(t) ? 'Le sol argileux gonfle et se rétracte avec l\'humidité : étude de sol obligatoire à la vente d\'un terrain constructible et fondations adaptées imposées.' : 'Le sol peut légèrement bouger avec la sécheresse : pas d\'étude obligatoire au titre des argiles, fondations soignées recommandées.'; }
    if (r.key === 'radon') return (RK.radonClass === 3 || /important|significatif/i.test(String(r.adresse || r.commune || ''))) ? 'Gaz radioactif naturel venant du sol : prévoir une bonne ventilation et l\'étanchéité du plancher bas ; mention obligatoire dans l\'état des risques.' : 'Gaz radioactif naturel en faible quantité : une bonne ventilation suffit.';
    return RKX[r.key] || 'Risque recensé : se renseigner en mairie sur les règles applicables.';
  };
  if (RK.unavailable) note('Le service Géorisques n\'a pas répondu au moment de l\'établissement du rapport. Les risques doivent être vérifiés sur georisques.gouv.fr.', 'cond');
  if (RK.secours) note('Le rapport de risques à l\'adresse de Géorisques était indisponible : les risques ci-dessous sont ceux recensés sur la commune, à confirmer sur georisques.gouv.fr pour la parcelle.', 'cond');
  {
    const ALLR = [...(RK.naturels || []), ...(RK.techno || [])];
    const PRES = RK.addressLevel ? ALLR.filter(r => r.present) : ALLR.filter(r => /existant|concern/i.test(String(r.commune || '')) || r.present);
    const ABS = RK.addressLevel ? ALLR.filter(r => !r.present) : [];
    h3(RK.addressLevel ? 'Les risques qui concernent le terrain' : 'Les risques recensés sur la commune');
    if (PRES.length) {
      text(RK.addressLevel ? 'Seuls les risques relevés à l\'adresse du terrain sont présentés, avec ce qu\'ils impliquent pour un projet.' : 'Le niveau de risque à l\'adresse du terrain n\'a pas pu être obtenu : voici les risques recensés sur la commune, à confirmer pour la parcelle.', { size: 9 });
      table([{ label: 'RISQUE', w: 0.24, bold: true }, { label: 'NIVEAU', w: 0.16 }, { label: 'CE QUE CELA IMPLIQUE', w: 0.6 }], PRES.map(r => [r.label, r.key === 'seisme' && RK.sismique ? RK.sismique.replace(/^Zone\s*/i, 'Zone ') : rkLvl(r), rkExpl(r)]), { size: 8.5 });
    } else note('Aucun risque naturel ou technologique n\'est relevé à l\'adresse du terrain.', 'ok');
    const PM1 = (d.sups || []).filter(x => x.code === 'pm1');
    if (PM1.length) note('Plan de prévention : ' + PM1.map(x => x.label || 'plan des risques naturels').join(', ') + '. ' + supExpl('pm1', PM1[0].label), 'cond');
    if (ABS.length) text('Recherchés et non relevés à l\'adresse : ' + ABS.map(r => r.label.charAt(0).toLowerCase() + r.label.slice(1)).join(', ') + '.', { size: 8.5, color: C.muet });
  }
  h3('Catastrophes naturelles déjà reconnues sur la commune');
  if (RK.catnat && RK.catnat.length) {
    const G = {}; RK.catnat.forEach(c => { const k = c.label || 'Autre'; (G[k] = G[k] || []).push(c); });
    const yr = c => String(c.period || '').slice(-4);
    const parts = Object.entries(G).sort((a, b) => b[1].length - a[1].length).map(([k, L]) => L.length + ' pour ' + k.toLowerCase() + ' (dernier en ' + yr(L[0]) + ')');
    note(RK.catnat.length + ' arrêté' + (RK.catnat.length > 1 ? 's' : '') + ' de catastrophe naturelle depuis ' + yr(RK.catnat[RK.catnat.length - 1]) + ' : ' + parts.join(', ') + '.', 'info');
    text('Pourquoi c\'est utile : ces arrêtés montrent les événements qui ont déjà touché la commune et qui ont été indemnisés par les assurances. Ils ne signifient pas que ce terrain a été touché, mais ils indiquent les risques à surveiller ; le vendeur doit déclarer dans l\'état des risques les sinistres indemnisés sur le bien.', { size: 9 });
  } else text('Aucun arrêté de catastrophe naturelle n\'a été pris pour la commune : aucun événement naturel majeur n\'y a été reconnu par l\'État.', { size: 9.5 });
  if (RK.icpe && RK.icpe.length) {
    h3('Installations classées à moins de 1 km');
    text('Ce sont des activités (industrie, commerce, entrepôt, élevage...) soumises à une surveillance de l\'État pour l\'environnement. Pour un acheteur, elles peuvent signifier du bruit, du trafic ou des odeurs ; elles n\'imposent pas de règle de construction, sauf plan de prévention des risques technologiques.', { size: 9 });
    RK.icpe.forEach(i => bullet(i.replace(/ · Autres régimes/i, ' · activité suivie hors régime d\'autorisation').replace(/ · Enregistrement/i, ' · régime d\'enregistrement').replace(/ · Autorisation/i, ' · régime d\'autorisation (le plus surveillé)'), { size: 9 }));
  }
  if (RK.ssp && RK.ssp.length) { h3('Sols pollués à proximité'); text('Anciens sites d\'activité ou sites pollués recensés autour du terrain : un diagnostic de sol est conseillé avant d\'acheter si le terrain en est proche.', { size: 9 }); RK.ssp.forEach(i => bullet(i, { size: 9 })); }
  h3('Rapport officiel Géorisques');
  if (d.georisquesPdf && d.georisquesPdf.bytes) text('Le rapport officiel de risques édité par Géorisques, service public d\'information sur les risques, est reproduit intégralement en annexe B de ce document.', { size: 9.5 });
  else text('À quoi il sert : c\'est le document officiel de l\'État sur les risques à l\'adresse du terrain, daté du jour où vous l\'éditez. Il sert à remplir l\'état des risques à remettre à l\'acheteur ou au locataire. Il s\'édite sans frais en saisissant l\'adresse sur le site Géorisques.', { size: 9.5 });
"""
cut("  const riskTable = (title, list) => {", "  {\n    ensure(40); const t = 'Éditer le rapport officiel Géorisques'", new5, 'risques')
open(p, 'w', encoding='utf-8').write(s); print('ok A')
