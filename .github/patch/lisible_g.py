"""Informations du PLU sans code : explication selon le libellé ; identifiants résiduels retirés des servitudes."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)
rep("function supExpl(code, label) {", r"""function infExpl(code, label) {
  if (INF_EXPL[code] && code !== '99') return INF_EXPL[code];
  const t = String(label || '');
  const niv = /tr[eè]s fort|fort|rouge/i.test(t) ? ' Niveau de risque élevé : construction en principe interdite.' : /mod[ée]r|moyen|bleu/i.test(t) ? ' Niveau de risque modéré : construction en principe possible avec des prescriptions.' : /faible/i.test(t) ? ' Niveau de risque faible : quelques prescriptions.' : '';
  if (/PPRIF|incendie|feu/i.test(t)) return 'Zone du plan de prévention des risques d\'incendie de forêt.' + niv + ' Le règlement du plan s\'impose au permis.';
  if (/PPRI\b|PPRi|inond|ruissel|talweg/i.test(t)) return 'Zone du plan de prévention des risques d\'inondation (débordement ou ruissellement).' + niv + ' Le règlement du plan s\'impose au permis.';
  if (/mouvement|glissement|PPRMT|éboul|chute/i.test(t)) return 'Zone exposée aux mouvements de terrain.' + niv + ' Une étude de sol adaptée est indispensable.';
  if (/archéo/i.test(t)) return INF_EXPL['16'];
  if (/bruit/i.test(t)) return INF_EXPL['14'];
  if (/pr[ée]emption/i.test(t)) return INF_EXPL['04'];
  if (/assainiss|eaux pluvial|imperm/i.test(t)) return INF_EXPL['19'];
  return 'Information à prendre en compte : voir le règlement du PLU.';
}
function supExpl(code, label) {""", 'infExpl')
rep("d.infos.map(p => [p.typeLabel + (p.label && p.label !== p.typeLabel && p.label !== 'Information' ? ' : ' + p.label : ''), INF_EXPL[p.code] || 'Information à prendre en compte : voir le règlement du PLU.']), { size: 8.5 });",
    "d.infos.map(p => [(p.typeLabel === 'Information du PLU' ? '' : p.typeLabel + (p.label && p.label !== 'Information' ? ' : ' : '')) + (p.label && p.label !== p.typeLabel && p.label !== 'Information' ? p.label : ''), infExpl(p.code, p.label)]), { size: 8.5 });", 'inftab')
rep(".replace(/\\s+(abor|abo|ass|asse|zon|zo|peri|péri|prot|pro)\\.?\\s*$/i, '')", ".replace(/\\s+(abor|abo|ass|asse|zon|zo|peri|péri|prot|pro)\\.?\\s*$/i, '').replace(/\\s+I[A-Z0-9]{5}\\s*$/, '')", 'supid')
open(p, 'w', encoding='utf-8').write(s); print('ok G')
s = open(p, encoding='utf-8').read()
a = ".replace(/\\s*abor(ds)?$/i, '').replace(/-I[0-9A-Z]{5,}$/, '')"
if s.count(a) < 1: print('ANCRE abords', s.count(a)); sys.exit(1)
s = s.replace(a, ".replace(/\\s*abor(ds)?$/i, '').replace(/-I[0-9A-Z]{5,}$/, '').replace(/\\s+I[0-9A-Z]{5}$/, '')")
open(p, 'w', encoding='utf-8').write(s); print('ok G2')
