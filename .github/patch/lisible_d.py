"""Lisibilité D : chapitres 9 à 12 expliqués (F/G, loyers, contrôles, copropriété, services avec contacts, données techniques, étapes concises, ERP)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag, n=1):
    global s
    c = s.count(a)
    if c != n: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)
def cut(start, end, new, tag, keep_end=True):
    global s
    i = s.find(start); j = s.find(end, i + 1)
    if i < 0 or j < 0 or s.count(start) != 1: print('ANCRE', tag, i, j, s.count(start)); sys.exit(1)
    s = s[:i] + new + s[j:]

# 9.2 F/G
rep("      text('Logements diagnostiqués F ou G dans un rayon de 350 m. Leur location est déjà interdite (G) ou le sera en 2028 (F) : leurs propriétaires sont souvent vendeurs, ou doivent engager des travaux de rénovation.', { size: 9.5 });",
    "      text('Logements diagnostiqués F ou G (les moins performants) à moins de 350 m, d\\'après la base officielle des diagnostics de performance énergétique de l\\'ADEME (DPE réalisés depuis juillet 2021).', { size: 9.5 });\n      note('À quoi ça sert : ces logements ne pourront plus être loués (G depuis 2025, F en 2028) sans travaux de rénovation. Leurs propriétaires sont souvent prêts à vendre : pour un agent immobilier, ce sont des mandats à prospecter ; pour un acheteur ou un investisseur, des biens à rénover, à négocier.', 'info');", 'fg')

# 10.1 Loyers
cut("      h3('Prix et loyers du secteur');", "      h3('Diagnostic de performance énergétique');", r"""      h3('Loyers du secteur');
      const PX = P.prix, LY = P.loyers;
      if (LY && (LY.mai || LY.app)) {
        text('Combien se loue un logement sur la commune, d\'après les annonces : utile pour estimer un futur loyer ou la rentabilité d\'un investissement.', { size: 9.5 });
        const ex = (l, sf) => 'environ ' + fmt(Math.round(l.m2 * sf / 10) * 10) + ' € par mois';
        const rows = [];
        if (LY.mai) rows.push(['Maison', m2e(LY.mai.m2) + ' par mois', 'Maison de 100 m² : ' + ex(LY.mai, 100), m2e(LY.mai.lo) + ' à ' + m2e(LY.mai.hi)]);
        if (LY.app) rows.push(['Appartement', m2e(LY.app.m2) + ' par mois', 'Appartement de 50 m² : ' + ex(LY.app, 50), m2e(LY.app.lo) + ' à ' + m2e(LY.app.hi)]);
        table([{ label: 'LOGEMENT', w: 0.17, bold: true }, { label: 'LOYER AU M²', w: 0.2, bold: true }, { label: 'EXEMPLE', w: 0.38 }, { label: 'FOURCHETTE', w: 0.25 }], rows, { size: 8.5 });
        if (LY.mai && LY.app && LY.app.m2 > LY.mai.m2) text('Le loyer au m² d\'un appartement est souvent plus élevé que celui d\'une maison : les petites surfaces se louent plus cher au m², mais le loyer total d\'une maison reste plus élevé.', { size: 9 });
        const yl = [];
        if (PX && PX.maison && PX.maison.median && LY.mai) yl.push('maison ' + (LY.mai.m2 * 12 / PX.maison.median * 100).toFixed(1).replace('.', ',') + ' % (prix médian de vente ' + fmt(Math.round(PX.maison.median)) + ' €/m²)');
        if (PX && PX.appartement && PX.appartement.median && LY.app) yl.push('appartement ' + (LY.app.m2 * 12 / PX.appartement.median * 100).toFixed(1).replace('.', ',') + ' % (prix médian de vente ' + fmt(Math.round(PX.appartement.median)) + ' €/m²)');
        if (yl.length) text('Rendement locatif brut sur la commune (loyer de l\'année divisé par le prix d\'achat) : ' + yl.join(', ') + '.', { size: 9 });
        text('Sources : loyers d\'annonce par m² (charges comprises) de la Carte des loyers ' + (LY.annee || 2025) + ' du ministère chargé du logement' + (((LY.mai && !LY.mai.commune) || (LY.app && !LY.app.commune)) ? ', estimés sur un groupe de communes voisines faute d\'annonces suffisantes' : '') + ' ; prix de vente médians de la commune (DVF, DGFiP).', { size: 8, color: C.muet });
      } else text('Les loyers ne sont pas publiés pour cette commune par la Carte des loyers du ministère chargé du logement.', { size: 9.5 });
