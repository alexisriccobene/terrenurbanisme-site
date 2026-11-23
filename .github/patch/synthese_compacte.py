# Synthèse : évite une page presque vide (points d'attention ou « Votre projet » qui débordent de quelques lignes) en resserrant la taille du texte ;
# taxe piscine du projet issue des données 2026
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a)); s = s.replace(a, b)
rep("""    h3('Points d\\'attention');
    d.points.forEach(pt => bullet(pt.text, { color: (VC[pt.key] || VC.info)[0] }));""", """    const hb = (L0, sz) => L0.reduce((a, t) => a + wrap(t, F, sz, CW - 16).length * sz * 1.5 + 5, 0) + 30;
    const PT0 = d.points.map(pt => pt.text), szP = (y - hb(PT0, 10) < 72 && y - hb(PT0, 8.8) >= 72) ? 8.8 : 10;
    h3('Points d\\'attention', szP < 10 ? hb(PT0, szP) : undefined);
    d.points.forEach(pt => bullet(pt.text, { size: szP, color: (VC[pt.key] || VC.info)[0] }));""")
rep("""    L.forEach(t2 => bullet(t2, { color: C.t || (VC.info)[0] }));""", """    { const hb2 = (sz) => L.reduce((a, t) => a + wrap(t, F, sz, CW - 16).length * sz * 1.5 + 5, 0); const szL = (y - hb2(10) < 72 && y - hb2(8.8) >= 72) ? 8.8 : 10;
      L.forEach(t2 => bullet(t2, { size: szL, color: C.t || (VC.info)[0] })); }""")
rep("L.push('Taxe d\\'aménagement : forfait de 250 € par m² de bassin,", "L.push('Taxe d\\'aménagement : forfait de ' + fmt((d.ta && d.ta.piscine) || 251) + ' € par m² de bassin,")
open(p, 'w', encoding='utf-8').write(s); print('patch synthèse compacte appliqué')
