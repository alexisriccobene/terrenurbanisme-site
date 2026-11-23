# Patrimoine et architecte des Bâtiments de France : site patrimonial remarquable, sites classés ou inscrits,
# abords de monuments historiques (Géoportail, à défaut base Mérimée dans un rayon de 500 m), verdict et chapitre dédiés.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)

# 1. Collecte
rep("""  // ----- Document -----
  const docp = (dj.features || []).map(f => f.properties || {}).find(p => p.du_type) || {};""",
"""  // ----- Patrimoine (architecte des Bâtiments de France) -----
  const patrimoine = await (async () => {
    const supP_ = [...(supS.features || []), ...(supL.features || []), ...(supP.features || [])].map(f => f.properties || {});
    const nomSup = p => String(p.nomsuplitt || p.nomass || '').replace(/_/g, ' ').replace(/^AC\\d\\s*/i, '').replace(/\\s*ass$/i, '').trim();
    const PT = { spr: null, sites: [], abords: [], probables: [], gpuAc1: false };
    const ac4 = supP_.find(p => String(p.suptype || '').toLowerCase() === 'ac4');
    const tc = t => t === t.toUpperCase() ? t.toLowerCase().replace(/(^|[\\s'’-])(\\p{L})/gu, (x, a, b) => a + b.toUpperCase()).replace(/\\b(De|Du|Des|La|Le|Les|Et|Ses|Son|Sa|Au|Aux|En|D'|L')\\b/g, w => w.toLowerCase()) : t;
    const sprNom = p => { const r = nomSup(p).replace(/^site patrimonial remarquable\s*(de |d'|du |des )?/i, '').trim(); return 'Site patrimonial remarquable' + (r ? ' de ' + tc(r) : ''); };
    if (ac4) PT.spr = { nom: sprNom(ac4), reg: /^https?:\\/\\//.test(ac4.urlreg || '') ? ac4.urlreg : '', nomreg: ac4.nomreg || '', acte: ac4.fichier && ac4.partition && ac4.gpu_doc_id ? `https://data.geopf.fr/annexes/gpu/documents/${ac4.partition}/${ac4.gpu_doc_id}/${ac4.fichier}` : '' };
    PT.sites = [...new Set(supP_.filter(p => String(p.suptype || '').toLowerCase() === 'ac2').map(p => tc(nomSup(p))).filter(Boolean))].slice(0, 4);
    PT.abords = [...new Set(supP_.filter(p => String(p.suptype || '').toLowerCase() === 'ac1').map(p => nomSup(p).replace(/\\s*abor(ds)?$/i, '').replace(/-I[0-9A-Z]{5,}$/, '').replace(/-+/g, ' ').trim()).filter(Boolean))].slice(0, 6);
    // Monuments historiques à moins de 500 m (base Mérimée du ministère de la Culture)
    try {
      const [cx, cy] = centroid;
      const { data: mons } = await admin.from('monuments').select('ref, nom, commune, protection, lon, lat').gte('lat', cy - 0.0065).lte('lat', cy + 0.0065).gte('lon', cx - 0.0088).lte('lon', cx + 0.0088).limit(200);
      const lines = turf.polygonToLine(pf); const LS = lines.type === 'FeatureCollection' ? lines.features : [lines];
      const dist = (lon, lat) => { const P0 = turf.point([lon, lat]); if (turf.booleanPointInPolygon(P0, pf)) return 0; return Math.min(...LS.map(l => turf.pointToLineDistance(P0, l, { units: 'meters' }))); };
      const mh = (mons || []).map(x => ({ ref: x.ref, nom: x.nom, commune: x.commune, protection: x.protection, d: Math.round(dist(x.lon, x.lat)) })).filter(x => x.d <= 500).sort((a, b) => a.d - b.d);
      PT.mh = mh.slice(0, 8);
      // Abords publiés au Géoportail à proximité : ils font foi (périmètre délimité possible) ; sinon, rayon légal de 500 m
      if (!PT.abords.length && !PT.spr && mh.length) {
        const a1 = await safe(gq('/gpu/assiette-sup-s', near, '&categorie=AC1'), E);
        PT.gpuAc1 = !!(a1.features && a1.features.length);
        if (!PT.gpuAc1) PT.probables = mh.slice(0, 5);
      }
    } catch (e) { console.warn('monuments', String(e && e.message || e).slice(0, 120)); }
    // Règlement du site patrimonial remarquable (plan de valorisation, plan de sauvegarde ou ancienne AVAP) : lecture automatique
    if (PT.spr && PT.spr.reg && /\\.pdf($|\\?)/i.test(PT.spr.reg)) {
      try {
        const r = await analyseReglement({ code: 'SPR', typeLabel: 'Site patrimonial remarquable ' + PT.spr.nom + ' : règles applicables aux constructions neuves, extensions, clôtures, piscines, façades, toitures et menuiseries' }, PT.spr.reg, props.nom_com || m.commune, false);
        if (r && r.analysis) PT.spr.analysis = r.analysis;
      } catch (e) { console.warn('règlement SPR', String(e && e.message || e).slice(0, 120)); }
    }
    return PT;
  })();

  // ----- Document -----
  const docp = (dj.features || []).map(f => f.properties || {}).find(p => p.du_type) || {};""")
