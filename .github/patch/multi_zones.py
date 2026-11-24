# Parcelle à cheval sur plusieurs zones : verdict « constructible sous conditions » quand une partie est constructible,
# surfaces par zone en m², et chapitre « Ce que vous pouvez construire » présenté zone par zone.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:80]))
    s = s.replace(old, new)

# 1. Lecture du règlement : toutes les zones couvrant au moins 3 % du terrain (et non plus 10 %)
rep("if (picks.length && z.share < 0.1) break;", "if (picks.length && z.share < 0.03) break;")

# 2. Verdict : zone principale non constructible mais une autre partie constructible
rep("""    why += key === 'ok' ? ' Les constructions y sont admises dans le respect du règlement de la zone.' : key === 'non' ? ' Les constructions nouvelles n\\'y sont pas admises, sauf exceptions encadrées.' : ' La construction y est possible sous conditions.';
  }
""", """    why += key === 'ok' ? ' Les constructions y sont admises dans le respect du règlement de la zone.' : key === 'non' ? ' Les constructions nouvelles n\\'y sont pas admises, sauf exceptions encadrées.' : ' La construction y est possible sous conditions.';
    const zc = zones.filter(z => z !== Z0 && (z.v === 'ok' || z.v === 'cond') && z.share >= 0.03 && z.share * (R.areaCalc || 0) >= 200);
    if (Z0.v === 'non' && zc.length) {
      key = 'cond'; partiel = zc;
      const m2z = z => fmtN(Math.round(z.share * (R.areaCalc || 0) / 10) * 10);
      why = 'Le terrain est à cheval sur ' + (zones.length > 1 ? zones.length + ' zones' : 'deux zones') + ' du ' + (c.doc.type === 'PLUI' ? 'PLU intercommunal' : 'plan local d\\'urbanisme') + ' de ' + R.commune + '. '
        + zones.map(z => 'Environ ' + m2z(z) + ' m² (' + Math.round(z.share * 100) + ' % du terrain) sont en zone ' + z.code + ' (' + z.typeLabel.toLowerCase() + ') : ' + (z.v === 'ok' ? 'constructible' : z.v === 'cond' ? 'constructible sous conditions' : 'non constructible, sauf exceptions encadrées') + '.').join(' ')
        + ' Une construction nouvelle ne peut donc s\\'implanter que sur la partie en zone ' + zc.map(z => z.code).join(' ou ') + ', dans le respect de son règlement.';
    }
  }
""")
rep("  let vigil = '';\n  if (majorHits.length) {", "  let vigil = '';\n  if (majorHits.length) {\n    const Z0 = partiel ? partiel[0] : zones[0];")
rep("  let key, why;\n  if (c.doc.rnu)", "  let key, why, partiel = null;\n  if (c.doc.rnu)")
rep("verdict: { key, word: WORD[key], title: vigil && key === 'ok'",
    "verdict: { key, word: partiel ? 'Constructible sous conditions' : WORD[key], partiel: partiel ? partiel.map(z => z.code) : null, title: partiel ? 'Constructible sous conditions : seule la partie en zone ' + partiel.map(z => z.code).join(' ou ') + ' peut accueillir une construction' : vigil && key === 'ok'")

# 3. Indicateur et points d'attention avec les surfaces
rep("  ind.push({ label: 'Zone principale', value: Z0 ? Z0.code + ' · ' + Math.round(Z0.share * 100) + ' %' : (c.doc.rnu ? 'RNU' : 'Non publiée'), key: Z0 ? Z0.v : 'cond' });",
    "  const zs3 = zones.filter(z => z.share >= 0.03);\n  ind.push(zs3.length > 1 ? { label: 'Zones du PLU', value: zs3.map(z => z.code + ' ' + Math.round(z.share * 100) + ' %').join(' · '), key } : { label: 'Zone principale', value: Z0 ? Z0.code + ' · ' + Math.round(Z0.share * 100) + ' %' : (c.doc.rnu ? 'RNU' : 'Non publiée'), key: Z0 ? Z0.v : 'cond' });")
rep("  zones.forEach(z => pts.push({ key: z.v, text: `Zone ${z.code} (${Math.round(z.share * 100)} % de la parcelle) : ${z.verdictWord.toLowerCase()}.` }));",
    """  zones.forEach(z => pts.push({ key: z.v, text: zones.length > 1 && R.areaCalc ? `Zone ${z.code} (${z.typeLabel.toLowerCase()}) : environ ${fmtN(Math.round(z.share * R.areaCalc / 10) * 10)} m², soit ${Math.round(z.share * 100)} % du terrain, ${z.verdictWord.toLowerCase()}.` : `Zone ${z.code} (${Math.round(z.share * 100)} % de la parcelle) : ${z.verdictWord.toLowerCase()}.` }));
  if (R.contenance && R.areaCalc && Math.abs(R.contenance - R.areaCalc) / R.contenance > 0.25) pts.push({ key: 'info', text: 'La surface inscrite au cadastre (' + fmtN(R.contenance) + ' m²) ne correspond pas à celle du plan cadastral (' + fmtN(R.areaCalc) + ' m²). Les surfaces par zone sont calculées sur le plan : seul un géomètre-expert peut fixer la surface exacte.' });""")