""", 'loyers')
# 10.2 DPE : déjà présenté au chapitre 1 (tableau avec les étiquettes) : supprimé ici
cut("      h3('Diagnostic de performance énergétique');", "    }\n    {\n      h3('Points à contrôler avant la vente');", "", 'dpe102')

# 10.3 Points à contrôler : seulement ceux qui concernent la parcelle, avec la raison
cut("      const rows = [\n        ['Document d\\'urbanisme et zone'", "      text('Ces résultats proviennent des bases officielles publiées en ligne", r"""      const abfT = d.verdict && d.verdict.abf === 'sur' ? (/à prévoir/.test(String(d.verdict.title || '')) ? 'Accord de l\'architecte à prévoir (terrain visible depuis le monument)' : 'Accord de l\'architecte obligatoire') : d.verdict && d.verdict.abf === 'probable' ? 'Avis de l\'architecte probable' : '';
      const zU = (d.zones || []).some(z => /^(U|AU)/i.test(String(z.code || '')));
      const rows = [
        ['Document d\'urbanisme et zone', d.doc ? d.doc.typeLabel + (zc.length ? ' · zone ' + zc.join(', ') : '') : (zc.length ? 'Zone ' + zc.join(', ') : 'Zone non publiée'), 'Fixe ce qui peut être construit.'],
        sup.length ? ['Servitudes d\'utilité publique', (() => { const m = {}; sup.forEach(x => { m[x.typeLabel] = 1; }); return Object.keys(m).join(' ; '); })(), 'S\'imposent au permis de construire.'] : null,
        inf.length ? ['Droit de préemption urbain', 'Périmètre publié : ' + inf.slice(0, 2).join(' ; '), 'La mairie peut acheter en priorité : la vente doit lui être déclarée (DIA).'] : zU ? ['Droit de préemption urbain', 'Probable en zone urbaine, à confirmer en mairie', 'La mairie peut acheter en priorité : la vente doit lui être déclarée (DIA).'] : null,
        agri ? ['Préemption SAFER', 'Terrain ' + (agriPart ? 'en partie ' : '') + 'en zone agricole ou naturelle (' + zAN.map(z => z.code).join(', ') + ')', 'La SAFER peut acheter en priorité.'] : null,
        abfT ? ['Architecte des Bâtiments de France', abfT, 'Conditionne le permis de construire.'] : null,
        ['État des risques (ERP)', 'Formulaire pré-rempli au dernier chapitre', 'Obligatoire, à remettre à l\'acheteur dès la promesse de vente.'],
        (RKp.catnat || []).length ? ['Catastrophes naturelles', RKp.catnat.length + ' arrêté' + (RKp.catnat.length > 1 ? 's' : '') + ' sur la commune', 'Les sinistres indemnisés sur le bien doivent être déclarés dans l\'état des risques.'] : null,
        RKp.sis && RKp.sis.length ? ['Sols pollués', 'Secteur d\'information sur les sols : ' + RKp.sis.join(', '), 'Étude de sol obligatoire avant de construire.'] : null,
        P.copro && P.copro.length ? ['Copropriété', P.copro.length > 1 ? P.copro.length + ' copropriétés sur la parcelle' : '1 copropriété sur la parcelle', 'Règlement, charges et procès-verbaux à remettre à l\'acheteur.'] : null
      ].filter(Boolean);
      text('Seuls les points qui concernent cette parcelle sont listés.', { size: 9 });
      table([{ label: 'Point', w: 0.26, bold: true }, { label: 'Résultat', w: 0.4 }, { label: 'Pourquoi le contrôler', w: 0.34 }], rows, { size: 8.5 });
