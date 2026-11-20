# Version client : lien court terrenurbanisme.com/r/c-xxxx ; pas de page presque vide (fin de paragraphe tenue sur la page) ;
# chapitre « Recommandation de l'agence » mieux mis en page.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)

# 1. Lien court de la version client
rep("""  slug = decodeURIComponent(slug).replace(/\\.pdf$/i, '');
  if (!/^[a-z0-9-]{8,120}$/.test(slug)) return new Response('Rapport introuvable', { status: 404 });
""", """  slug = decodeURIComponent(slug).replace(/\\.pdf$/i, '');
  if (!/^[a-z0-9-]{8,120}$/.test(slug)) return new Response('Rapport introuvable', { status: 404 });
  if (/^c-[0-9a-f]{12}$/.test(slug)) {
    const h = slug.slice(2), lo = h.slice(0, 8) + '-' + h.slice(8, 12) + '-0000-0000-000000000000', hi = h.slice(0, 8) + '-' + h.slice(8, 12) + '-ffff-ffff-ffffffffffff';
    const { data: cr } = await admin.from('dossiers').select('perso').gte('id', lo).lte('id', hi).limit(1).maybeSingle();
    const P = cr && cr.perso;
    if (!P || P.status !== 'pret' || !P.path) return new Response('Rapport introuvable ou en cours de préparation.', { status: 404, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
    const { data: cb } = await admin.storage.from('dossiers').download(P.path);
    if (!cb) return new Response('Rapport indisponible', { status: 500 });
    const nm = String(P.file || 'Rapport.pdf').normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/[^A-Za-z0-9.-]+/g, '-');
    return new Response(cb, { headers: { 'Content-Type': 'application/pdf', 'Content-Disposition': `inline; filename="${nm}"`, 'Cache-Control': 'private, max-age=60', 'X-Robots-Tag': 'noindex' } });
  }
""")
rep("""      client = { url: cu && cu.signedUrl, view: cv && cv.signedUrl };""",
    """      client = { url: cu && cu.signedUrl, view: cv && cv.signedUrl, court: SITE + '/r/c-' + String(dos.id).replace(/-/g, '').slice(0, 12) };""")

# 2. Pas de page presque vide : une fin de paragraphe de 1 ou 2 lignes reste sur la page (marge basse)
rep("""    const lines = wrap(t, font, size, width);
    for (const l of lines) { ensure(lh); page.drawText(l, { x, y: y - size, size, font, color: o.color || C.ink }); y -= lh; }""",
"""    const lines = wrap(t, font, size, width);
    const fit = Math.max(0, Math.floor((y - 72) / lh)), rest = lines.length - fit, tient = rest > 0 && rest <= 2 && y - lines.length * lh >= 56;
    for (const l of lines) { if (!tient) ensure(lh); page.drawText(l, { x, y: y - size, size, font, color: o.color || C.ink }); y -= lh; }""")
rep("""    const [c, bg] = VC[key] || VC.info, lines = wrap(t, F, 9.5, CW - 32), h = lines.length * 14 + 18;
    ensure(h + 6);""", """    const [c, bg] = VC[key] || VC.info, lines = wrap(t, F, 9.5, CW - 32), h = lines.length * 14 + 18;
    if (!(y - h >= 56 && y - h < 72)) ensure(h + 6);""")
rep("""    const size = o.size || 10, lines = wrap(t, F, size, CW - 16); ensure(lines.length * size * 1.5 + 2);""",
    """    const size = o.size || 10, lines = wrap(t, F, size, CW - 16), bh = lines.length * size * 1.5 + 2; if (!(y - bh >= 56 && lines.length <= 2)) ensure(bh);""")

# 3. Recommandation de l'agence : texte et photos
rep("""Il complète la fourchette calculée à partir des ventes publiées présentée au chapitre précédent.""",
    """Il s\\'appuie aussi sur les ventes réelles relevées autour du terrain, présentées dans ce rapport.""")
rep("""      h3('Photos du bien');
      const gw = (CW - 12) / 2, gh = 170;
      for (let i = 0; i < PH.length; i += 2) {
        ensure(gh + 14);
        for (let j = 0; j < 2 && i + j < PH.length; j++) {
          const im = await img(PH[i + j].bytes, PH[i + j].png); if (!im) continue;
          const r = Math.min(gw / im.width, gh / im.height), w2 = im.width * r, h2 = im.height * r, x0 = M + j * (gw + 12);
          page.drawRectangle({ x: x0, y: y - gh, width: gw, height: gh, color: C.cream });
          page.drawImage(im, { x: x0 + (gw - w2) / 2, y: y - gh + (gh - h2) / 2, width: w2, height: h2 });
        }
        y -= gh + 12;
      }""", """      // Photos recadrées sur une grille régulière : la première en grand, les suivantes trois par ligne
      const cover = async (ph, x0, yt, w, h) => {
        const im = await img(ph.bytes, ph.png); if (!im) return;
        const r = Math.max(w / im.width, h / im.height), w2 = im.width * r, h2 = im.height * r;
        page.pushOperators(PDFLib.pushGraphicsState(), PDFLib.rectangle(x0, yt - h, w, h), PDFLib.clip(), PDFLib.endPath());
        page.drawImage(im, { x: x0 + (w - w2) / 2, y: yt - h + (h - h2) / 2, width: w2, height: h2 });
        page.pushOperators(PDFLib.popGraphicsState());
      };
      const gap = 8, bigH = PH.length === 1 ? 300 : 230, sw = (CW - 2 * gap) / 3, sh = sw * 0.72;
      ensure(24 + bigH + (PH.length > 1 ? sh + gap : 0)); h3('Photos du bien', 10);
      await cover(PH[0], M, y, CW, bigH); y -= bigH + gap;
      for (let i = 1; i < PH.length; i += 3) {
        ensure(sh + gap);
        for (let j = 0; j < 3 && i + j < PH.length; j++) await cover(PH[i + j], M + j * (sw + gap), y, sw, sh);
        y -= sh + gap;
      }
      y -= 6;""")
open(p, 'w', encoding='utf-8').write(s); print('patch client_lien appliqué')
