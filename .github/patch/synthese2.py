# Rapport synthétique : tenir en 2 pages ; assainissement lu sur la partie constructible
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + old[:80])
    s = s.replace(old, new)
rep("const Z0a = d.zones && d.zones[0], tz = String((Z0a && Z0a.tz) || '').toUpperCase(), EAa = d.eau || {}, AC = EAa.ac, connu = !!EAa.sispea;",
    "const Z0a = (d.verdict.partiel && (d.zones || []).find(z => z.code === d.verdict.partiel[0])) || (d.zones && d.zones[0]), tz = String((Z0a && Z0a.tz) || '').toUpperCase(), EAa = d.eau || {}, AC = EAa.ac, connu = !!EAa.sispea;")
rep("(an.autorise || []).slice(0, 3).forEach(t => bullet(cut(t, 150), { size: 9 }));", "(an.autorise || []).slice(0, 2).forEach(t => bullet(cut(t, 120), { size: 8.8 }));")
rep("rg.map(r => [r.critere, cut(r.regle, 190)]), { size: 8.5 });", "rg.map(r => [r.critere, cut(r.regle, 150)]), { size: 8.3 });")
rep(".slice(0, 6);\n    if (pts.length) { h3('Risques et contraintes à connaître', 60); pts.forEach(pt => bullet(cut(pt.text, 200), { size: 9, color: (VC[pt.key] || VC.info)[0] })); }",
    ".slice(0, 5);\n    if (pts.length) { h3('Risques et contraintes à connaître', 60); pts.forEach(pt => bullet(cut(pt.text, 150), { size: 8.6, color: (VC[pt.key] || VC.info)[0] })); }")
rep("'Les risques à l\\'adresse et l\\'état des risques (ERP) pré-rempli, à remettre à l\\'acquéreur', 'Eau, électricité, assainissement : coûts, démarches et contacts', 'Les ventes réelles autour du terrain, l\\'historique aérien et les permis accordés', 'Les démarches, les délais et la taxe d\\'aménagement de votre projet'];\n      const lh = 13, bh = 58 + L.length * lh + 26;",
    "'Risques détaillés et état des risques (ERP) pré-rempli · eau, électricité, assainissement : coûts et contacts', 'Ventes réelles autour du terrain, historique aérien, permis accordés, démarches et taxe d\\'aménagement'];\n      const lh = 12, bh = 52 + L.length * lh + 24;")
rep("L.forEach((t, i) => { page.drawCircle({ x: M + 22, y: y - 56 - i * lh + 3, size: 1.8, color: C.t }); page.drawText(clean(t), { x: M + 30, y: y - 56 - i * lh, size: 8.8, font: F, color: C.ink }); });",
    "L.forEach((t, i) => { page.drawCircle({ x: M + 22, y: y - 54 - i * lh + 3, size: 1.8, color: C.t }); page.drawText(clean(t), { x: M + 30, y: y - 54 - i * lh, size: 8.4, font: F, color: C.ink }); });")
rep("page.drawText(clean(cta), { x: M + 18, y: y - bh + 16, size: 9, font: B, color: C.t });", "page.drawText(clean(cta), { x: M + 18, y: y - bh + 14, size: 9, font: B, color: C.t });")
open(p, 'w', encoding='utf-8').write(s); print('patch synthese2 appliqué')