""", 'controles')
# 10.4 Copropriété : seulement si elle existe
cut("    {\n      h3('Copropriété');", "    {\n      h3('Écoles, commerces, santé et gares');", r"""    if (P.copro && P.copro.length) {
      h3('Copropriété');
      text('Une copropriété est immatriculée sur la parcelle. À quoi ça sert : l\'acheteur d\'un lot est soumis à son règlement (usage des lots, travaux) et à ses charges ; le syndic fournit les documents à remettre avant la vente (règlement, procès-verbaux d\'assemblée, montant des charges).', { size: 9.5 });
      P.copro.slice(0, 3).forEach(x => kvn([['Copropriété', (x.nom || 'Sans nom d\'usage') + ' · immatriculation ' + x.immat], ['Lots', [x.lots ? fmt(x.lots) + ' lots' : '', x.hab ? fmt(x.hab) + ' à usage d\'habitation' : '', x.park ? fmt(x.park) + ' de stationnement' : ''].filter(Boolean).join(', ')], ['Construction', x.periode], ['Règlement de copropriété', x.reglement], ['Syndic (contact)', [x.syndic, x.mandat].filter(Boolean).join(' · ')], ['Fiche officielle', 'https://www.registre-coproprietes.gouv.fr/']]));
      text('Source : registre national d\'immatriculation des copropriétés (ANAH), données déclarées par les syndics.', { size: 8, color: C.muet });
    }
