"""Cartes : tracés coupés au cadre (plus rien ne déborde sur la page). Fibre : adresses lisibles, 3 au plus, pas de distances contradictoires quand le terrain a ses propres adresses."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(a, b, label):
    global s
    n = s.count(a)
    if n != 1: print('ANCRE', label, n); sys.exit(1)
    s = s.replace(a, b)
# 1. mapBox : découpe au cadre
a = "if (!drew) page.drawRectangle({ x, y: bottom, width: mw, height: mh, color: C.cream });"
one(a, a + "\n    page.pushOperators(PDFLib.pushGraphicsState(), PDFLib.rectangle(x, bottom, mw, mh), PDFLib.clip(), PDFLib.endPath());", 'clip')
a = "page.drawRectangle({ x, y: bottom, width: mw, height: mh, borderColor: C.ligne, borderWidth: 0.8 });\n    if (opts.title) {"
one(a, "page.pushOperators(PDFLib.popGraphicsState());\n    " + a, 'pop')
# 2. Fibre : libellés propres
a = "const ad = o => [o.num, o.voie].filter(Boolean).join(' ') || o.lieu || 'Adresse sans nom';"
b = r"""const PET = /^(di|de|du|des|la|le|les|l|d|et|a|à|en|u|e)$/i;
      const clA = t => { let v = String(t || '').replace(/\bparcelle\s+[0-9a-z]{8,16}\b/gi, '').replace(/\blieu[- ]dit\b/gi, '').replace(/\s+/g, ' ').trim(); if (!v) return ''; if (v === v.toUpperCase() || v === v.toLowerCase()) v = v.toLowerCase().split(' ').map((w, i) => i && PET.test(w) ? w : w.charAt(0).toUpperCase() + w.slice(1)).join(' '); return v; };
      const ad = o => { const n = /^0+$/.test(String(o.num || '').trim()) ? '' : String(o.num || '').trim(); return clA([n, o.voie].filter(Boolean).join(' ')) || clA(o.lieu) || 'Adresse sans nom'; };
      const adL = L => { const u = [...new Set(L.map(ad))]; return u.slice(0, 3).join(', ') + (u.length > 3 ? ' et ' + (u.length - 3) + ' autre' + (u.length > 4 ? 's' : '') : ''); };"""
one(a, b, 'ad')
one("' sur la parcelle (' + opF.map(ad).join(', ') + ') '", "' sur la parcelle (' + adL(opF) + ') '", 'liste')
a = "      if (ok) kvn([\n        ['Adresse la plus proche',"
one(a, "      if (ok && opF.length) kvn([\n        ['Adresses sur la parcelle', fmt(OP.length) + ', dont ' + fmt(opF.length) + ' raccordable' + (opF.length > 1 ? 's' : '') + ' à la fibre'],\n        ['Adresses fibrées à moins de 400 m', fmt(FB.f400) + ' sur ' + fmt(FB.n400)],\n        ['Technologies disponibles à proximité', FB.techs.map(t => TECHNO_L[t] || t).filter((v, i, a) => a.indexOf(v) === i).join(', ')]\n      ], { lw: 0.4 });\n      else if (ok) kvn([\n        ['Adresse la plus proche',", 'kvn')
open(p, 'w', encoding='utf-8').write(s); print('ok clip fibre')
