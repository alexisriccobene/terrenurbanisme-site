# Zonages communaux : extrait du plan de zonage officiel de la mairie (tuiles géoréférencées), parcelle entourée en rouge
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable : ' + old[:70])
    s = s.replace(old, new)
rep("""  const zbbox = frame(487 / 280, 3.2, 0.0016);          // plan de zonage""", """  const zbbox = frame(487 / 280, 3.2, 0.0016);          // plan de zonage
  // Extrait du plan officiel de la mairie (tuiles 0,003° x 0,002°, 512 px)
  const pbox = frame(487 / 330, 2.4, 0.0012);
  const pluTilesP = zLocalF ? (async () => {
    const DX = 0.003, DY = 0.002, L = [];
    for (let ix = Math.floor(pbox[0] / DX); ix <= Math.floor(pbox[2] / DX); ix++) for (let iy = Math.floor(pbox[1] / DY); iy <= Math.floor(pbox[3] / DY); iy++) L.push({ ix, iy, b: [ix * DX, iy * DY, (ix + 1) * DX, (iy + 1) * DY] });
    if (L.length > 12) return [];
    const base = (Deno.env.get('SUPABASE_URL') || '') + '/storage/v1/object/public/plu/' + INS + '/t/';
    const R = await Promise.all(L.map(async t => ({ ...t, bytes: await getBytes(base + t.ix + '_' + t.iy + '.jpg', 15000) })));
    return R.filter(t => t.bytes);
  })() : Promise.resolve([]);""")
rep("images: { ortho, cadastre, bbox, plan, planBbox, orthoWide, wideBbox, zortho, zbbox },", "images: { ortho, cadastre, bbox, plan, planBbox, orthoWide, wideBbox, zortho, zbbox, pluTiles: await pluTilesP, pbox },")
rep("""  if (d.doc.local) note('Le plan local d\\'urbanisme de ' + R.commune""", """  if (d.doc.local && I.pluTiles && I.pluTiles.length && I.pbox) {
    const mw = CW, mh = 330; ensure(mh + 40);
    const top = y, bottom = y - mh, x = M, [x0, y0, x1, y1] = I.pbox;
    const sx = lon => (lon - x0) / (x1 - x0) * mw, sy = lat => (y1 - lat) / (y1 - y0) * mh;
    page.pushOperators(PDFLib.pushGraphicsState(), PDFLib.rectangle(x, bottom, mw, mh), PDFLib.clip(), PDFLib.endPath());
    page.drawRectangle({ x, y: bottom, width: mw, height: mh, color: C.white });
    for (const t of I.pluTiles) {
      const im = await img(t.bytes); if (!im) continue;
      const tx = x + sx(t.b[0]), tw2 = sx(t.b[2]) - sx(t.b[0]), th2 = sy(t.b[1]) - sy(t.b[3]), ty = top - sy(t.b[1]);
      page.drawImage(im, { x: tx, y: ty, width: tw2, height: th2 });
    }
    const pp = 'M' + d.parcelCoords.map(q => sx(q[0]).toFixed(1) + ' ' + sy(q[1]).toFixed(1)).join('L') + 'Z';
    page.drawSvgPath(pp, { x, y: top, borderColor: C.white, borderWidth: 4.5, borderOpacity: 0.85 });
    page.drawSvgPath(pp, { x, y: top, borderColor: rgb(0.85, 0.05, 0.05), borderWidth: 2.4 });
    page.pushOperators(PDFLib.popGraphicsState());
    page.drawRectangle({ x, y: bottom, width: mw, height: mh, borderColor: C.ligne, borderWidth: 0.8 });
    const ttl = 'Extrait du plan de zonage officiel de la mairie', w0 = tw(ttl, B, 8) + 16;
    page.drawRectangle({ x: x + 8, y: top - 24, width: w0, height: 16, color: C.white, opacity: 0.94 });
    page.drawText(clean(ttl), { x: x + 16, y: top - 19, size: 8, font: B, color: C.ink });
    y = bottom - 6;
    page.drawText(clean('Plan officiel publié par la commune, recalé sur le cadastre · parcelle entourée en rouge'), { x: M, y: y - 8, size: 7.5, font: F, color: C.muet });
    y -= 22;
  }
  if (d.doc.local) note('Le plan local d\\'urbanisme de ' + R.commune""")
open(p, 'w', encoding='utf-8').write(s); print('patch plu_local4 appliqué')
