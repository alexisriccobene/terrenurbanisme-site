# Rapport synthétique (2 pages, 9,90 €) et passage au rapport complet (+10 €)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:80]))
    s = s.replace(old, new)

SYNTH = r"""
  // =====================================================================
  // RAPPORT SYNTHÉTIQUE : l'essentiel en deux pages
  // =====================================================================
  if (opt.synth) {
    const SURF = R.areaCalc || R.contenance, m2 = v => fmt(Math.round(v / 10) * 10) + ' m²';
    const zl = (d.zones || []).filter(z => z.share >= 0.03), MULTI = zl.length > 1;
    const cut = (t, n) => { t = String(t || '').trim(); if (t.length <= n) return t; const k = t.lastIndexOf('. ', n); return (k > n * 0.5 ? t.slice(0, k + 1) : t.slice(0, n).replace(/\s+\S*$/, '') + '…'); };
    CUR = 'Rapport synthétique'; newPage();
    page.drawText('RAPPORT D\'URBANISME SYNTHÉTIQUE', { x: M, y: y - 8, size: 9, font: B, color: C.t });
    wrap(R.commune, B, 22, CW).slice(0, 1).forEach(l => page.drawText(l, { x: M, y: y - 34, size: 22, font: B, color: C.ink }));
    page.drawText(clean('Section ' + R.section + ' · Parcelle n° ' + R.numero + ' · établi le ' + d.date), { x: M, y: y - 52, size: 10, font: Md, color: C.muet });
    y -= 68;
    // Verdict
    {
      const [vc, vbg] = VC[d.verdict.key];
      const tl = wrap(d.verdict.title, B, 14, CW - 44), why = wrap(d.verdict.why, F, 9.5, CW - 44).slice(0, 7), bh = 40 + tl.length * 18 + why.length * 13.5;
      page.drawRectangle({ x: M, y: y - bh, width: CW, height: bh, color: vbg });
      page.drawRectangle({ x: M, y: y - bh, width: 5, height: bh, color: vc });
      page.drawText(clean(d.verdict.word.toUpperCase()), { x: M + 22, y: y - 22, size: 9, font: B, color: vc });
      tl.forEach((l, i) => page.drawText(l, { x: M + 22, y: y - 42 - i * 18, size: 14, font: B, color: C.ink }));
      why.forEach((l, i) => page.drawText(l, { x: M + 22, y: y - 46 - tl.length * 18 - i * 13.5 + 6, size: 9.5, font: F, color: C.ink }));
      y -= bh + 14;
    }
    // Carte : zones du PLU sur la vue aérienne, à défaut vue aérienne et cadastre
    {
      const zo = (await img(I.zortho)) || ortho, zbb = I.zortho ? I.zbbox : I.bbox;
      if (d.zoneShapes && d.zoneShapes.length && zo && zbb) mapBox([{ img: zo, opacity: 0.85 }], zbb, { h: 205, title: d.doc.type === 'CC' ? 'Le terrain sur la carte communale' : 'Le terrain sur le plan de zonage', shapes: d.zoneShapes, parcel: d.parcelCoords, caption: (d.doc.local ? 'Plan de zonage officiel de la commune, recalé sur le cadastre' : 'Zonage : Géoportail de l\'Urbanisme') + ' · fond : © IGN · terrain entouré' });
      else if (ortho && I.bbox) mapBox([{ img: ortho }, { img: cadastre, opacity: 0.8 }], I.bbox, { h: 205, title: 'Le terrain', parcel: d.parcelCoords, caption: 'Photographie aérienne et plan cadastral · © IGN' });
    }
    // L'essentiel
    const A0 = d.reglement && d.reglement.analysis;
    let assain = null;
    {
      const AS = String((A0 && A0.assainissement) || ''), inf = (d.infos || []).concat(d.prescriptions || []).filter(p => /assainiss|eaux us/i.test(p.label || ''));
      const Z0a = d.zones && d.zones[0], tz = String((Z0a && Z0a.tz) || '').toUpperCase(), EAa = d.eau || {}, AC = EAa.ac, connu = !!EAa.sispea;
      const zColl = inf.find(p => /collectif/i.test(p.label || '') && !/non[- ]?collectif/i.test(p.label || '')), zAnc = inf.find(p => /non[- ]?collectif|autonome|individuel/i.test(p.label || ''));
      assain = zColl && !zAnc ? 'Tout-à-l\'égout (zone d\'assainissement collectif)' : zAnc && !zColl ? 'Assainissement individuel (fosse ou micro-station)' : /^U/.test(tz) && (AC || !connu) ? 'Tout-à-l\'égout très probable (zone urbaine)' : connu && !AC ? 'Assainissement individuel : pas de réseau collectif sur la commune' : /^AU/.test(tz) && AC ? 'Tout-à-l\'égout prévu avec l\'aménagement de la zone' : 'Assainissement individuel probable (hors zone urbaine)';
      if (!AS && !d.eau && !Z0a) assain = null;
    }
    const AC = d.acces, E = d.elec, FB = d.fibre;
    const dbt = E && E.checked ? (E.bt ? E.bt.d : null) : undefined;
    const OPf = FB && !FB.none && FB.onParcel ? FB.onParcel.filter(o => o.fibre) : [];
    h3('L\'essentiel en un coup d\'œil', 60);
    kvn([
      ['Surface du terrain', fmt(R.contenance || R.areaCalc) + ' m²' + (R.contenance && R.areaCalc && Math.abs(R.contenance - R.areaCalc) / R.contenance > 0.25 ? ' au cadastre (' + fmt(R.areaCalc) + ' m² sur le plan : à faire confirmer par un géomètre)' : '')],
      ['Document d\'urbanisme', d.doc.typeLabel + (d.doc.date ? ', approuvé le ' + d.doc.date : '')],
      [MULTI ? 'Zones du terrain' : 'Zone du terrain', zl.length ? zl.map(z => z.code + ' (' + z.typeLabel.toLowerCase() + ')' + (MULTI ? ' : ' + m2(z.share * SURF) + ', ' + Math.round(z.share * 100) + ' %' : '') + ', ' + z.verdictWord.toLowerCase()).join(' ; ') : (d.doc.rnu ? 'Règlement national d\'urbanisme' : 'Zone non publiée en ligne : à consulter en mairie')],
      ['Accès', AC ? (AC.direct ? 'Accès direct à une voie' + (AC.contact && AC.contact[0] && AC.contact[0].nom ? ' (' + AC.contact[0].nom + ')' : '') : AC.nearest ? 'Pas d\'accès direct identifié · voie la plus proche à ' + fmt(AC.nearest.d) + ' m' : 'Aucune voie carrossable à moins de 400 m') : null],
      ['Eaux usées', assain],
      ['Électricité', dbt === undefined ? null : dbt == null ? 'Aucun réseau basse tension à proximité : raccordement lourd' : dbt <= 30 ? 'Réseau à ' + (dbt === 0 ? 'moins de 5' : fmt(Math.max(5, Math.round(dbt / 5) * 5))) + ' m : branchement simple probable' : dbt <= 100 ? 'Réseau à environ ' + fmt(Math.round(dbt / 5) * 5) + ' m : extension probable' : 'Réseau à environ ' + fmt(Math.round(dbt / 5) * 5) + ' m : extension importante'],
      ['Fibre', FB && !FB.none && FB.nearest ? (OPf.length ? 'Terrain déjà raccordable' : FB.nearestFibre ? 'Point fibré le plus proche à ' + fmt(FB.nearestFibre.d) + ' m' : 'Aucun point fibré à moins de 400 m') : null]
    ], { lw: 0.3 });

    // Page 2
    newPage();
    h3('Ce que vous pouvez construire', 60);
    const K = d.calc || {}, RG = d.reglement;
    const KEY = /emprise|hauteur|limites s[ée]paratives|par rapport aux voies|voies et emprises/i;
    const zoneBlock = (code, an, z, main) => {
      if (!an) return;
      const rg = (an.regles || []).filter(r => r && r.critere && r.regle && KEY.test(r.critere) && !/^Non (précisé|réglementé)/i.test(r.regle)).slice(0, 4);
      if (MULTI) h4('Zone ' + code + (z ? ' · ' + z.verdictWord.toLowerCase() + (z.share ? ' · ' + m2(z.share * SURF) : '') : ''), 60);
      if (z && z.v === 'non' || (main && K.neuf === false)) {
        text('Pas de construction nouvelle de logement, sauf exceptions. Restent possibles notamment :', { size: 9.5, after: 2 });
        (an.autorise || []).slice(0, 3).forEach(t => bullet(cut(t, 150), { size: 9 }));
      } else if (rg.length) table([{ label: 'RÈGLE', w: 0.3, bold: true }, { label: 'CE QUE DIT LE RÈGLEMENT', w: 0.7 }], rg.map(r => [r.critere, cut(r.regle, 190)]), { size: 8.5 });
    };
    if (RG && RG.analysis) {
      zoneBlock(RG.zone, RG.analysis, zl.find(z => z.code === RG.zone), true);
      (RG.others || []).forEach(o => zoneBlock(o.zone, o.analysis, zl.find(z => z.code === o.zone), false));
      if (K.footprint && K.neuf !== false && !MULTI) note('En clair : ' + (K.empPct != null ? 'jusqu\'à ' + fmt(K.footprint) + ' m² de construction au sol (emprise de ' + K.empPct + ' %)' : 'pas de plafond d\'emprise au sol ; la construction doit rester en retrait des limites et des voies') + (K.H ? ', ' + String(K.H).replace('.', ',') + ' m de hauteur au plus' : '') + (d.implant && d.implant.ok ? '. Une maison d\'environ ' + fmt(d.implant.hab) + ' m² habitables y trouve sa place.' : '.'), 'ok');
    } else if (d.doc && (d.doc.type === 'CC' || d.doc.rnu)) text('Les règles de construction sont celles du règlement national d\'urbanisme : la mairie apprécie chaque projet au regard de son insertion dans le site et de la desserte par les réseaux.', { size: 9.5 });
    else text('Le règlement de la zone n\'a pas pu être lu automatiquement : il est à consulter en mairie.', { size: 9.5 });
    const pts = (d.points || []).filter(pt => !/^Zone /.test(pt.text) && pt.key !== 'ok').slice(0, 6);
    if (pts.length) { h3('Risques et contraintes à connaître', 60); pts.forEach(pt => bullet(cut(pt.text, 200), { size: 9, color: (VC[pt.key] || VC.info)[0] })); }
    // Le rapport complet
    {
      const L = ['Le règlement lu en entier, zone par zone, avec les extraits officiels et les numéros d\'articles', 'Le potentiel constructible calculé et l\'implantation d\'une maison sur le terrain', 'Prescriptions, servitudes, loi Littoral, loi Montagne' + (R.corse ? ' et PADDUC' : '') + ' en détail', 'Les risques à l\'adresse et l\'état des risques (ERP) pré-rempli, à remettre à l\'acquéreur', 'Eau, électricité, assainissement : coûts, démarches et contacts', 'Les ventes réelles autour du terrain, l\'historique aérien et les permis accordés', 'Les démarches, les délais et la taxe d\'aménagement de votre projet'];
      const lh = 13, bh = 58 + L.length * lh + 26; ensure(bh + 10);
      page.drawRectangle({ x: M, y: y - bh, width: CW, height: bh, color: C.cream });
      page.drawRectangle({ x: M, y: y - bh, width: 4, height: bh, color: C.t });
      page.drawText(clean('BESOIN DE TOUT LE DÉTAIL ?'), { x: M + 18, y: y - 20, size: 8.5, font: B, color: C.t });
      page.drawText(clean('Le rapport complet (environ 45 pages) ajoute :'), { x: M + 18, y: y - 38, size: 11.5, font: B, color: C.ink });
      L.forEach((t, i) => { page.drawCircle({ x: M + 22, y: y - 56 - i * lh + 3, size: 1.8, color: C.t }); page.drawText(clean(t), { x: M + 30, y: y - 56 - i * lh, size: 8.8, font: F, color: C.ink }); });
      const cta = 'Passez au rapport complet pour 10 € depuis votre espace : terrenurbanisme.com/espace.html';
      page.drawText(clean(cta), { x: M + 18, y: y - bh + 16, size: 9, font: B, color: C.t });
      try { linkAnnot(page, M + 18, y - bh + 12, tw(cta, B, 9), 14, SITE + '/espace.html'); } catch (e) {}
      y -= bh + 12;
    }
    text('Document d\'information établi à partir des sources publiques officielles. Il ne vaut ni certificat d\'urbanisme ni autorisation d\'urbanisme : seule la mairie se prononce sur la constructibilité d\'un terrain, au vu d\'un projet précis.', { size: 7.5, color: C.muet });
    const N = pdf.getPageCount();
    pages.forEach((p, i) => {
      p.drawLine({ start: { x: M, y: 46 }, end: { x: W - M, y: 46 }, thickness: 0.5, color: C.ligne });
      p.drawText(clean('terrenurbanisme.com · contact@terrenurbanisme.com · rapport n° ' + d.orderId), { x: M, y: 30, size: 7.5, font: F, color: C.muet });
      p.drawText(clean('Document d\'information : ne vaut pas certificat d\'urbanisme et ne peut être joint à une demande de permis de construire.'), { x: M, y: 19, size: 6.5, font: F, color: C.muet });
      const pg = (i + 1) + ' / ' + N; p.drawText(pg, { x: W - M - tw(pg, F, 7.5), y: 30, size: 7.5, font: F, color: C.muet });
    });
    return await pdf.save({ useObjectStreams: false });
  }
"""
rep("""
  // =====================================================================
  // PAGE DE GARDE
  // =====================================================================
  const cover = pdf.addPage([W, H]); pages.push(cover);""", SYNTH + """
  // =====================================================================
  // PAGE DE GARDE
  // =====================================================================
  const cover = pdf.addPage([W, H]); pages.push(cover);""")

