# Zonage des communes dont le PLU n'est pas publié au Géoportail : lu sur les cartes de zonage officielles de la commune (table zonage_local)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable : ' + old[:70])
    s = s.replace(old, new)
rep("""  // ----- Zonage -----
  const zf = zj.features || [];""", """  // ----- Zonage -----
  let zLocalF = null, zLocalSrc = '';
  if (!(zj.features || []).length && !(ccj.features || []).length) {
    try {
      const { data: zl } = await admin.from('zonage_local').select('libelle,libelong,typezone,urlfic,datappro,source,geom,bbox').eq('insee', INS);
      const pb = turf.bbox(pf);
      const hit = (zl || []).filter(r => !(r.bbox[0] > pb[2] || r.bbox[2] < pb[0] || r.bbox[1] > pb[3] || r.bbox[3] < pb[1]))
        .filter(r => { try { return turf.booleanIntersects(pf, turf.feature(r.geom)); } catch (e) { return false; } });
      if (hit.length) {
        zLocalF = hit.map(r => ({ type: 'Feature', geometry: r.geom, properties: { libelle: r.libelle, libelong: r.libelong, typezone: r.typezone, urlfic: r.urlfic, datappro: r.datappro } }));
        zLocalSrc = hit[0].source || '';
        const zb = turf.bbox(turf.buffer(pf, 400, { units: 'meters' }));
        const ctx = (zl || []).filter(r => !hit.includes(r) && !(r.bbox[0] > zb[2] || r.bbox[2] < zb[0] || r.bbox[1] > zb[3] || r.bbox[3] < zb[1]));
        zLocalF.ctx = ctx.map(r => ({ type: 'Feature', geometry: r.geom, properties: { libelle: r.libelle, libelong: r.libelong, typezone: r.typezone } }));
      }
    } catch (e) { console.warn('zonage_local', e); }
  }
  const zf = zLocalF || zj.features || [];""")
rep("const zsrc = zf.length ? zf : ccF;", "const zsrc = zf.length ? (zLocalF && zLocalF.ctx ? [...zf, ...zLocalF.ctx] : zf) : ccF;")
rep("""status: docp.gpu_status ? (""", """local: !!zLocalF, source: zLocalSrc, status: zLocalF ? 'Non publié au Géoportail de l\\'Urbanisme. Zonage relevé sur le plan de zonage officiel publié par la commune' : docp.gpu_status ? (""")
rep("""caption: 'Zonage : Géoportail de l\\'Urbanisme · fond : © IGN' });""", """caption: (d.doc.local ? 'Zonage : plan de zonage officiel de la commune, recalé sur le cadastre' : 'Zonage : Géoportail de l\\'Urbanisme') + ' · fond : © IGN' });
  if (d.doc.local) note('Le plan local d\\'urbanisme de ' + R.commune + ' n\\'est pas publié sur le Géoportail de l\\'Urbanisme. La zone indiquée a été relevée directement sur le plan de zonage officiel mis en ligne par la commune, recalé sur le cadastre. Plan de zonage : ' + d.doc.source + '. Règlement de la zone : ' + (d.doc.url || 'en mairie') + '.', 'info');""")
rep("""    ['Règlement officiel', d.doc.url || 'Non publié en ligne : à consulter en mairie']
  ]);""", """    ['Règlement officiel', d.doc.url || 'Non publié en ligne : à consulter en mairie'],
    ...(d.doc.local && d.doc.source ? [['Plan de zonage officiel', d.doc.source]] : [])
  ]);""")
rep("""'Lire le règlement écrit de la zone ' + (Z0 ? Z0.code : '') + ' et, le cas échéant, les orientations d\\'aménagement, disponibles sur le Géoportail de l\\'Urbanisme.'""",
    """'Lire le règlement écrit de la zone ' + (Z0 ? Z0.code : '') + ' et, le cas échéant, les orientations d\\'aménagement, ' + (c.doc.local ? 'publiés sur le site de la commune.' : 'disponibles sur le Géoportail de l\\'Urbanisme.')""")
open(p, 'w', encoding='utf-8').write(s); print('patch plu_local appliqué')