rep("    props, zones, zoneShapes, prescriptions, infos, sups, doc,", "    props, zones, zoneShapes, prescriptions, infos, sups, patrimoine, doc,")
rep("    doc: c.doc, zones, zoneShapes: c.zoneShapes, prescriptions: c.prescriptions, infos: c.infos, sups: c.sups,",
    "    doc: c.doc, zones, zoneShapes: c.zoneShapes, prescriptions: c.prescriptions, infos: c.infos, sups: c.sups, patrimoine: c.patrimoine || null,")

# 2. Verdict
rep("""  if (key === 'ok' && c.sups.some(s => s.code === 'ac1' || s.code === 'ac2' || s.code === 'ac4')) { key = 'cond'; why += ' Le terrain est situé dans un périmètre patrimonial protégé : l\\'architecte des Bâtiments de France donne son avis sur les travaux.'; }""",
"""  const PAT = c.patrimoine || { spr: null, sites: [], abords: [], probables: [] };
  let abf = '';
  if (PAT.spr || PAT.sites.length || PAT.abords.length || c.sups.some(s => s.code === 'ac1' || s.code === 'ac2' || s.code === 'ac4')) {
    abf = 'sur';
    const qui = PAT.spr ? 'dans le s' + PAT.spr.nom.slice(1) : PAT.abords.length ? 'aux abords d\\'un monument historique (' + PAT.abords.slice(0, 2).join(', ') + ')' : PAT.sites.length ? 'dans un site classé ou inscrit (' + PAT.sites[0] + ')' : 'dans un périmètre patrimonial protégé';
    why += ' Le terrain est situé ' + qui + ' : ' + (PAT.spr ? 'tout projet modifiant l\\'aspect extérieur (construction, extension, clôture, piscine, façade, toiture, menuiseries) doit recevoir l\\'accord de l\\'architecte des Bâtiments de France, qui peut imposer des prescriptions ou refuser' + (PAT.spr.reg ? ', en appliquant le règlement propre au site.' : ' ; en l\\'absence de règlement approuvé pour ce site, l\\'architecte apprécie chaque projet au cas par cas.') : 'l\\'architecte des Bâtiments de France donne son avis sur les travaux et peut imposer des prescriptions (matériaux, couleurs, volumes).');
    if (key === 'ok') key = 'cond';
  } else if (PAT.probables && PAT.probables.length) {
    abf = 'probable';
    const M0 = PAT.probables[0];
    why += ' Le monument historique « ' + M0.nom + ' » se trouve à ' + (M0.d === 0 ? 'moins de 10 m' : 'environ ' + fmtN(Math.max(10, Math.round(M0.d / 10) * 10)) + ' m') + ' du terrain : si le terrain est visible depuis ce monument ou en même temps que lui, l\\'accord de l\\'architecte des Bâtiments de France sera obligatoire (abords de monument historique, rayon de 500 m).';
    if (key === 'ok') key = 'cond';
  }""")
rep("vigil && key === 'cond' ? 'Constructible au PLU, avec une contrainte forte à vérifier' : TITLE[key], why, vigil },",
    "vigil && key === 'cond' ? 'Constructible au PLU, avec une contrainte forte à vérifier' : abf === 'sur' && key === 'cond' ? 'Constructible sous conditions : accord de l\\'architecte des Bâtiments de France' : abf === 'probable' && key === 'cond' ? 'Constructible sous conditions : avis de l\\'architecte des Bâtiments de France probable' : TITLE[key], why, vigil, abf },")

