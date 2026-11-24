"""Relecture des rapports par profil : service sans réponse signalé, servitudes regroupées, SAFER seulement en zone A ou N, surfaces cadastrale et mesurée, accords."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
rep("try { await sirene(lab, naf); } catch (e) { console.warn('Sirene', lab, String(e && e.message || e).slice(0, 80)); }",
    "try { await sirene(lab, naf); } catch (e) { console.warn('Sirene', lab, String(e && e.message || e).slice(0, 80)); out.push({ cat: lab, ko: true }); }")
rep("PR.map(x => x.aucun ?", "PR.map(x => x.ko ? [x.cat, 'Source momentanément indisponible', '—'] : x.aucun ?")
# Servitudes : types regroupés avec leur nombre
SUPT = "(() => { const m = {}; sup.forEach(x => { m[x.typeLabel] = (m[x.typeLabel] || 0) + 1; }); return Object.entries(m).map(([k, v]) => v > 1 ? k + ' (' + v + ')' : k).join(' ; '); })()"
rep("sup.length ? (sup.length > 1 ? sup.length + ' servitudes : ' : '1 servitude : ') + sup.slice(0, 3).map(x => x.typeLabel).join(' ; ') + (sup.length > 3 ? '…' : '')",
    "sup.length ? (sup.length > 1 ? sup.length + ' servitudes : ' : '1 servitude : ') + " + SUPT)
rep("(zc.length ? ' · zone ' + zc.join(', ') : '') : (zc.length ? 'Zone ' + zc.join(', ') : 'Voir le chapitre')",
    "(zc.length ? ' · zone ' + zc.join(', ') : ' · zone non disponible en ligne (voir le chapitre)') : (zc.length ? 'Zone ' + zc.join(', ') : 'Voir le chapitre')")
# Géomètre : SAFER seulement si zone A ou N
rep("       'Terrain en zone agricole ou naturelle : la division et la vente peuvent être soumises au droit de préemption de la SAFER (voir « Conditions de vente du terrain » le cas échéant).'].forEach(t2 => bullet(t2, { size: 9.5 }));",
    "       (d.zones || []).some(z => /^(A|N)/i.test(String(z.code || ''))) ? 'Partie en zone agricole ou naturelle : la division et la vente peuvent être soumises au droit de préemption de la SAFER (voir « Conditions de vente du terrain »).' : ''].filter(Boolean).forEach(t2 => bullet(t2, { size: 9.5 }));")
# Maître d'œuvre : surface cadastrale et surface mesurée
rep("['Surface du terrain', R.contenance ? fmt(R.contenance) + ' m² (cadastre)' : null],",
    "['Surface du terrain', R.contenance ? fmt(R.contenance) + ' m² (cadastre)' + (R.areaCalc && Math.abs(R.areaCalc - R.contenance) / R.contenance > 0.1 ? ' · ' + fmt(R.areaCalc) + ' m² mesurés sur le plan : écart à faire lever par un géomètre' : '') : null],")
rep("fmt(P.dxf.nParc) + ' parcelles, ' + fmt(P.dxf.nBat) + ' bâtiments, '", "fmt(P.dxf.nParc) + (P.dxf.nParc > 1 ? ' parcelles, ' : ' parcelle, ') + (P.dxf.nBat ? fmt(P.dxf.nBat) + (P.dxf.nBat > 1 ? ' bâtiments, ' : ' bâtiment, ') : 'aucun bâtiment, ')")
open(p, 'w', encoding='utf-8').write(s); print('ok profils7')