# linkAnnot est défini plus bas (page de garde) : version locale pour le rapport synthétique
rep("  if (opt.synth) {\n    const SURF", "  if (opt.synth) {\n    const linkAnnot = (p, x, y0, w, h, uri) => { try { const a = pdf.context.obj({ Type: 'Annot', Subtype: 'Link', Rect: [x, y0, x + w, y0 + h], Border: [0, 0, 0], A: { Type: 'Action', S: 'URI', URI: PDFLib.PDFString.of(uri) } }); p.node.addAnnot(pdf.context.register(a)); } catch (e) {} };\n    const SURF")

# makeReport : option synthétique (sans annexes)
rep("  const annex = !meta.leger && reg && reg.src", "  const annex = !meta.leger && !meta.synth && reg && reg.src")
rep("  const pdf = await buildReport(PDFLib, d, { fonts, fontkit, annex, debug: meta.debug });",
    "  d.synth = !!meta.synth;\n  const pdf = await buildReport(PDFLib, d, { fonts, fontkit, annex, debug: meta.debug, synth: !!meta.synth });")

# buildAndSend : formule lue sur le dossier
rep("    const { d, pdf } = await makeReport(m, { orderRef, email, leger: !!leger, marque: marqueV || undefined });",
    "    let synth = m.formule === 'synthese';\n    if (!m.formule) { try { const { data: fo } = await admin.from('dossiers').select('formule').eq('stripe_session_id', sessionId).maybeSingle(); synth = !!(fo && fo.formule === 'synthese'); } catch (e) {} }\n    const { d, pdf } = await makeReport(m, { orderRef, email, leger: !!leger, marque: marqueV || undefined, synth });")