# 3. Points d'attention et démarches
rep("""  { const n1 = c.sups.filter(s => s.code === 'ac1').length, n2 = c.sups.filter(s => s.code === 'ac2').length;
    if (n1) pts.push({ key: 'cond', text: (n1 > 1 ? 'Abords de ' + n1 + ' monuments historiques' : 'Abords d\\'un monument historique') + ' : l\\'avis de l\\'architecte des Bâtiments de France est requis pour les travaux.' });
    if (n2) pts.push({ key: 'cond', text: (n2 > 1 ? n2 + ' sites classés ou inscrits' : 'Site classé ou inscrit') + ' : l\\'avis de l\\'architecte des Bâtiments de France est requis pour les travaux.' }); }""",
"""  if (PAT.spr) pts.push({ key: 'cond', text: 'Site patrimonial remarquable (' + PAT.spr.nom + ') : accord obligatoire de l\\'architecte des Bâtiments de France pour tout projet visible de l\\'extérieur' + (PAT.spr.reg ? ', selon le règlement du site.' : ', apprécié au cas par cas.') });
  if (!PAT.spr && PAT.abords.length) pts.push({ key: 'cond', text: 'Abords de monument historique (' + PAT.abords.slice(0, 2).join(', ') + ') : accord de l\\'architecte des Bâtiments de France pour les travaux.' });
  if (PAT.sites.length) pts.push({ key: 'cond', text: 'Site classé ou inscrit (' + PAT.sites[0] + ') : avis de l\\'architecte des Bâtiments de France, autorisation spéciale en site classé.' });
  if (!PAT.spr && !PAT.abords.length && PAT.probables && PAT.probables.length) pts.push({ key: 'cond', text: 'Monument historique à ' + fmtN(Math.max(10, Math.round(PAT.probables[0].d / 10) * 10)) + ' m (' + PAT.probables[0].nom + ') : accord de l\\'architecte des Bâtiments de France si le terrain est en covisibilité.' });
  if (!PAT.spr && !PAT.abords.length && !PAT.sites.length && !(PAT.probables || []).length) { const n1 = c.sups.filter(s => s.code === 'ac1').length, n2 = c.sups.filter(s => s.code === 'ac2').length;
    if (n1) pts.push({ key: 'cond', text: 'Abords d\\'un monument historique : accord de l\\'architecte des Bâtiments de France pour les travaux.' });
    if (n2) pts.push({ key: 'cond', text: 'Site classé ou inscrit : avis de l\\'architecte des Bâtiments de France pour les travaux.' }); }""")
rep("  if (c.sups.some(s => s.code === 'ac1' || s.code === 'ac2')) steps.push(['Architecte des Bâtiments de France',",
    "  if (PAT.spr || PAT.abords.length || PAT.sites.length || (PAT.probables || []).length || c.sups.some(s => s.code === 'ac1' || s.code === 'ac2')) steps.push(['Architecte des Bâtiments de France',")

