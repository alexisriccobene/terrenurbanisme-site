"""Pente : une seule valeur dans tout le rapport (pente moyenne du terrain, plan moyen sur 25 points), au lieu de la pente maximale entre deux points dans la synthèse et l'identification."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', c, a[:90]); sys.exit(1)
    s = s.replace(a, b)
rep("if (c.alti && c.alti.slope >= 15) pts.push({ key: 'info', text: 'Terrain en pente marquée (environ ' + c.alti.slope + ' %) : surcoût probable de terrassement.' });",
    "{ const sl = c.relief && c.relief.slope != null ? c.relief.slope : (c.alti ? c.alti.slope : null); if (sl != null && sl >= 15) pts.push({ key: 'info', text: 'Terrain en pente marquée (pente moyenne d\\'environ ' + sl + ' %) : surcoût probable de terrassement.' }); }")
rep("['Pente estimée', d.alti && d.alti.slope != null ? d.alti.slope + ' %' + (d.alti.slope >= 15 ? ' (terrain en pente marquée)' : d.alti.slope >= 5 ? ' (pente modérée)' : ' (terrain plutôt plat)') : null],",
    "(() => { const sl = d.relief && d.relief.slope != null ? d.relief.slope : (d.alti && d.alti.slope != null ? d.alti.slope : null); return ['Pente moyenne', sl != null ? sl + ' %' + (sl >= 15 ? ' (terrain en pente marquée)' : sl >= 5 ? ' (pente modérée)' : ' (terrain plutôt plat)') : null]; })(),")
open(p, 'w', encoding='utf-8').write(s); print('ok')
# Plans de prévention : un atlas des zones inondables n'est pas un PPR, libellé exact selon le cas
s = open(p, encoding='utf-8').read()
a = "['Plans de prévention (PPR)', RK.ppr && RK.ppr.length ? RK.ppr.join(' ; ') : 'Aucun plan de prévention des risques recensé']"
if s.count(a) != 1: print('ANCRE PPR', s.count(a)); sys.exit(1)
b = "[(RK.ppr || []).length && (RK.ppr || []).every(x => /atlas/i.test(String(x))) ? 'Atlas des zones inondables (AZI)' : (RK.ppr || []).some(x => /atlas/i.test(String(x))) ? 'Plans de prévention et atlas (PPR, AZI)' : 'Plans de prévention (PPR)', RK.ppr && RK.ppr.length ? RK.ppr.join(' ; ') : 'Aucun plan de prévention des risques recensé']"
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok ppr')
