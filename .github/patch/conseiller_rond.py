# Carte « Votre conseiller » : photo dans un rond
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "        page.pushOperators(PDFLib.pushGraphicsState(), PDFLib.rectangle(px, y0, 58, 58), PDFLib.clip(), PDFLib.endPath());"
if s.count(old) != 1: sys.exit('ancre introuvable')
new = "        { const r0 = 29, cxx = px + r0, cyy = y0 + r0, kk = 0.5523 * r0; page.pushOperators(PDFLib.pushGraphicsState(), PDFLib.moveTo(cxx + r0, cyy), PDFLib.appendBezierCurve(cxx + r0, cyy + kk, cxx + kk, cyy + r0, cxx, cyy + r0), PDFLib.appendBezierCurve(cxx - kk, cyy + r0, cxx - r0, cyy + kk, cxx - r0, cyy), PDFLib.appendBezierCurve(cxx - r0, cyy - kk, cxx - kk, cyy - r0, cxx, cyy - r0), PDFLib.appendBezierCurve(cxx + kk, cyy - r0, cxx + r0, cyy - kk, cxx + r0, cyy), PDFLib.closePath(), PDFLib.clip(), PDFLib.endPath()); }"
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s); print('patch rond appliqué')
