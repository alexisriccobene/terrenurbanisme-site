"""Synthèse « Ce que vous pouvez construire » : chiffres seulement quand ils sont sûrs (une seule zone, emprise ou reculs chiffrés) ;
terrain sur plusieurs zones : règles zone par zone, sans total trompeur."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
i = s.index("  // Ce que vous pouvez construire : les chiffres et les règles clés, dès la synthèse")
j = s.index("  // Points d'attention complémentaires\n  try {", i)
NEW = r'''  // Ce que vous pouvez construire : les chiffres et les règles clés, dès la synthèse (uniquement des valeurs sûres)
  try {
    const K = d.calc || {}, RG = d.reglement, zl = (d.zones || []).filter(z => z.share >= 0.03), MULTI = zl.length > 1, SURF = R.areaCalc || R.contenance || 0;
    const nb = v => String(v).replace('.', ','), cut = (t, n) => { t = String(t || '').trim(); if (t.length <= n) return t; const k = t.lastIndexOf('. ', n); return (k > n * 0.5 ? t.slice(0, k + 1) : t.slice(0, n).replace(/\s+\S*$/, '') + '…'); };
    const KEY = /emprise|hauteur|limites s[ée]paratives|par rapport aux voies|voies et emprises/i;
    const regles = an => (an && an.regles || []).filter(r => r && r.critere && r.regle && KEY.test(r.critere) && !/^Non (précisé|réglementé)/i.test(r.regle)).slice(0, 4);
    const tableZ = (an, code) => { const rg = regles(an); if (rg.length) table([{ label: 'RÈGLE' + (code ? ' (ZONE ' + code + ')' : ''), w: 0.3, bold: true }, { label: 'CE QUE DIT LE RÈGLEMENT', w: 0.7 }], rg.map(r => [r.critere, cut(r.regle, 160)]), { size: 8.3 }); };
    const noBuild = K.neuf === false || d.verdict.key === 'non';
    if (RG && RG.analysis && !MULTI) {
      const rows = [];
      if (!noBuild) {
        const chiffre = K.empPct != null || K.rl > 0 || K.rv > 0;
        if (K.footprint && chiffre && !(K.empPct == null && SURF && K.footprint >= SURF * 0.9)) rows.push(['Surface au sol constructible', 'environ ' + fmt(K.footprint) + ' m²' + (K.empPct != null ? ' (emprise maximale ' + nb(K.empPct) + ' % du terrain)' : ' (après les reculs)')]);
        if (K.empPct != null && !rows.length) rows.push(['Emprise au sol maximale', nb(K.empPct) + ' % du terrain']);
        let ht = null; try { ht = typeof hauteurTexte === 'function' ? hauteurTexte(d) : null; } catch (e) {}
        if (ht && String(ht).length <= 90 && !/…$/.test(ht) && !/non précis/i.test(ht)) rows.push(['Hauteur maximale', ht]);
        if (K.rl) rows.push(['Recul des limites séparatives', nb(K.rl) + ' m minimum']);
        if (K.rv) rows.push(['Recul par rapport aux voies', nb(K.rv) + ' m minimum']);
        rows.push(['Surface minimale de terrain', K.minTerrain ? fmt(K.minTerrain) + ' m² ' + (K.minOk ? '(respectée)' : '(non respectée)') : 'Aucune exigée par le règlement relevé']);
      }
      if (K.logement === false) rows.push(['Logement neuf', 'Non admis par le règlement de la zone, sauf exceptions']);
      h3('Ce que vous pouvez construire', 120);
      if (rows.length) kv(rows, { lw: 0.36 });
      tableZ(RG.analysis, RG.zone);
      text('Valeurs relevées dans le règlement de la zone ; le détail, les extraits officiels et le plan d\'implantation figurent au chapitre « Ce que vous pouvez construire ».', { size: 8.3, color: C.muet });
    } else if (RG && RG.analysis && MULTI) {
      h3('Ce que vous pouvez construire, zone par zone', 120);
      const AN = [{ zone: RG.zone, analysis: RG.analysis }].concat((RG.others || []).filter(o => o && o.analysis));
      zl.slice().sort((a, b) => (a.v === 'non') - (b.v === 'non')).forEach(z => {
        const a = AN.find(x => x.zone === z.code);
        h4('Zone ' + z.code + ' · ' + String(z.verdictWord || '').toLowerCase() + (SURF ? ' · environ ' + fmt(Math.round(z.share * SURF / 10) * 10) + ' m²' : ''), 70);
        if (z.v === 'non') text('Pas de construction nouvelle de logement, sauf exceptions prévues par la zone.', { size: 9 });
        else if (a) tableZ(a.analysis, z.code);
        else text('Règles de cette zone : voir le chapitre « Ce que vous pouvez construire ».', { size: 9 });
      });
      text('Le terrain est à cheval sur plusieurs zones : chaque partie suit les règles de sa zone. Le détail figure au chapitre « Ce que vous pouvez construire ».', { size: 8.3, color: C.muet });
    } else if (d.doc && (d.doc.type === 'CC' || d.doc.rnu)) {
      h3('Ce que vous pouvez construire', 80);
      text('Règles nationales d\'urbanisme (RNU) : construction en limite séparative, ou à une distance au moins égale à la moitié de sa hauteur sans être inférieure à 3 m (article R. 111-17 du code de l\'urbanisme) ; la mairie apprécie chaque projet au regard de son insertion et des réseaux. Détail au chapitre « Ce que vous pouvez construire ».', { size: 9.3 });
    }
  } catch (e) { console.warn('synthèse construire', String(e && e.message || e).slice(0, 120)); }
'''
s = s[:i] + NEW + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok synthese2')
