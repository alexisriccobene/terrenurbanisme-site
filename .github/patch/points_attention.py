# Synthèse : points d'attention complémentaires (logement non admis, argiles et étude géotechnique loi ELAN, risques technologiques à la parcelle) ; accent « très »
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:80], s.count(a))
    s = s.replace(a, b)
rep("""  // Points d'attention
  if (d.points && d.points.length) {
    h3('Points d\\'attention');""", """  // Points d'attention complémentaires
  try {
    const K0 = d.calc || {}, RK0 = d.risques || {}, ex = [], nz0 = d.zones && d.zones[0] ? d.zones[0].code : '';
    if (K0.neuf === false && d.verdict.key !== 'non') ex.push({ key: 'cond', text: 'Le règlement de la zone ' + nz0 + ' n\\'admet pas de construction nouvelle, sauf exceptions prévues par la zone : voir le chapitre « Ce que vous pouvez construire ».' });
    else if (K0.logement === false) ex.push({ key: 'cond', text: 'Logement : le règlement de la zone ' + nz0 + ' n\\'admet pas de logement neuf, sauf exceptions prévues par la zone (logement de gardiennage, par exemple) : voir le chapitre « Ce que vous pouvez construire ».' });
    const rga0 = (RK0.naturels || []).find(r => r.key === 'retraitGonflementArgile');
    const rgaT = String((rga0 && (rga0.adresse || (!RK0.addressLevel ? rga0.commune : ''))) || '');
    if (/mod[ée]r|moyen|fort|important/i.test(rgaT)) ex.push({ key: 'cond', text: 'Retrait-gonflement des argiles (exposition ' + (/fort|important/i.test(rgaT) ? 'forte' : 'moyenne') + ') : en cas de vente d\\'un terrain non bâti constructible, le vendeur doit fournir une étude géotechnique préalable (loi ELAN, article L. 132-5 du Code de la construction et de l\\'habitation) ; une étude géotechnique de conception est exigée avant de construire.' });
    (RK0.techno || []).filter(r => r.present && r.adresse).forEach(r => ex.push({ key: 'cond', text: r.label + ' : concerné à l\\'adresse de la parcelle (voir le chapitre « Risques naturels et technologiques »).' }));
    if (ex.length) { const pp = d.points || []; const cat = pp.findIndex(x => /catastrophe naturelle/.test(x.text)); const ins = cat >= 0 ? cat : pp.length; d.points = pp.slice(0, ins).concat(ex, pp.slice(ins)); }
  } catch (e) { console.warn('points complémentaires', String(e && e.message || e).slice(0, 120)); }
  // Points d'attention
  if (d.points && d.points.length) {
    h3('Points d\\'attention');""")
rep("if (risques.sismique) risques.sismique = 'Zone ' + risques.sismique.replace(/^(\\d)\\s*–\\s*/, '$1 – ');",
    "if (risques.sismique) risques.sismique = ('Zone ' + risques.sismique.replace(/^(\\d)\\s*–\\s*/, '$1 – ')).replace(/\\btres\\b/g, 'très');")
open(p, 'w', encoding='utf-8').write(s); print('patch points attention appliqué')
