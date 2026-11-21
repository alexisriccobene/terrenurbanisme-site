# Page de garde : photo ronde du collaborateur à la place du logo dans « Votre interlocuteur »
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("    { const fl = fitLogo(110, 40); cover.drawImage(MQ.im, { x: x + CW - 20 - fl.w, y: top - 12 - fl.h, width: fl.w, height: fl.h }); }",
r"""    let phI = null;
    if (CSV0 && CSV0.photo && CSV0.photo.bytes) { try { phI = CSV0.photo.png ? await pdf.embedPng(CSV0.photo.bytes) : await pdf.embedJpg(CSV0.photo.bytes); } catch (e) { phI = null; } }
    if (phI) {
      const D = 58, r0 = D / 2, cxx = x + CW - 20 - r0, cyy = top - 12 - r0, kk = 0.5523 * r0, sc = Math.max(D / phI.width, D / phI.height), w2 = phI.width * sc, h2 = phI.height * sc;
      cover.drawCircle({ x: cxx, y: cyy, size: r0 + 2, color: C.white });
      cover.pushOperators(PDFLib.pushGraphicsState(), PDFLib.moveTo(cxx + r0, cyy), PDFLib.appendBezierCurve(cxx + r0, cyy + kk, cxx + kk, cyy + r0, cxx, cyy + r0), PDFLib.appendBezierCurve(cxx - kk, cyy + r0, cxx - r0, cyy + kk, cxx - r0, cyy), PDFLib.appendBezierCurve(cxx - r0, cyy - kk, cxx - kk, cyy - r0, cxx, cyy - r0), PDFLib.appendBezierCurve(cxx + kk, cyy - r0, cxx + r0, cyy - kk, cxx + r0, cyy), PDFLib.closePath(), PDFLib.clip(), PDFLib.endPath());
      cover.drawImage(phI, { x: cxx - w2 / 2, y: cyy - h2 / 2, width: w2, height: h2 });
      cover.pushOperators(PDFLib.popGraphicsState());
    } else { const fl = fitLogo(110, 40); cover.drawImage(MQ.im, { x: x + CW - 20 - fl.w, y: top - 12 - fl.h, width: fl.w, height: fl.h }); }""")
rep("select('nom, telephone, email').eq('user_id', dz.user_id).eq('nom', dz.agent).limit(1).maybeSingle(); if (ag) d.conseiller = { nom: ag.nom, tel: ag.telephone || '', email: ag.email || '' }; }",
r"""select('nom, telephone, email, photo').eq('user_id', dz.user_id).eq('nom', dz.agent).limit(1).maybeSingle(); if (ag) { d.conseiller = { nom: ag.nom, tel: ag.telephone || '', email: ag.email || '' }; if (ag.photo) { const { data: pb } = await admin.storage.from('perso').download(ag.photo); if (pb) { const by = new Uint8Array(await pb.arrayBuffer()); if ((by[0] === 0xFF && by[1] === 0xD8) || (by[0] === 0x89 && by[1] === 0x50)) d.conseiller.photo = { bytes: by, png: by[0] === 0x89 }; } } } }""")
open(p, 'w', encoding='utf-8').write(s); print('patch photo interlocuteur appliqué')
