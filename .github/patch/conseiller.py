# Version client : carte « Votre conseiller » (photo, téléphone, e-mail du collaborateur) dans la recommandation de l'agence
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("  const { data: dos } = await admin.from('dossiers').select('id, user_id, stripe_session_id, perso').eq('id', dossierId).maybeSingle();",
    "  const { data: dos } = await admin.from('dossiers').select('id, user_id, stripe_session_id, perso, agent').eq('id', dossierId).maybeSingle();")
rep("  d.perso = { exclure: P.exclure || [], sans: P.sans || [], reco: P.reco || {}, client: P.client || {}, photos };\n",
r"""  d.perso = { exclure: P.exclure || [], sans: P.sans || [], reco: P.reco || {}, client: P.client || {}, photos };
  try {
    if (dos.agent) {
      const { data: ag } = await admin.from('pro_agents').select('nom, telephone, email, photo').eq('user_id', dos.user_id).eq('nom', dos.agent).limit(1).maybeSingle();
      if (ag) {
        const c = { nom: ag.nom, tel: ag.telephone || '', email: ag.email || '' };
        if (ag.photo && String(ag.photo).startsWith(dos.user_id + '/')) {
          const { data: pb } = await admin.storage.from('perso').download(ag.photo);
          if (pb) { const by = new Uint8Array(await pb.arrayBuffer()); const png = by[0] === 0x89 && by[1] === 0x50, jpg = by[0] === 0xFF && by[1] === 0xD8; if ((png || jpg) && by.length < 4 * 1024 * 1024) c.photo = { bytes: by, png }; }
        }
        d.perso.conseiller = c;
      }
    }
  } catch (e) { console.warn('conseiller', String(e && e.message || e).slice(0, 120)); }
""")
rep("PERSO.reco.designation || PERSO.reco.type || PERSO.reco.fiche ||", "PERSO.reco.designation || PERSO.reco.type || PERSO.reco.fiche || PERSO.conseiller ||")
rep("    chapter(++CHN, 'Recommandation de l\\'agence', (MQ && MQ.nom ? MQ.nom : 'Votre conseiller') + (CLI ? ' · pour ' + CLI : ''));\n",
r"""    chapter(++CHN, 'Recommandation de l\'agence', (MQ && MQ.nom ? MQ.nom : 'Votre conseiller') + (CLI ? ' · pour ' + CLI : ''));
    const CS = PERSO.conseiller;
    if (CS && CS.nom) {
      ensure(96);
      const ch = 78, ph = CS.photo ? await img(CS.photo.bytes, CS.photo.png) : null, px = M + 14, tx = ph ? M + 14 + 58 + 16 : M + 20;
      page.drawRectangle({ x: M, y: y - ch, width: CW, height: ch, color: C.cream });
      page.drawRectangle({ x: M, y: y - ch, width: 4, height: ch, color: C.t });
      if (ph) {
        const r = Math.max(58 / ph.width, 58 / ph.height), w2 = ph.width * r, h2 = ph.height * r, y0 = y - 10 - 58;
        page.pushOperators(PDFLib.pushGraphicsState(), PDFLib.rectangle(px, y0, 58, 58), PDFLib.clip(), PDFLib.endPath());
        page.drawImage(ph, { x: px + (58 - w2) / 2, y: y0 + (58 - h2) / 2, width: w2, height: h2 });
        page.pushOperators(PDFLib.popGraphicsState());
      }
      page.drawText(clean('VOTRE CONSEILLER'), { x: tx, y: y - 20, size: 7.5, font: B, color: C.t });
      page.drawText(clean(CS.nom), { x: tx, y: y - 38, size: 14, font: B, color: C.ink });
      const lc = [MQ && MQ.nom ? MQ.nom : '', CS.tel, CS.email].filter(Boolean).join('  ·  ');
      if (lc) page.drawText(clean(lc), { x: tx, y: y - 56, size: 9.5, font: F, color: C.muet });
      y -= ch + 14;
    }
""")
open(p, 'w', encoding='utf-8').write(s); print('patch conseiller appliqué')