# 4. Chapitre « Ce que vous pouvez construire » zone par zone
rep("""    chapter(++CHN, 'Ce que vous pouvez construire', 'Lecture du règlement écrit de la zone ' + (RG.zone || '') + (RG.pages ? ', pages ' + RG.pages[0] + ' à ' + RG.pages[1] + ' du règlement officiel.' : '.'));
    const K = d.calc, n0 = v => v == null ? null : fmt(v);
    if (K) {
      h3('Potentiel constructible estimé');""",
"""    const MZ = (d.zones || []).filter(z => z.share >= 0.03), MULTI = MZ.length > 1, ZP = t => MULTI ? 'Zone ' + (RG.zone || '') + ' · ' + t : t;
    const m2Z = z => fmt(Math.round(z.share * (R.areaCalc || 0) / 10) * 10);
    chapter(++CHN, 'Ce que vous pouvez construire', MULTI ? 'Lecture du règlement écrit des zones ' + MZ.map(z => z.code).join(' et ') + ', sur lesquelles le terrain est à cheval.' : 'Lecture du règlement écrit de la zone ' + (RG.zone || '') + (RG.pages ? ', pages ' + RG.pages[0] + ' à ' + RG.pages[1] + ' du règlement officiel.' : '.'));
    if (MULTI) {
      const okz = MZ.filter(z => z.v !== 'non'), noz = MZ.filter(z => z.v === 'non');
      h3('Un terrain à cheval sur ' + MZ.length + ' zones');
      table([{ label: 'ZONE', w: 0.14, bold: true }, { label: 'NATURE', w: 0.3 }, { label: 'SURFACE', w: 0.2 }, { label: 'PART', w: 0.12 }, { label: 'CONSTRUCTIBILITÉ', w: 0.24 }],
        MZ.map(z => [z.code, z.typeLabel, R.areaCalc ? 'environ ' + m2Z(z) + ' m²' : '–', Math.round(z.share * 100) + ' %', z.verdictWord]), { size: 9, color: (r, i, ri) => i === 4 ? VC[MZ[ri].v][0] : null });
      note('Les règles ne sont pas les mêmes d\\'une zone à l\\'autre : chaque titre ci-dessous indique la zone à laquelle la règle s\\'applique.' + (okz.length && noz.length ? ' Une maison ou un autre bâtiment neuf ne peut être construit que sur la partie en zone ' + okz.map(z => z.code).join(' ou ') + ' (environ ' + okz.map(z => m2Z(z) + ' m²').join(' et ') + ') ; sur la partie en zone ' + noz.map(z => z.code).join(' ou ') + ', seules les constructions listées pour cette zone sont admises.' : ''), okz.length ? 'cond' : 'non');
    }
    const K = d.calc, n0 = v => v == null ? null : fmt(v);
    if (K) {
      h3(ZP('Potentiel constructible estimé'));""")
a = s.index("    if (A.caractere) { h3('Caractère de la zone'); text(A.caractere, { size: 10 }); }")
b = s.index("    note('Cette lecture est établie automatiquement, par intelligence artificielle, à partir du règlement officiel en vigueur.", a)
blk = s[a:b]
def brep(old, new):
    global blk
    if blk.count(old) != 1: sys.exit('ancre bloc introuvable : ' + old[:70])
    blk = blk.replace(old, new)
for t in ['Caractère de la zone', 'Règles de construction', 'Usages autorisés', 'Usages interdits ou soumis à conditions', 'Points de vigilance pour votre projet', 'Extraits du règlement', 'Démarches probables']:
    brep("h3('" + t + "')", "h3(ZP('" + t + "'))")
i = blk.index("    for (const O of (RG.others || [])) {")
blk = blk[:i] + """    for (const O of (RG.others || [])) {
      const OA = O.analysis || {}, OZ = (d.zones || []).find(z => z.code === O.zone), OP = t => 'Zone ' + O.zone + ' · ' + t;
      ensure(140); h3('Zone ' + O.zone + (OZ ? ' (' + OZ.typeLabel.toLowerCase() + ')' : '') + ' : ' + (O.share ? 'environ ' + fmt(Math.round(O.share * (R.areaCalc || 0) / 10) * 10) + ' m², ' + Math.round(O.share * 100) + ' % du terrain' : 'partie du terrain'));
      if (OZ) note(OZ.v === 'non' ? 'Sur cette partie du terrain, les constructions nouvelles ne sont pas admises, sauf celles listées ci-dessous.' : 'Sur cette partie du terrain, une construction est possible dans le respect des règles ci-dessous' + (OZ.v === 'cond' ? ', sous conditions.' : '.'), OZ.v);
      if (OA.caractere) { h4(OP('Caractère de la zone')); text(OA.caractere, { size: 9.5 }); }
      const rg = (OA.regles || []).filter(r => r && r.critere && r.regle && !/^Non précisé/i.test(r.regle));
      if (rg.length) { h4(OP('Règles de construction')); table([{ label: 'CRITÈRE', w: 0.28, bold: true }, { label: 'RÈGLE APPLICABLE', w: 0.56 }, { label: 'ARTICLE', w: 0.16 }], rg.map(r => [r.critere, r.regle, r.article || '']), { size: 8.5 }); }
      if (OA.autorise && OA.autorise.length) { h4(OP('Usages autorisés')); OA.autorise.forEach(t => bullet(t, { size: 9.5, color: C.ok })); }
      if (OA.interdit_ou_conditionne && OA.interdit_ou_conditionne.length) { h4(OP('Usages interdits ou soumis à conditions')); OA.interdit_ou_conditionne.forEach(t => bullet(t, { size: 9.5, color: C.non })); }
      if (OA.points_vigilance && OA.points_vigilance.length) { h4(OP('Points de vigilance')); OA.points_vigilance.forEach(t => bullet(t, { size: 9.5, color: C.cond })); }
    }
"""
s = s[:a] + blk + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('patch multi_zones appliqué')