# 4. Rapport complet : section dédiée après les servitudes
rep("""  } else text('Aucune servitude d\\'utilité publique numérisée n\\'est recensée sur la parcelle au Géoportail de l\\'Urbanisme. Les servitudes non encore numérisées figurent en annexe du PLU.', { size: 9.5 });
""", """  } else text('Aucune servitude d\\'utilité publique numérisée n\\'est recensée sur la parcelle au Géoportail de l\\'Urbanisme. Les servitudes non encore numérisées figurent en annexe du PLU.', { size: 9.5 });
  {
    const PT = d.patrimoine || {}, MH = PT.mh || [];
    const any = PT.spr || (PT.sites || []).length || (PT.abords || []).length || (PT.probables || []).length;
    h3('Patrimoine : l\\'architecte des Bâtiments de France');
    if (!any) {
      text(MH.length ? 'Aucune protection patrimoniale ne s\\'applique au terrain d\\'après les servitudes publiées : les monuments historiques les plus proches sont couverts par des périmètres délimités qui n\\'incluent pas le terrain.' : 'Aucun site patrimonial remarquable, site classé ou inscrit, ni monument historique à moins de 500 m n\\'est recensé : l\\'avis de l\\'architecte des Bâtiments de France n\\'est pas requis au titre du patrimoine.', { size: 9.5 });
    } else {
      note('En clair : ' + (PT.spr ? 'le terrain est dans un site patrimonial remarquable. Toute construction, extension, clôture, piscine ou modification de façade, de toiture ou de menuiseries doit recevoir l\\'accord de l\\'architecte des Bâtiments de France. Il peut imposer des matériaux, des couleurs, des volumes, ou refuser le projet.' : (PT.abords || []).length ? 'le terrain est aux abords d\\'un monument historique. Les travaux visibles de l\\'extérieur doivent recevoir l\\'accord de l\\'architecte des Bâtiments de France, qui peut imposer des prescriptions.' : (PT.sites || []).length ? 'le terrain est dans un site classé ou inscrit. L\\'architecte des Bâtiments de France donne son avis sur les travaux ; en site classé, une autorisation spéciale est nécessaire.' : 'un monument historique se trouve à moins de 500 m. Si le terrain est visible depuis ce monument ou en même temps que lui, l\\'accord de l\\'architecte des Bâtiments de France sera obligatoire. La mairie vous le confirmera.'), 'cond');
      const rows = [];
      if (PT.spr) rows.push(['Site patrimonial remarquable', PT.spr.nom, 'Accord obligatoire de l\\'architecte (avis conforme) pour tout projet modifiant l\\'aspect extérieur' + (PT.spr.reg ? ', selon le règlement du site' : ' ; pas de règlement approuvé publié : appréciation au cas par cas')]);
      (PT.sites || []).forEach(n => rows.push(['Site classé ou inscrit', n, 'Site inscrit : avis de l\\'architecte. Site classé : autorisation spéciale du préfet ou du ministre']));
      (PT.abords || []).forEach(n => rows.push(['Abords de monument historique', n, 'Accord de l\\'architecte pour les travaux visibles (périmètre publié)']));
      (PT.probables || []).forEach(x => rows.push(['Monument historique ' + (x.protection || 'protégé'), x.nom + ' · à ' + (x.d === 0 ? 'moins de 10 m' : 'environ ' + fmt(Math.max(10, Math.round(x.d / 10) * 10)) + ' m'), 'Accord de l\\'architecte si le terrain est visible depuis le monument ou en même temps que lui']));
      table([{ label: 'PROTECTION', w: 0.26, bold: true }, { label: 'NOM', w: 0.32 }, { label: 'CE QUE CELA IMPLIQUE', w: 0.42 }], rows, { size: 8.5 });
      if (PT.spr && PT.spr.analysis && PT.spr.analysis.zone_trouvee !== false) {
        const SA = PT.spr.analysis, rg = (SA.regles || []).filter(r => r && r.critere && r.regle && !/^Non précisé/i.test(r.regle));
        h4('Ce que dit le règlement du site patrimonial remarquable');
        if (SA.caractere) text(SA.caractere, { size: 9.5 });
        if (rg.length) table([{ label: 'SUJET', w: 0.26, bold: true }, { label: 'RÈGLE', w: 0.58 }, { label: 'ARTICLE', w: 0.16 }], rg.map(r => [r.critere, r.regle, r.article || '']), { size: 8.5 });
        (SA.points_vigilance || []).slice(0, 5).forEach(t => bullet(t, { size: 9, color: C.cond }));
      }
      const L = [];
      if (PT.spr && PT.spr.reg) L.push(['Règlement du site patrimonial remarquable', PT.spr.reg]);
      if (PT.spr && PT.spr.acte) L.push(['Acte de création du site patrimonial remarquable', PT.spr.acte]);
      if (L.length) kvn(L, { lw: 0.42 });
      text('Conseils : consulter l\\'architecte des Bâtiments de France (unité départementale de l\\'architecture et du patrimoine, joignable par la mairie) avant de dessiner le projet ; prévoir un délai d\\'instruction majoré d\\'un mois ; soigner l\\'insertion (matériaux, teintes, toitures, clôtures) dès l\\'esquisse.', { size: 9 });
    }
  }
""")

# 5. Rapport synthétique : ligne Patrimoine
rep("      ['Fibre', FB && !FB.none && FB.nearest ?", """      ['Patrimoine (architecte des Bâtiments de France)', (() => { const PT = d.patrimoine || {}; if (PT.spr) return 'Site patrimonial remarquable : accord de l\\'architecte obligatoire' + (PT.spr.reg ? ', selon le règlement du site' : ', au cas par cas'); if ((PT.abords || []).length) return 'Abords de monument historique : accord de l\\'architecte'; if ((PT.sites || []).length) return 'Site classé ou inscrit : avis de l\\'architecte'; if ((PT.probables || []).length) return 'Monument historique à environ ' + fmt(Math.max(10, Math.round(PT.probables[0].d / 10) * 10)) + ' m : accord de l\\'architecte si covisibilité'; return d.patrimoine ? 'Aucune protection patrimoniale' : null; })()],
      ['Fibre', FB && !FB.none && FB.nearest ?""")
open(p, 'w', encoding='utf-8').write(s); print('patch abf appliqué')
