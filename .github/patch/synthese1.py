"""Synthèse en page 2, juste après la couverture (le sommaire passe après), avec « Ce que vous pouvez construire » :
surface au sol, emprise, hauteur, reculs des limites et des voies, surface minimale, extraits du règlement."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
# 1. Le sommaire est créé après la synthèse
rep("  // Page 2 : sommaire (rempli à la fin, une fois les numéros de page connus)\n  CUR = 'Sommaire'; newPage(); const tocPage = page;\n", "")
rep("  // =====================================================================\n  // 1. IDENTIFICATION\n",
    "  // Sommaire, après la synthèse (rempli à la fin, une fois les numéros de page connus)\n  CUR = 'Sommaire'; newPage(); const tocPage = page;\n\n  // =====================================================================\n  // 1. IDENTIFICATION\n")
rep("const all = [{ num: '', title: 'Synthèse', page: 3,", "const all = [{ num: '', title: 'Synthèse', page: 2,")
# 2. Ce que vous pouvez construire, sur la page de synthèse
BLOCK = r'''  // Ce que vous pouvez construire : les chiffres et les règles clés, dès la synthèse
  try {
    const K = d.calc || {}, RG = d.reglement, zl = (d.zones || []).filter(z => z.share >= 0.03), MULTI = zl.length > 1;
    const nb = v => String(v).replace('.', ','), cut = (t, n) => { t = String(t || '').trim(); if (t.length <= n) return t; const k = t.lastIndexOf('. ', n); return (k > n * 0.5 ? t.slice(0, k + 1) : t.slice(0, n).replace(/\s+\S*$/, '') + '…'); };
    const KEY = /emprise|hauteur|limites s[ée]paratives|par rapport aux voies|voies et emprises/i;
    const rows = [];
    const noBuild = K.neuf === false || d.verdict.key === 'non';
    if (RG && RG.analysis && !noBuild) {
      if (K.footprint) rows.push(['Surface au sol constructible', 'environ ' + fmt(K.footprint) + ' m²' + (K.empPct != null ? ' (emprise maximale ' + nb(K.empPct) + ' % du terrain)' : ' (pas de plafond d\'emprise relevé ; limitée par les reculs)')]);
      if (K.plancher) rows.push(['Surface de plancher estimée', 'environ ' + fmt(K.plancher) + ' m²' + (K.niv ? ' sur ' + K.niv + ' niveau' + (K.niv > 1 ? 'x' : '') : '')]);
      { let ht = null; try { ht = typeof hauteurTexte === 'function' ? hauteurTexte(d) : null; } catch (e) {} if (ht && String(ht).length <= 90 && !/…$/.test(ht)) rows.push(['Hauteur maximale', ht]); else if (K.H) rows.push(['Hauteur maximale', 'environ ' + nb(K.H) + ' m de façade (détail au chapitre « Ce que vous pouvez construire »)']); }
      if (K.rl) rows.push(['Recul des limites séparatives', nb(K.rl) + ' m minimum']);
      if (K.rv) rows.push(['Recul par rapport aux voies', nb(K.rv) + ' m minimum']);
      rows.push(['Surface minimale de terrain', K.minTerrain ? fmt(K.minTerrain) + ' m² ' + (K.minOk ? '(respectée)' : '(non respectée)') : 'Aucune exigée par le règlement relevé']);
      if (K.logement === false) rows.push(['Logement neuf', 'Non admis par le règlement de la zone, sauf exceptions']);
    }
    if (rows.length || (RG && RG.analysis)) {
      h3('Ce que vous pouvez construire', 120);
      if (rows.length) kv(rows, { lw: 0.36 });
      const rg = RG && RG.analysis ? (RG.analysis.regles || []).filter(r => r && r.critere && r.regle && KEY.test(r.critere) && !/^Non (précisé|réglementé)/i.test(r.regle)).slice(0, 4) : [];
      if (rg.length) table([{ label: 'RÈGLE' + (RG.zone ? ' (ZONE ' + RG.zone + ')' : ''), w: 0.3, bold: true }, { label: 'CE QUE DIT LE RÈGLEMENT', w: 0.7 }], rg.map(r => [r.critere, cut(r.regle, 160)]), { size: 8.3 });
      text('Calcul indicatif établi à partir du règlement de la zone et du plan cadastral ; le détail, les extraits officiels et le plan d\'implantation figurent au chapitre « Ce que vous pouvez construire ».', { size: 8.3, color: C.muet });
    } else if (d.doc && (d.doc.type === 'CC' || d.doc.rnu)) {
      h3('Ce que vous pouvez construire', 80);
      text('Règles nationales d\'urbanisme (RNU) : construction en limite séparative, ou à une distance au moins égale à la moitié de sa hauteur sans être inférieure à 3 m (article R. 111-17 du code de l\'urbanisme) ; la mairie appréciant chaque projet au regard de son insertion et des réseaux. Détail au chapitre « Ce que vous pouvez construire ».', { size: 9.3 });
    }
  } catch (e) { console.warn('synthèse construire', String(e && e.message || e).slice(0, 120)); }
'''
rep("  // Points d'attention complémentaires\n  try {", BLOCK + "  // Points d'attention complémentaires\n  try {")
open(p, 'w', encoding='utf-8').write(s); print('ok synthese1')