rep("    const file = `Rapport-TerrenUrbanisme-${d.ref.commune}",
    "    const file = `Rapport-${synth ? 'synthetique-' : ''}TerrenUrbanisme-${d.ref.commune}")

# processOrder : formule enregistrée ; passage au complet
rep("section: m.section, numero: m.numero, amount_total: s.amount_total, status: 'pending', origine: 'paiement', projet: projetCle(m.projet)",
    "section: m.section, numero: m.numero, amount_total: s.amount_total, status: 'pending', origine: 'paiement', projet: projetCle(m.projet), formule: m.formule === 'synthese' ? 'synthese' : 'complet'")
rep("  if (!m.insee) { // lot de rapports",
    """  if (m.upgrade) { // passage d'un rapport synthétique au rapport complet
    if (!(await onceOnly('upgrade/' + s.id))) return;
    const { data: row } = await admin.from('dossiers').select('*').eq('stripe_session_id', m.upgrade).eq('user_id', m.user_id).maybeSingle();
    if (!row) { console.error('passage au complet : dossier introuvable', m.upgrade); return; }
    await admin.from('dossiers').update({ formule: 'complet', status: 'pending', amount_total: (row.amount_total || 0) + (s.amount_total || 0), updated_at: new Date().toISOString() }).eq('stripe_session_id', row.stripe_session_id);
    await buildAndSend(row.stripe_session_id, { user_id: row.user_id, insee: row.insee, section: row.section, numero: row.numero, commune: row.commune, projet: row.projet, formule: 'complet' }, row.order_ref, (s.customer_details && s.customer_details.email) || row.email, row.origine);
    return;
  }
  if (!m.insee) { // lot de rapports""")
rep("Le rapport complet de la parcelle <strong>", "${d.synth ? 'Le rapport synthétique' : 'Le rapport complet'} de la parcelle <strong>")
open(p, 'w', encoding='utf-8').write(s); print('patch synthese appliqué')