""", 'copro')
# 10.5 Services avec contacts
rep("        table([{ label: 'Service', w: 0.3, bold: true }, { label: 'Le plus proche', w: 0.48 }, { label: 'Distance', w: 0.22 }], PR.map(x => x.ko ? [x.cat, 'Source momentanément indisponible', '—'] : x.aucun ? [x.cat, 'Aucun à moins de ' + fmt(x.r / 1000) + ' km', '—'] : x.n ? [x.cat, fmt(x.n) + ' établissements à moins de ' + (x.r < 1000 ? fmt(x.r) + ' m' : fmt(x.r / 1000) + ' km'), 'moins de ' + (x.r < 1000 ? fmt(x.r) + ' m' : fmt(x.r / 1000) + ' km')] : [x.cat, x.nom || 'Nom non renseigné', dist(x.d)]));",
    "        table([{ label: 'Service', w: 0.2, bold: true }, { label: 'Le plus proche', w: 0.34 }, { label: 'Distance', w: 0.12 }, { label: 'Contact', w: 0.34 }], PR.map(x => x.ko ? [x.cat, 'Source momentanément indisponible', '—', ''] : x.aucun ? [x.cat, 'Aucun à moins de ' + fmt(x.r / 1000) + ' km', '—', ''] : x.n ? [x.cat, fmt(x.n) + ' établissements à moins de ' + (x.r < 1000 ? fmt(x.r) + ' m' : fmt(x.r / 1000) + ' km'), '—', ''] : [x.cat, x.nom || 'Nom non renseigné', dist(x.d), [x.tel, x.mail].filter(Boolean).join(' · ') || '–']), { size: 8.5 });", 'proxT')
rep("        text('Distances à vol d\\'oiseau depuis le centre de la parcelle. Sources : annuaire de l\\'Éducation nationale' + (/^2[AB]/.test(R.insee) ? '' : ', gares de voyageurs SNCF') + ' et répertoire Sirene de l\\'INSEE (établissements actifs : boulangerie 10.71C, supérette 47.11B-C, supermarché 47.11D-F, pharmacie 47.73Z, médecin généraliste 86.21Z).', { size: 8.5, color: C.muet });",
    "        text('Distances à vol d\\'oiseau depuis le centre de la parcelle. Sources : annuaire de l\\'Éducation nationale (écoles, avec téléphone et courriel pour les inscriptions)' + (/^2[AB]/.test(R.insee) ? '' : ', gares de voyageurs SNCF') + ', OpenStreetMap pour le nom commercial des magasins et le répertoire Sirene de l\\'INSEE (établissements actifs).', { size: 8, color: C.muet });", 'proxS')
# proximite : nom commercial (OpenStreetMap), téléphone et courriel des écoles
rep("&limit=6&select=nom_etablissement,position,statut_public_prive`;", "&limit=6&select=nom_etablissement,position,statut_public_prive,telephone,mail`;", 'ecoSel')
rep("      out.push(r && r.position ? { cat: lab, nom: r.nom_etablissement + (r.statut_public_prive ? ' (' + String(r.statut_public_prive).toLowerCase() + ')' : ''), d: Math.round(dm(r.position.lat, r.position.lon)) } : { cat: lab, aucun: true, r: 15000 });",
    "      out.push(r && r.position ? { cat: lab, nom: String(r.nom_etablissement || '').replace(/^Ecole/, 'École') + (r.statut_public_prive ? ' (' + String(r.statut_public_prive).toLowerCase() + ')' : ''), d: Math.round(dm(r.position.lat, r.position.lon)), tel: r.telephone || '', mail: r.mail || '' } : { cat: lab, aucun: true, r: 15000 });", 'ecoOut')
rep("  const sirene = async (lab, naf) => {", r"""  const TCs = t => t && t === t.toUpperCase() ? t.toLowerCase().replace(/(^|[\s'’-])(\p{L})/gu, (x, a, b) => a + b.toUpperCase()).replace(/\b(De|Du|Des|La|Le|Les|Et|D'|L'|Sarl|Sas|Eurl)\b/g, w => /^(Sarl|Sas|Eurl)$/.test(w) ? w.toUpperCase() : w.toLowerCase()) : t;
  let OSM = null;
  try {
    const q = `[out:json][timeout:12];(nwr(around:3000,${lat.toFixed(6)},${lon.toFixed(6)})[shop~"^(bakery|convenience|supermarket)$"];nwr(around:3000,${lat.toFixed(6)},${lon.toFixed(6)})[amenity=pharmacy];);out center tags 300;`;
    const x = await fetch('https://overpass-api.de/api/interpreter', { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'TerrenUrbanisme/1.0' }, signal: AbortSignal.timeout(14000) });
    if (x.ok) OSM = ((await x.json()).elements || []).map(e => { const t = e.tags || {}, la = e.lat || (e.center && e.center.lat), lo = e.lon || (e.center && e.center.lon); return la && lo ? { k: t.shop || t.amenity, nom: t.name || t.brand || '', tel: t.phone || t['contact:phone'] || '', mail: t.email || t['contact:email'] || '', d: dm(la, lo) } : null; }).filter(e => e && e.nom);
  } catch (e) { console.warn('OSM commerces', String(e && e.message || e).slice(0, 80)); }
  const OSMK = { 'Boulangerie': ['bakery'], 'Supérette': ['convenience'], 'Supermarché ou hypermarché': ['supermarket'], 'Pharmacie': ['pharmacy'] };
  const sirene = async (lab, naf) => {""", 'osm')
rep("      if (E.length && E[0].d <= r * 1000 * 1.05) { out.push({ cat: lab, nom: String(E[0].nom).replace(/\\s+/g, ' ').trim(), d: Math.round(E[0].d) }); return; }",
    "      if (E.length && E[0].d <= r * 1000 * 1.05) { const os = OSM && OSMK[lab] ? OSM.filter(o => OSMK[lab].includes(o.k)).sort((a, b) => a.d - b.d)[0] : null; if (os && os.d <= E[0].d + 150) out.push({ cat: lab, nom: os.nom, d: Math.round(os.d), tel: os.tel, mail: os.mail }); else out.push({ cat: lab, nom: TCs(String(E[0].nom).replace(/\\s+/g, ' ').trim()), d: Math.round(E[0].d) }); return; }", 'sirOut')

# 10.6 Foncier : intro, sans doublons (voisins et servitudes déjà présentés)
rep("      h3('Foncier et division');", "      h3('Foncier et division');\n      text('À quoi ça sert : l\\'identifiant cadastral est à reporter dans la promesse de vente ; la surface du cadastre est indicative, seul un géomètre fixe la surface réelle ; ces règles disent si le terrain peut être découpé en plusieurs lots.', { size: 9.5 });", 'fonc')
rep("        ['Parcelles voisines', (d.neighbors || []).length ? d.neighbors.join(', ') : null],\n        ['Surface minimale de terrain', K.minTerrain ? fmt(K.minTerrain) + ' m² exigés par le règlement de la zone' : 'Aucune surface minimale relevée dans le règlement de la zone'],\n        ['Servitudes d\\'utilité publique', sup.length ? sup.map(x => x.typeLabel).filter((v, i, a) => a.indexOf(v) === i).slice(0, 4).join(' ; ') : 'Aucune publiée au Géoportail de l\\'Urbanisme']\n      ]);",
    "        ['Surface minimale de terrain', K.minTerrain ? fmt(K.minTerrain) + ' m² exigés par le règlement de la zone' : 'Aucune surface minimale relevée dans le règlement de la zone']\n      ]);", 'foncRows')

# 10.7 Cadre technique : à quoi sert chaque donnée
i = s.find("      h3('Cadre technique du terrain');\n      const ZC = P.zclim;\n      kvn([")
j = s.find("      ]);\n      if (ZC && !ZC.dom) text('Zones climatiques", i)
if i < 0 or j < 0: print('ANCRE cadre'); sys.exit(1)
blk = s[i:j]
blk = blk.replace("      kvn([", "      text('Les données à transmettre à l\\'architecte, au bureau d\\'études et au constructeur pour préparer le permis et chiffrer le projet.', { size: 9.5 });\n      const USE = { 'Zone du document d\\'urbanisme': 'Fixe les règles du permis', 'Emprise au sol maximale': 'Surface au sol maximale de toutes les constructions', 'Hauteur': 'Limite le nombre d\\'étages', 'Recul des limites séparatives': 'Distance minimale avec les voisins', 'Zone climatique RE2020': 'Pour l\\'étude thermique jointe au permis', 'Zone de sismicité': 'Règles parasismiques de la structure (zones 3 à 5)', 'Retrait-gonflement des argiles': 'Étude de sol obligatoire si aléa moyen ou fort', 'Potentiel radon': 'Ventilation et étanchéité du plancher bas', 'Altitude et pente': 'Coût des fondations, terrassements et accès', 'Assainissement': 'Égouts ou fosse : coût et étude de sol' };\n      const KV = [", 1)
s = s[:i] + blk + "      ];\n      table([{ label: 'DONNÉE', w: 0.27, bold: true }, { label: 'VALEUR', w: 0.4 }, { label: 'À QUOI ÇA SERT', w: 0.33 }], KV.filter(x => x[1] != null && x[1] !== '').map(x => [x[0], x[1], USE[x[0]] || '']), { size: 8.5 });\n" + s[j + len("      ]);\n"):]

# 11.2 Étapes concises
i = s.find("    text('Les étapes ci-dessous suivent l\\'ordre réel d\\'un projet de construction")
j = s.find("    ET.forEach((s0, i) => {", i)
k = s.find("    });\n  }\n  h3('Les points à vérifier pour ce terrain');", j)
if i < 0 or j < 0 or k < 0: print('ANCRE etapes', i, j, k); sys.exit(1)
rga = "/moyen|fort/i.test(String((d.risques || {}).rga || ''))"
newET = r"""    text('Ce qu\'il faut faire, dans l\'ordre, avec le coût et la personne à contacter. Montants indicatifs, à confirmer par devis.', { size: 9.5 });
    const ET = [
      ['Avant d\'acheter le terrain', ['Demander un certificat d\'urbanisme opérationnel (Cerfa 13410) : il fige les règles 18 mois.', 'Faire chiffrer les raccordements (eau, électricité, égouts).', RGAX ? 'Le vendeur doit fournir l\'étude de sol préalable (argiles d\'aléa moyen ou fort).' : '', 'Mettre dans le compromis une condition « obtention du permis ».'].filter(Boolean), 'Sans frais · réponse sous 2 mois', 'Mairie : ' + mair],
      ['Les études obligatoires', ['Étude de sol (G2), pour les fondations : 1 500 à 3 000 €.', 'Étude thermique RE2020, jointe au permis : 500 à 1 500 €.', 'Bornage par un géomètre, si les limites sont incertaines.'], '', (d.geometres && d.geometres.length ? 'Géomètres proches : liste à la fin de ce chapitre' : 'Géomètres : geometre-expert.fr')],
      ['Les plans', ['Architecte obligatoire au-delà de 150 m² de surface de plancher : 3 000 à 8 000 € pour le permis, 8 à 12 % des travaux pour la mission complète.', 'En dessous : dessinateur ou maître d\'œuvre, 1 500 à 4 000 €.'], '', 'Architectes : architectes.org'],
      ['Déposer le permis', ['Cerfa 13406 et plans PCMI1 à PCMI8, en mairie ou en ligne.', 'Réponse en 2 mois après dossier complet, 1 mois de plus en secteur protégé.'], 'Sans frais', 'Mairie : ' + mair],
      ['Affichage et recours', ['Panneau sur le terrain, visible de la rue, pendant tout le chantier.', 'Les voisins peuvent contester pendant 2 mois.'], 'Constat d\'affichage par commissaire de justice : 300 à 600 €', 'Commissaires de justice : commissaire-justice.fr'],
      ['Avant les travaux', ['Assurance dommages-ouvrage, obligatoire.', 'Déclaration d\'ouverture de chantier (Cerfa 13407) le jour du démarrage.', 'Le permis est valable 3 ans, prolongeable deux fois un an.'], 'Assurance : 2 à 4 % du coût de la construction', 'Mairie : ' + mair],
      ['Le financement', ['La banque paie au fur et à mesure du chantier.', 'Avec un constructeur : 15 % à l\'ouverture, 25 % fondations, 40 % murs, 60 % hors d\'eau, 75 % hors d\'air, 95 % équipements, solde à la réception.'], '', 'Votre banque ou votre courtier'],
      ['La fin du chantier', ['Réception des travaux, avec réserves si besoin.', 'Déclaration d\'achèvement (Cerfa 13408) et attestation RE2020.'], 'Sans frais', 'Mairie : ' + mair],
      ['Les impôts', ['Déclarer la construction sur impots.gouv.fr dans les 90 jours.', 'Taxe d\'aménagement : estimation plus bas.'], '', 'impots.gouv.fr › Gérer mes biens immobiliers']
    ];
    ET.forEach((s0, i) => {
      const L1 = s0[1].map(t => wrap('• ' + t, F, 9, CW - 30)), lc = s0[3] ? wrap(s0[3], F, 8.5, CW - 30) : [], lk = s0[2] ? wrap('Coût : ' + s0[2], B, 9, CW - 30) : [];
      ensure(L1.flat().length * 12.5 + lk.length * 12.5 + lc.length * 12 + 30);
      page.drawCircle({ x: M + 9, y: y - 9, size: 9, color: C.t });
      page.drawText(String(i + 1), { x: M + 9 - tw(String(i + 1), B, 9) / 2, y: y - 12, size: 9, font: B, color: C.white });
      page.drawText(clean(s0[0]), { x: M + 28, y: y - 12, size: 10.5, font: B, color: C.ink }); y -= 18;
      L1.forEach(ls => ls.forEach((l, li) => { page.drawText(li ? '  ' + l : l, { x: M + 28, y: y - 9, size: 9, font: F, color: C.ink }); y -= 12.5; }));
      lk.forEach(l => { page.drawText(l, { x: M + 28, y: y - 9, size: 9, font: B, color: C.ink }); y -= 12.5; });
      lc.forEach(l => { page.drawText(l, { x: M + 28, y: y - 9, size: 8.5, font: F, color: C.t }); y -= 12; });
      y -= 8;
"""
s = s[:i] + newET.replace('RGAX', rga) + s[k:]

# ERP expliqué
rep("    note('Formulaire pré-rempli à partir de Géorisques et du Géoportail de l\\'Urbanisme à la date du rapport. Avant de le remettre",
    "    text('À quoi sert ce chapitre : pour vendre ou louer, le propriétaire doit remettre à l\\'acheteur ou au locataire un état des risques (ERP). Ce chapitre est ce formulaire, déjà rempli avec les données officielles : il reste à le vérifier, à cocher la case des sinistres et à le signer.', { size: 9.5 });\n    note('Formulaire pré-rempli à partir de Géorisques et du Géoportail de l\\'Urbanisme à la date du rapport. Avant de le remettre", 'erp0')
rep("    h3('Autres zonages réglementaires');", "    h3('Autres zonages réglementaires');\n    text('Les autres questions obligatoires du formulaire. Chaque « Oui » doit être porté à la connaissance de l\\'acheteur ou du locataire ; « À vérifier » signifie que la donnée publique ne permet pas de répondre avec certitude.', { size: 9 });", 'erp3')
rep("    text('Arrêtés de catastrophe naturelle sur la commune : ' + ((RKe.catnat || []).length || 0) + ' (liste en section Risques). Le vendeur ou le bailleur déclare ci-dessous les sinistres ayant donné lieu à une indemnisation au titre des catastrophes naturelles ou technologiques pendant la période où il a été propriétaire.', { size: 9.5 });",
    "    text('Dernière partie du formulaire, à remplir par le propriétaire : a-t-il été indemnisé par son assurance après une catastrophe naturelle ou technologique (inondation, sécheresse, glissement...) pendant qu\\'il possédait le bien ? Il coche Oui ou Non, puis le propriétaire et l\\'acheteur ou le locataire datent et signent. La commune compte ' + ((RKe.catnat || []).length || 0) + ' arrêté' + (((RKe.catnat || []).length || 0) > 1 ? 's' : '') + ' de catastrophe naturelle (chapitre Risques).', { size: 9.5 });", 'erp4')
open(p, 'w', encoding='utf-8').write(s); print('ok D')
