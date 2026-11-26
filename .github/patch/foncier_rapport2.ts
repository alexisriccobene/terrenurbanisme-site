// ---------- PDF ----------
const C = {
  t: [0.639, 0.275, 0.173], th: [0.53, 0.22, 0.12], ink: [0.165, 0.114, 0.09], muet: [0.43, 0.38, 0.35],
  ligne: [0.906, 0.867, 0.835], soft: [0.976, 0.949, 0.933], soft2: [0.965, 0.898, 0.867],
  ok: [0.18, 0.49, 0.31], okbg: [0.898, 0.949, 0.918], non: [0.70, 0.25, 0.18], nonbg: [0.973, 0.902, 0.886],
  yel: [1, 0.85, 0.2], white: [1, 1, 1]
};
async function getBytes(u: string, ms = 25000) {
  for (let t = 0; t < 2; t++) {
    try { const r = await fetch(u, { signal: AbortSignal.timeout(ms) }); if (r.ok) { const b = new Uint8Array(await r.arrayBuffer()); if (b.length > 800) return b; } } catch (_) {}
  }
  return null;
}
const wmsU = (layer: string, b: number[], w: number, h: number, fmt = 'image/jpeg') => `https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=${layer}&STYLES=&CRS=EPSG:4326&BBOX=${b[1]},${b[0]},${b[3]},${b[2]}&WIDTH=${w}&HEIGHT=${h}&FORMAT=${fmt}&TRANSPARENT=${fmt === 'image/png' ? 'TRUE' : 'FALSE'}`;
// Cadre géographique centré, au rapport largeur / hauteur demandé, demi-hauteur en km
const cadre = (lat: number, lon: number, demiKm: number, ratio: number) => { const k = Math.cos(lat * Math.PI / 180), dLat = demiKm / 111, dLon = dLat * ratio / k; return [lon - dLon, lat - dLat, lon + dLon, lat + dLat]; };
const telF = (v: any) => { const s = String(v || '').replace(/[^\d+]/g, ''); return /^0\d{9}$/.test(s) ? s.replace(/(\d{2})(?=\d)/g, '$1 ') : /^\+33\d{9}$/.test(s) ? '+33 ' + s.slice(3, 4) + ' ' + s.slice(4).replace(/(\d{2})(?=\d)/g, '$1 ') : String(v || '').trim(); };
const siteF = (v: any) => String(v || '').trim().replace(/^https?:\/\//i, '').replace(/^www\./i, '').replace(/\/+$/, '');
const dateF = (d: any) => d ? String(d).slice(0, 10).split('-').reverse().join('/') : '';
const nomFichier = (r: any) => slugify(['recherche-fonciere', r.commune, r.rayon_km + 'km', r.societe || r.nom || ''].filter(Boolean).join('-')).slice(0, 110);

async function buildPdf(q: any, sites: any[], ref: string, X: any = {}) {
  const pdf = await PDFLib.PDFDocument.create();
  pdf.registerFontkit(fontkit);
  const [fr, fb, fm] = await Promise.all([getBytes(`${SITE}/assets/report/tu-regular.ttf`), getBytes(`${SITE}/assets/report/tu-bold.ttf`), getBytes(`${SITE}/assets/report/tu-medium.ttf`)]);
  const F = fr ? await pdf.embedFont(fr, { subset: true }) : await pdf.embedFont(PDFLib.StandardFonts.Helvetica);
  const B = fb ? await pdf.embedFont(fb, { subset: true }) : await pdf.embedFont(PDFLib.StandardFonts.HelveticaBold);
  const Md = fm ? await pdf.embedFont(fm, { subset: true }) : F;
  const rgb = (c: number[]) => PDFLib.rgb(c[0], c[1], c[2]);
  const W = 595.28, H = 841.89, M = 48, CW = W - 2 * M;
  const clean = (t: any) => String(t ?? '').replace(/[  ]/g, ' ').replace(/[^\x00-ɏ€’‘“”«»–—…·²³°•✓]/g, '');
  const tw = (t: any, f: any, s: number) => f.widthOfTextAtSize(clean(t), s);
  const wrap = (t: any, f: any, s: number, w: number) => {
    const out: string[] = [];
    for (const para of clean(t).split('\n')) {
      let line = '';
      for (const word of para.split(/\s+/)) { const tt = line ? line + ' ' + word : word; if (tw(tt, f, s) > w && line) { out.push(line); line = word; } else line = tt; }
      out.push(line);
    }
    return out;
  };
  const cut = (t: any, f: any, s: number, w: number) => { let x = clean(t); if (tw(x, f, s) <= w) return x; while (x && tw(x + '…', f, s) > w) x = x.slice(0, -1); return x.trim() + '…'; };
  const commune = clean(X.nomC || q.commune), besoinL = BESOIN[q.besoin] || 'Terrain ou bâtiment';
  const titreDoc = clean(`Recherche foncière – ${commune} – ${q.rayon_km} km` + (q.societe ? ' – ' + q.societe : ''));
  pdf.setTitle(titreDoc, { showInWindowTitleBar: true });
  pdf.setAuthor('TerrenUrbanisme'); pdf.setCreator('TerrenUrbanisme'); pdf.setProducer('TerrenUrbanisme');
  pdf.setSubject('Terrains et bâtiments disponibles pour l\'implantation d\'une entreprise'); pdf.setLanguage('fr-FR');

  // ---------- Éléments graphiques ----------
  function logo(p: any, x: number, yTop: number, s: number, c: any, fill?: any) {
    const k = s / 64;
    p.drawCircle({ x: x + 32 * k, y: yTop - 32 * k, size: 29.5 * k, borderColor: c, borderWidth: 3 * k });
    p.drawCircle({ x: x + 32 * k, y: yTop - 32 * k, size: 23 * k, borderColor: c, borderWidth: 1.4 * k, borderDashArray: [2.2 * k, 3.2 * k] });
    p.drawSvgPath('M20 26L37 20L45 36L29 44Z', { x, y: yTop, scale: k, borderColor: c, borderWidth: 3.2 * k, color: fill || undefined });
    p.drawCircle({ x: x + 33 * k, y: yTop - 32 * k, size: 3.6 * k, color: c });
  }
  function rrect(p: any, x: number, yTop: number, w: number, h: number, r: number, o: any) { r = Math.min(r, h / 2, w / 2); p.drawSvgPath(`M${r} 0H${w - r}Q${w} 0 ${w} ${r}V${h - r}Q${w} ${h} ${w - r} ${h}H${r}Q0 ${h} 0 ${h - r}V${r}Q0 0 ${r} 0Z`, { x, y: yTop, ...o }); }
  const linkAt = (p: any, x: number, yb: number, w: number, h: number, u: string) => {
    try { const a = pdf.context.obj({ Type: 'Annot', Subtype: 'Link', Rect: [x, yb, x + w, yb + h], Border: [0, 0, 0], A: { Type: 'Action', S: 'URI', URI: PDFLib.PDFString.of(u) } }); p.node.addAnnot(pdf.context.register(a)); } catch (e) { console.error('lien', e); }
  };
  function ico(p: any, cx: number, cy: number, kind: string, bg: any, fg: any) {
    p.drawCircle({ x: cx, y: cy, size: 8.5, color: bg });
    if (kind === 'tel') { rrect(p, cx - 3, cy + 5, 6, 10, 1.5, { borderColor: fg, borderWidth: 1.1 }); p.drawCircle({ x: cx, y: cy - 3.2, size: 0.7, color: fg }); }
    else if (kind === 'mail') { p.drawRectangle({ x: cx - 4.6, y: cy - 3.2, width: 9.2, height: 6.4, borderColor: fg, borderWidth: 1 }); p.drawSvgPath('M0 0L4.6 3.8L9.2 0', { x: cx - 4.6, y: cy + 3.2, borderColor: fg, borderWidth: 1 }); }
    else if (kind === 'pin') { p.drawCircle({ x: cx, y: cy + 1, size: 3.6, borderColor: fg, borderWidth: 1.1 }); p.drawSvgPath('M-2.6 2.6L0 6.6L2.6 2.6', { x: cx, y: cy - 1, borderColor: fg, borderWidth: 1.1 }); }
    else { p.drawCircle({ x: cx, y: cy, size: 4.8, borderColor: fg, borderWidth: 1 }); p.drawEllipse({ x: cx, y: cy, xScale: 2, yScale: 4.8, borderColor: fg, borderWidth: 0.9 }); p.drawLine({ start: { x: cx - 4.8, y: cy }, end: { x: cx + 4.8, y: cy }, thickness: 0.9, color: fg }); }
  }
  // Pastilles de contact cliquables ; renvoie la hauteur utilisée
  function chips(p: any, x0: number, yTop: number, maxW: number, list: any[], st: any = {}) {
    const sz = st.size || 8.6, ph = 22, gap = 7, ws = list.map(c => 26 + tw(c.v, B, sz) + 10);
    const rows: number[][] = [[]]; let rw = 0;
    list.forEach((c, i) => { if (rw && rw + gap + ws[i] > maxW) { rows.push([]); rw = 0; } rows[rows.length - 1].push(i); rw += (rw ? gap : 0) + ws[i]; });
    if (st.measure) return rows.length * ph + (rows.length - 1) * 6;
    rows.forEach((row, ri) => {
      let x = x0; const yt = yTop - ri * (ph + 6);
      row.forEach(i => {
        const c = list[i];
        rrect(p, x, yt, ws[i], ph, 11, { color: rgb(st.bg || C.white), borderColor: rgb(C.ligne), borderWidth: 0.6 });
        ico(p, x + 12, yt - ph / 2, c.k, rgb(C.t), rgb(C.white));
        p.drawText(clean(c.v), { x: x + 25, y: yt - ph / 2 - sz * 0.35, size: sz, font: B, color: rgb(C.ink) });
        if (c.uri) linkAt(p, x, yt - ph, ws[i], ph, c.uri);
        x += ws[i] + gap;
      });
    });
    return rows.length * ph + (rows.length - 1) * 6;
  }
  // Étiquette arrondie ; renvoie la largeur
  const pill = (p: any, t: string, x: number, yTop: number, bg: any, fg: any, sz = 7.8) => { const s = clean(t), w = tw(s, B, sz) + 14; rrect(p, x, yTop, w, 16, 8, { color: rgb(bg) }); p.drawText(s, { x: x + 7, y: yTop - 11.2, size: sz, font: B, color: rgb(fg) }); return w; };
  const pills = (p: any, list: any[], x0: number, yTop: number, maxW: number) => { let x = x0, yy = yTop; for (const [t, bg, fg] of list) { if (!t) continue; const w = tw(clean(t), B, 7.8) + 14; if (x > x0 && x + w > x0 + maxW) { x = x0; yy -= 20; } pill(p, t, x, yy, bg, fg); x += w + 5; } return yTop - yy + 16; };
  async function img(bytes: any) { if (!bytes) return null; try { return await pdf.embedJpg(bytes); } catch (_) { try { return await pdf.embedPng(bytes); } catch (_) { return null; } } }

  // ---------- Pages ----------
  let page: any, y = 0;
  const pages: any[] = [];
  let chap = 0;
  const newPage = () => {
    page = pdf.addPage([W, H]); pages.push(page);
    logo(page, M, H - 30, 20, rgb(C.t), rgb(C.soft2));
    page.drawText('TerrenUrbanisme', { x: M + 27, y: H - 45, size: 10.5, font: B, color: rgb(C.ink) });
    const h = clean('Recherche foncière · ' + commune + ' · ' + q.rayon_km + ' km');
    page.drawText(h, { x: W - M - tw(h, Md, 8.5), y: H - 44, size: 8.5, font: Md, color: rgb(C.t) });
    page.drawLine({ start: { x: M, y: H - 60 }, end: { x: W - M, y: H - 60 }, thickness: 0.6, color: rgb(C.ligne) });
    y = H - 92;
  };
  const section = (titre: string, chapeau?: string) => {
    newPage(); chap++;
    page.drawText(String(chap).padStart(2, '0'), { x: M, y, size: 10, font: B, color: rgb(C.t) });
    page.drawLine({ start: { x: M + 20, y: y + 3.5 }, end: { x: M + 44, y: y + 3.5 }, thickness: 1.2, color: rgb(C.t) });
    y -= 30;
    for (const l of wrap(titre, B, 23, CW)) { page.drawText(l, { x: M, y, size: 23, font: B, color: rgb(C.ink) }); y -= 28; }
    y -= 2;
    if (chapeau) { for (const l of wrap(chapeau, F, 10.5, CW)) { page.drawText(l, { x: M, y, size: 10.5, font: F, color: rgb(C.muet) }); y -= 15.5; } y -= 10; }
  };
  const ensure = (h: number) => { if (y - h < 70) newPage(); };
  const text = (t: string, o: any = {}) => {
    const s = o.size || 9.5, f = o.bold ? B : o.md ? Md : F;
    for (const l of wrap(t, f, s, o.w || CW)) { ensure(s + 4); page.drawText(l, { x: o.x || M, y, size: s, font: f, color: rgb(o.color || C.ink) }); y -= s * 1.45; }
    y -= o.after ?? 4;
  };
  const h3 = (t: string) => { ensure(70); y -= 8; page.drawText(clean(t), { x: M, y, size: 13.5, font: B, color: rgb(C.ink) }); y -= 22; };
  const note = (t: string, tone: 'info' | 'non' = 'info') => {
    const ls = wrap(t, F, 9, CW - 34), h = ls.length * 13 + 22; ensure(h + 8);
    rrect(page, M, y, CW, h, 10, { color: rgb(tone === 'non' ? C.nonbg : C.soft) });
    page.drawRectangle({ x: M, y: y - h + 8, width: 3, height: h - 16, color: rgb(tone === 'non' ? C.non : C.t) });
    ls.forEach((l, i) => page.drawText(l, { x: M + 18, y: y - 16 - i * 13, size: 9, font: F, color: rgb(C.ink) }));
    y -= h + 12;
  };
  const kv = (rows: any[]) => {
    for (const [k, v] of rows) {
      if (v == null || v === '') continue;
      const ls = wrap(String(v), F, 9.5, CW * 0.64), kl = wrap(String(k), B, 9, CW * 0.3), n = Math.max(ls.length, kl.length);
      ensure(n * 13.5 + 16);
      kl.forEach((l, i) => page.drawText(l, { x: M, y: y - i * 13.5, size: 9, font: B, color: rgb(C.ink) }));
      ls.forEach((l, i) => page.drawText(l, { x: M + CW * 0.34, y: y - i * 13.5, size: 9.5, font: F, color: rgb(C.ink) }));
      y -= (n - 1) * 13.5 + 10;
      page.drawLine({ start: { x: M, y }, end: { x: W - M, y }, thickness: 0.5, color: rgb(C.ligne) });
      y -= 16;
    }
  };
  const table = (cols: any[], rows: any[][], o: any = {}) => {
    const s = o.size || 7.6, pad = 5;
    const head = () => {
      ensure(40);
      rrect(page, M, y + 4, CW, 20, 6, { color: rgb(C.soft2) });
      let x = M; cols.forEach(c => { page.drawText(clean(c.label), { x: x + pad, y: y - 9, size: 6.6, font: B, color: rgb(C.th) }); x += c.w * CW; });
      y -= 22;
    };
    head();
    rows.forEach(row => {
      const cells = row.map((v, i) => wrap(String(v ?? '–'), cols[i].bold ? B : F, s, cols[i].w * CW - 2 * pad).slice(0, 4));
      const h = Math.max(...cells.map(c => c.length)) * (s + 2.8) + 8;
      if (y - h < 70) { newPage(); head(); }
      let x = M;
      cells.forEach((c, i) => { const col = o.color && o.color(row, i); c.forEach((l, li) => page.drawText(l, { x: x + pad, y: y - 7 - li * (s + 2.8), size: s, font: cols[i].bold || col ? B : F, color: rgb(col || C.ink) })); x += cols[i].w * CW; });
      y -= h;
      page.drawLine({ start: { x: M, y: y + 2 }, end: { x: W - M, y: y + 2 }, thickness: 0.4, color: rgb(C.ligne) });
    });
    y -= 10;
  };

  // ---------- Données ----------
  const N = sites.length, TOP = sites.slice(0, 20);
  const procs = (X.procs || []) as any[];
  const cnt = {
    terr: sites.filter(s => s.kind === 'terrain' && !s.bati).length,
    bat: sites.filter(s => s.bati).length,
    act: sites.filter(s => s.activite).length,
    dif: sites.filter(s => s.dif).length,
    fri: sites.filter(s => s.kind === 'friche').length,
    pos: sites.filter(s => s.poste_km != null && s.poste_km < 2).length
  };
  const date = new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Europe/Paris' });
  const sit = (s: any) => s.dispo === 'libre' ? 'Terrain libre' : s.kind === 'friche' ? (s.nom ? 'Friche : ' + s.nom : 'Friche recensée') : s.proc_nature ? natCourt(s.proc_nature) + (s.proc_date ? ' (' + dateF(s.proc_date) + ')' : '') : s.etat === 'C' ? 'Société radiée' + (s.fermeture ? ' (' + dateF(s.fermeture) + ')' : '') : s.armee ? 'Emprise publique (défense, gendarmerie)' : s.dispo === 'vacant' ? 'Aucune entreprise en activité à cette adresse' : '';
  const sitTone = (s: any) => s.proc_nature || s.etat === 'C' ? 'non' : s.kind === 'friche' ? 'fri' : 'ok';
  const proprio = (s: any) => s.proprio ? s.proprio + (s.forme ? ' (' + s.forme + ')' : '') : s.kind === 'friche' ? 'Non communiqué' : 'Particulier ou non communiqué';
  const comm = (s: any) => String(s.commune || '').replace(/ Arrondissement$/, '');
  const parcL = (s: any) => s.kind === 'friche' ? comm(s) : comm(s) + ' · ' + (s.section || '') + ' ' + String(s.numero || '').replace(/^0+/, '');
  const titreSite = (s: any) => s.kind === 'friche' ? (s.nom || 'Friche') + ' · ' + comm(s) : comm(s) + ' · section ' + (s.section || '') + ' n° ' + String(s.numero || '').replace(/^0+/, '');
  const zone = (s: any) => s.zone ? 'Zone ' + s.zone + (s.activite ? ' (activité)' : '') : '';
  const pk = (v: number) => String(Math.round(v * 10) / 10).replace('.', ',') + ' km';
  const poste = (s: any) => s.poste_km != null ? pk(s.poste_km) + (s.poste_tension ? ' · ' + String(s.poste_tension).split(';')[0].replace(/000$/, ' kV') : '') : '';
  const km = (v: number) => String(Math.round(v * 10) / 10).replace('.', ',') + ' km';
  const gp = (s: any) => `https://www.geoportail.gouv.fr/carte?c=${s.lon.toFixed(5)},${s.lat.toFixed(5)}&z=18&l0=ORTHOIMAGERY.ORTHOPHOTOS::GEOPORTAIL:OGC:WMTS(1)&l1=CADASTRALPARCELS.PARCELLAIRE_EXPRESS::GEOPORTAIL:OGC:WMTS(1)&permalink=yes`;
  // Coordonnées du mandataire (annuaire des mandataires judiciaires, par nom)
  const MJ = (X.mj || []) as any[];
  const norm = (t: any) => String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const mjFind = (t: string) => { const n = ' ' + norm(t) + ' '; if (n.length < 4) return null; for (const m of MJ) for (const k of (m.cles || [])) if (k && n.includes(' ' + k + ' ')) return m; return null; };
  const contacts = (m: any) => !m ? [] : [
    m.tel ? { k: 'tel', v: telF(m.tel), uri: 'tel:' + String(m.tel).replace(/[^\d+]/g, '') } : null,
    m.email ? { k: 'mail', v: String(m.email).trim(), uri: 'mailto:' + String(m.email).trim() } : null,
    m.site ? { k: 'web', v: siteF(m.site), uri: /^https?:/i.test(m.site) ? String(m.site).trim() : 'https://' + siteF(m.site) } : null
  ].filter(Boolean);

  // ---------- Images : vue aérienne, carte, vignettes ----------
  const RC = 595 / 270, RM = CW / 330, RT = 150 / 112;
  const bbCover = cadre(q.lat, q.lon, q.rayon_km * 1.08, RC), bbMap = cadre(q.lat, q.lon, q.rayon_km * 1.06, RM);
  const vign = TOP.map(s => { const d = Math.max(0.09, Math.min(0.45, Math.sqrt(Math.max(s.surface || 0, 400)) * 1.5 / 1000)); return cadre(s.lat, s.lon, d, RT); });
  const geoP = (async () => {
    const ids = TOP.filter(s => s.kind !== 'friche' && s.id).map(s => String(s.id).replace(/[^0-9A-Z]/g, ''));
    if (!ids.length) return new Map();
    const j = await getJ(WFS_IGN + '&typeNames=CADASTRALPARCELS.PARCELLAIRE_EXPRESS:parcelle&count=60&CQL_FILTER=' + encodeURIComponent('idu IN (' + ids.map(x => "'" + x + "'").join(',') + ')'), 30000);
    const m = new Map(); for (const f of (j && j.features) || []) m.set(f.properties?.idu, polysOf(f.geometry)); return m;
  })().catch(() => new Map());
  const [coverB, mapB, geo, ...vB] = await Promise.all([
    getBytes(wmsU('ORTHOIMAGERY.ORTHOPHOTOS', bbCover, 1400, Math.round(1400 / RC))),
    getBytes(wmsU('GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2', bbMap, 1300, Math.round(1300 / RM))),
    geoP,
    ...vign.map(b => getBytes(wmsU('ORTHOIMAGERY.ORTHOPHOTOS', b, 450, 336)))
  ]);
  const coverI = await img(coverB), mapI = await img(mapB), vI: any[] = [];
  for (const b of vB) vI.push(await img(b));
  // Points sur une image : projection directe dans le cadre
  const proj = (bb: number[], x0: number, yTop: number, w: number, h: number) => ({ X: (lon: number) => x0 + (lon - bb[0]) / (bb[2] - bb[0]) * w, Y: (lat: number) => yTop - (bb[3] - lat) / (bb[3] - bb[1]) * h });
  const clipBox = (p: any, x: number, yb: number, w: number, h: number, draw: () => void) => { p.pushOperators(PDFLib.pushGraphicsState(), PDFLib.rectangle(x, yb, w, h), PDFLib.clip(), PDFLib.endPath()); try { draw(); } finally { p.pushOperators(PDFLib.popGraphicsState()); } };
  const cercle = (p: any, P: any, bb: number[], h: number, lw = 1.4) => { const rr = q.rayon_km / ((bb[3] - bb[1]) * 111) * h; p.drawEllipse({ x: P.X(q.lon), y: P.Y(q.lat), xScale: rr, yScale: rr, borderColor: rgb(C.white), borderWidth: lw + 2.4, borderOpacity: 0.85 }); p.drawEllipse({ x: P.X(q.lon), y: P.Y(q.lat), xScale: rr, yScale: rr, borderColor: rgb(C.t), borderWidth: lw }); };
  const pastille = (p: any, x: number, yy: number, n: number, r = 7) => { p.drawCircle({ x, y: yy, size: r + 1.4, color: rgb(C.white) }); p.drawCircle({ x, y: yy, size: r, color: rgb(C.t) }); const s = String(n), fs = r * 1.05; p.drawText(s, { x: x - tw(s, B, fs) / 2, y: yy - fs * 0.36, size: fs, font: B, color: rgb(C.white) }); };

  // =================== COUVERTURE ===================
  {
    const p = pdf.addPage([W, H]); pages.push(p); page = p;
    logo(p, M, H - 46, 44, rgb(C.t), rgb(C.soft2));
    p.drawText('TerrenUrbanisme', { x: M + 56, y: H - 70, size: 19, font: B, color: rgb(C.ink) });
    p.drawText(clean('Le foncier des entreprises, partout en France'), { x: M + 56, y: H - 85, size: 9, font: F, color: rgb(C.muet) });
    let cy = H - 150;
    p.drawText(clean('RECHERCHE FONCIÈRE'), { x: M, y: cy, size: 10, font: B, color: rgb(C.t) });
    let TS = 40; while (TS > 26 && tw(commune, B, TS) > CW) TS -= 1;
    cy -= TS + 6;
    for (const l of wrap(commune, B, TS, CW).slice(0, 2)) { p.drawText(l, { x: M, y: cy, size: TS, font: B, color: rgb(C.ink) }); cy -= TS + 4; }
    p.drawText(clean('Rayon de ' + q.rayon_km + ' km · ' + besoinL), { x: M, y: cy + 2, size: 16, font: Md, color: rgb(C.ink) });
    cy -= 26;
    const nb0 = N ? nb(N) + (N > 1 ? ' sites disponibles' : ' site disponible') : 'Aucun site disponible';
    { const w = tw(nb0, B, 10) + 30; rrect(p, M, cy + 16, w, 24, 12, { color: rgb(C.soft2) }); p.drawCircle({ x: M + 12, y: cy + 4, size: 3.5, color: rgb(C.t) }); p.drawText(clean(nb0), { x: M + 20, y: cy, size: 10, font: B, color: rgb(C.th) }); }
    cy -= 30;
    const phH = Math.round(CW / RC);
    if (coverI) {
      p.drawRectangle({ x: M - 1, y: cy - phH - 1, width: CW + 2, height: phH + 2, color: rgb(C.ligne) });
      p.drawImage(coverI, { x: M, y: cy - phH, width: CW, height: phH });
      const P = proj(bbCover, M, cy, CW, phH);
      clipBox(p, M, cy - phH, CW, phH, () => {
        cercle(p, P, bbCover, phH, 1.8);
        sites.slice(20, 300).forEach(s => p.drawCircle({ x: P.X(s.lon), y: P.Y(s.lat), size: 1.9, color: rgb(C.white), borderColor: rgb(C.t), borderWidth: 0.8 }));
        TOP.slice().reverse().forEach((s, j) => { const i = TOP.length - 1 - j; pastille(p, P.X(s.lon), P.Y(s.lat), i + 1, 5.6); });
        p.drawCircle({ x: P.X(q.lon), y: P.Y(q.lat), size: 3, color: rgb(C.white), borderColor: rgb(C.ink), borderWidth: 1.4 });
      });
      cy -= phH + 10;
      p.drawText(clean(`Vue aérienne du secteur : cercle de ${q.rayon_km} km autour de ${commune}, sites numérotés par ordre de pertinence · © IGN`), { x: M, y: cy, size: 7.5, font: F, color: rgb(C.muet) });
      cy -= 26;
    }
    const facts = [['Établi pour', q.societe || q.nom || ''], ['Demandé par', q.nom && q.societe ? q.nom : ''], ['Recherche', besoinL], ['Surfaces minimales', [q.surface ? 'terrain ' + nb(q.surface) + ' m²' : '', q.bati ? 'bâti ' + nb(q.bati) + ' m²' : ''].filter(Boolean).join(' · ') || 'aucune'], ['Activité', q.usage || ''], ['Rapport établi le', date], ['Référence', ref]].filter(f => f[1]);
    const colW = CW / 2;
    facts.forEach((f, i) => {
      const fx = M + (i % 2) * colW, fy = cy - Math.floor(i / 2) * 36;
      p.drawLine({ start: { x: fx, y: fy + 13 }, end: { x: fx + colW - 16, y: fy + 13 }, thickness: 0.6, color: rgb(C.ligne) });
      p.drawText(clean(f[0]), { x: fx, y: fy, size: 8, font: F, color: rgb(C.muet) });
      p.drawText(cut(f[1], B, 10.5, colW - 18), { x: fx, y: fy - 14, size: 10.5, font: B, color: rgb(C.ink) });
    });
    p.drawLine({ start: { x: M, y: 96 }, end: { x: W - M, y: 96 }, thickness: 1, color: rgb(C.t) });
    const s1 = 'terrenurbanisme.com', e1 = 'contact@terrenurbanisme.com';
    p.drawText(s1, { x: M, y: 70, size: 13, font: B, color: rgb(C.t) }); linkAt(p, M, 64, tw(s1, B, 13), 18, 'https://terrenurbanisme.com');
    p.drawText(e1, { x: W - M - tw(e1, B, 13), y: 70, size: 13, font: B, color: rgb(C.t) }); linkAt(p, W - M - tw(e1, B, 13), 64, tw(e1, B, 13), 18, 'mailto:' + e1);
    p.drawText(clean('Document d\'information établi à partir de sources publiques. Il ne constitue ni une offre de vente, ni une évaluation, ni un certificat d\'urbanisme.'), { x: M, y: 40, size: 7, font: F, color: rgb(C.muet) });
  }

  // =================== 01 SYNTHÈSE ===================
  section('Synthèse');
  {
    const big = nb(N), lab = N > 1 ? 'sites disponibles' : 'site disponible';
    const phr = N
      ? `dans un rayon de ${q.rayon_km} km autour de ${commune}. Seuls les sites mobilisables sont retenus : terrains libres et sans construction, biens de sociétés en liquidation ou fermées, friches. Les sites occupés par une entreprise en activité sont écartés.`
      : `dans un rayon de ${q.rayon_km} km autour de ${commune} avec ces critères. Écrivez-nous à contact@terrenurbanisme.com : nous relançons la recherche avec un rayon plus large ou des surfaces ajustées.`;
    const ls = wrap(phr, F, 10.2, CW - 150), bh = Math.max(92, ls.length * 15 + 34);
    rrect(page, M, y, CW, bh, 14, { color: rgb(C.soft) });
    page.drawRectangle({ x: M, y: y - bh + 12, width: 4, height: bh - 24, color: rgb(C.t) });
    let fs = 46; while (fs > 26 && tw(big, B, fs) > 108) fs -= 2;
    page.drawText(big, { x: M + 22, y: y - 22 - fs * 0.78, size: fs, font: B, color: rgb(C.t) });
    wrap(lab, B, 10, 110).forEach((l, i) => page.drawText(l, { x: M + 22, y: y - 34 - fs * 0.78 - i * 12, size: 10, font: B, color: rgb(C.ink) }));
    ls.forEach((l, i) => page.drawText(l, { x: M + 138, y: y - 24 - i * 15, size: 10.2, font: F, color: rgb(C.ink) }));
    y -= bh + 14;
    const tiles: [number, string][] = ([
      [cnt.terr, 'terrains libres, sans construction'], [cnt.bat, 'bâtiments sans entreprise en activité'], [cnt.dif, 'biens de sociétés en liquidation ou fermées'],
      [cnt.fri, 'friches recensées'], [cnt.act, 'en zone d\'activité du PLU'], [procs.length, 'entreprises en procédure collective dans le secteur'], [cnt.pos, 'à moins de 2 km d\'un poste électrique']
    ] as [number, string][]).filter(t => t[0] > 0).slice(0, 6);
    const tw3 = (CW - 20) / 3;
    tiles.forEach(([v, l], i) => {
      const x = M + (i % 3) * (tw3 + 10), yt = y - Math.floor(i / 3) * 62;
      rrect(page, x, yt, tw3, 54, 12, { color: rgb(C.white), borderColor: rgb(C.ligne), borderWidth: 0.8 });
      page.drawText(nb(v), { x: x + 12, y: yt - 24, size: 19, font: B, color: rgb(C.t) });
      wrap(l, F, 7.8, tw3 - 24).slice(0, 2).forEach((ll, k) => page.drawText(ll, { x: x + 12, y: yt - 36 - k * 9.5, size: 8, font: F, color: rgb(C.muet) }));
    });
    y -= Math.ceil(tiles.length / 3) * 62 + 6;
    if (N) {
      h3('Les meilleures opportunités');
      TOP.slice(0, 3).forEach((s, i) => {
        ensure(50);
        rrect(page, M, y, CW, 44, 10, { color: rgb(C.white), borderColor: rgb(C.ligne), borderWidth: 0.8 });
        pastille(page, M + 22, y - 22, i + 1, 9);
        page.drawText(cut(titreSite(s), B, 11, CW - 200), { x: M + 42, y: y - 18, size: 11, font: B, color: rgb(C.ink) });
        const det = [s.surface ? nb(s.surface) + ' m² de terrain' : '', s.bati ? nb(s.bati) + ' m² bâtis' : '', zone(s), 'à ' + km(s.dist)].filter(Boolean).join(' · ');
        page.drawText(cut(det, F, 8.8, CW - 200), { x: M + 42, y: y - 32, size: 8.8, font: F, color: rgb(C.muet) });
        const st = cut(sit(s) || 'Disponible', B, 7.8, 140), tone = sitTone(s);
        const pw = tw(st, B, 7.8) + 14; pill(page, st, W - M - 12 - pw, y - 14, tone === 'non' ? C.nonbg : tone === 'fri' ? C.soft2 : C.okbg, tone === 'non' ? C.non : tone === 'fri' ? C.th : C.ok);
        y -= 50;
      });
    }
    h3('Vos prochaines étapes');
    const steps = [
      ['Repérez les sites', 'Carte (partie 02) et fiches détaillées (partie 03) : parcelle, surfaces, zone du PLU, situation, et un lien vers le Géoportail.'],
      ['Contactez le bon interlocuteur', 'Société en procédure : le mandataire judiciaire conduit la vente (partie 04). Terrain privé : la mairie ou un agent immobilier. Société : son siège.'],
      ['Sécurisez votre projet', 'Avant toute offre, le rapport d\'urbanisme TerrenUrbanisme de la parcelle détaille règles du PLU, risques, servitudes et réseaux.']
    ];
    steps.forEach(([t, d], i) => {
      const ls2 = wrap(d, F, 9.2, CW - 40); ensure(ls2.length * 13 + 26);
      page.drawCircle({ x: M + 11, y: y - 4, size: 11, color: rgb(C.soft2) });
      page.drawText(String(i + 1), { x: M + 11 - tw(String(i + 1), B, 10.5) / 2, y: y - 7.6, size: 10.5, font: B, color: rgb(C.th) });
      page.drawText(clean(t), { x: M + 32, y: y - 8, size: 10.5, font: B, color: rgb(C.ink) });
      ls2.forEach((l, k) => page.drawText(l, { x: M + 32, y: y - 23 - k * 13, size: 9.2, font: F, color: rgb(C.muet) }));
      y -= ls2.length * 13 + 26;
    });
  }

  // =================== 02 CARTE ===================
  if (N) {
    section('Carte des sites', `Les ${Math.min(20, N)} sites les plus pertinents sont numérotés ; les autres sites disponibles apparaissent en points clairs. Le cercle marque le rayon de ${q.rayon_km} km autour de ${commune}.`);
    const mh = Math.round(CW / RM);
    if (mapI) {
      page.drawRectangle({ x: M - 1, y: y - mh - 1, width: CW + 2, height: mh + 2, color: rgb(C.ligne) });
      page.drawImage(mapI, { x: M, y: y - mh, width: CW, height: mh });
      const P = proj(bbMap, M, y, CW, mh);
      clipBox(page, M, y - mh, CW, mh, () => {
        cercle(page, P, bbMap, mh, 1.6);
        sites.slice(20, 400).forEach(s => page.drawCircle({ x: P.X(s.lon), y: P.Y(s.lat), size: 2.2, color: rgb(C.white), borderColor: rgb(C.t), borderWidth: 0.9 }));
        TOP.slice().reverse().forEach((s, j) => pastille(page, P.X(s.lon), P.Y(s.lat), TOP.length - j, 6.8));
      });
      y -= mh + 12;
      page.drawText(clean('Fond de carte © IGN · Plan IGN'), { x: M, y, size: 7.5, font: F, color: rgb(C.muet) });
      y -= 20;
    }
    // Légende : les 20 premiers sur deux colonnes
    const cw2 = (CW - 16) / 2;
    TOP.forEach((s, i) => {
      const col = i < Math.ceil(TOP.length / 2) ? 0 : 1, r = col ? i - Math.ceil(TOP.length / 2) : i, x = M + col * (cw2 + 16), yy = y - r * 19;
      if (yy < 76) return;
      pastille(page, x + 7, yy - 3, i + 1, 6.2);
      const t1 = cut(parcL(s), B, 8.4, cw2 * 0.5), t2 = cut([s.surface ? nb(s.surface) + ' m²' : '', s.bati ? nb(s.bati) + ' m² bâtis' : '', km(s.dist)].filter(Boolean).join(' · '), F, 8.2, cw2 - 22 - tw(t1, B, 8.4) - 8);
      page.drawText(t1, { x: x + 19, y: yy - 6, size: 8.4, font: B, color: rgb(C.ink) });
      page.drawText(t2, { x: x + 19 + tw(t1, B, 8.4) + 6, y: yy - 6, size: 8.2, font: F, color: rgb(C.muet) });
    });
    y -= Math.ceil(TOP.length / 2) * 19 + 8;
  }

  // =================== 03 FICHES ===================
  if (N) {
    section('Les sites en détail', 'Les vingt sites les plus pertinents, classés selon votre recherche : zone d\'activité du PLU, société en difficulté, friche, proximité d\'un poste électrique et distance. Cliquez sur « Voir sur le Géoportail » pour ouvrir la vue aérienne et le cadastre.');
    const TW = 150, TH = 112;
    TOP.forEach((s, i) => {
      const xr = M + TW + 16, wr = CW - TW - 16;
      const m = s.mandataire ? mjFind(s.mandataire) : null, ct = contacts(m);
      const lignes: [string, string, any][] = [
        ['Situation', sit(s) || 'Disponible', sitTone(s) === 'non' ? C.non : C.ink],
        ['Propriétaire', proprio(s), C.ink],
        ...(s.mandataire ? [['Mandataire', s.mandataire, C.ink]] as any : []),
        ...(poste(s) ? [['Poste électrique', poste(s), C.ink]] as any : [])
      ];
      const lh = lignes.map(([k, v]) => wrap(v, F, 8.8, wr - 92).slice(0, 3).length);
      const chH = ct.length ? chips(page, 0, 0, wr, ct, { measure: true }) + 8 : 0;
      const h = Math.max(TH, 24 + 22 + lh.reduce((a, b) => a + b * 12 + 3, 0) + chH + 18) + 16;
      ensure(h + 4);
      const y0 = y;
      // Vignette
      const im = vI[i];
      page.drawRectangle({ x: M - 0.6, y: y0 - TH - 0.6, width: TW + 1.2, height: TH + 1.2, color: rgb(C.ligne) });
      if (im) {
        page.drawImage(im, { x: M, y: y0 - TH, width: TW, height: TH });
        const bb = vign[i], P = proj(bb, M, y0, TW, TH), ps = geo.get(String(s.id || '').replace(/[^0-9A-Z]/g, ''));
        clipBox(page, M, y0 - TH, TW, TH, () => {
          if (ps && ps.length) for (const poly of ps) {
            const path = 'M' + poly[0].map((c: number[]) => (P.X(c[0]) - M).toFixed(1) + ' ' + (y0 - P.Y(c[1])).toFixed(1)).join('L') + 'Z';
            page.drawSvgPath(path, { x: M, y: y0, borderColor: rgb(C.white), borderWidth: 3.4, borderOpacity: 0.9 });
            page.drawSvgPath(path, { x: M, y: y0, borderColor: rgb(C.yel), borderWidth: 1.6 });
          } else { page.drawCircle({ x: P.X(s.lon), y: P.Y(s.lat), size: 5, color: rgb(C.yel), borderColor: rgb(C.white), borderWidth: 1.6 }); }
        });
      } else rrect(page, M, y0, TW, TH, 0, { color: rgb(C.soft) });
      pastille(page, M + 14, y0 - 14, i + 1, 8.5);
      // Texte
      page.drawText(cut(titreSite(s), B, 12, wr), { x: xr, y: y0 - 12, size: 12, font: B, color: rgb(C.ink) });
      const tone = sitTone(s);
      const ph = pills(page, [
        [s.surface ? nb(s.surface) + ' m² de terrain' : '', C.soft2, C.th], [s.bati ? nb(s.bati) + ' m² bâtis' : '', C.soft2, C.th],
        [zone(s), s.activite ? C.okbg : C.soft, s.activite ? C.ok : C.ink], ['à ' + km(s.dist), C.soft, C.ink]
      ], xr, y0 - 20, wr);
      let yy = y0 - 20 - ph - 14;
      lignes.forEach(([k, v, col], li) => {
        page.drawText(clean(k), { x: xr, y: yy, size: 8.2, font: B, color: rgb(C.muet) });
        wrap(v, li === 0 && tone === 'non' ? B : F, 8.8, wr - 92).slice(0, 3).forEach((l, j) => page.drawText(l, { x: xr + 88, y: yy - j * 12, size: 8.8, font: li === 0 && tone === 'non' ? B : F, color: rgb(col) }));
        yy -= lh[li] * 12 + 3;
      });
      if (ct.length) { yy -= 2; chips(page, xr, yy + 8, wr, ct); yy -= chH; }
      const lk = 'Voir sur le Géoportail';
      page.drawText(lk, { x: xr, y: yy - 6, size: 8.6, font: B, color: rgb(C.t) });
      page.drawLine({ start: { x: xr, y: yy - 8 }, end: { x: xr + tw(lk, B, 8.6), y: yy - 8 }, thickness: 0.6, color: rgb(C.t) });
      linkAt(page, xr, yy - 10, tw(lk, B, 8.6), 13, gp(s));
      if (s.proc_url) { const l2 = 'Annonce au BODACC', x2 = xr + tw(lk, B, 8.6) + 18; page.drawText(l2, { x: x2, y: yy - 6, size: 8.6, font: B, color: rgb(C.t) }); page.drawLine({ start: { x: x2, y: yy - 8 }, end: { x: x2 + tw(l2, B, 8.6), y: yy - 8 }, thickness: 0.6, color: rgb(C.t) }); linkAt(page, x2, yy - 10, tw(l2, B, 8.6), 13, s.proc_url); }
      y = y0 - h + 4;
      if (i < TOP.length - 1) page.drawLine({ start: { x: M, y: y + 8 }, end: { x: W - M, y: y + 8 }, thickness: 0.6, color: rgb(C.ligne) });
      y -= 8;
    });
  }

  // Liste complète (suite de la partie 03)
  const cols = [
    { label: 'N°', w: 0.05, bold: true }, { label: 'COMMUNE · PARCELLE', w: 0.2, bold: true }, { label: 'TERRAIN', w: 0.09 }, { label: 'BÂTI', w: 0.08 },
    { label: 'ZONE PLU', w: 0.1 }, { label: 'PROPRIÉTAIRE', w: 0.18 }, { label: 'SITUATION', w: 0.15 }, { label: 'POSTE ÉLEC.', w: 0.09 }, { label: 'DIST.', w: 0.06 }
  ];
  if (N > 20) {
    const L = Math.min(N, 400);
    newPage(); h3('Les autres sites disponibles');
    text(`Sites ${21} à ${L}${N > L ? ' (sur ' + nb(N) + ' au total ; les ' + nb(N - L) + ' suivants, plus éloignés ou moins adaptés, sont disponibles sur demande)' : ''}. En rouge : société en procédure collective ou radiée.`, { size: 9, color: C.muet, after: 8 });
    table(cols, sites.slice(20, L).map((s, i) => [String(i + 21), parcL(s), s.surface ? nb(s.surface) + ' m²' : '–', s.bati ? nb(s.bati) + ' m²' : '–', s.zone ? s.zone + (s.activite ? ' (act.)' : '') : '–', proprio(s), sit(s) || '–', s.poste_km != null ? pk(s.poste_km) : '–', km(s.dist)]), { color: (r: any[], i: number) => i === 6 && /liquidation|redressement|sauvegarde|radi|proc[ée]dure|cession/i.test(String(r[6])) ? C.non : null });
  }

  // =================== 04 PROCÉDURES COLLECTIVES ===================
  if (procs.length) {
    section('Entreprises en procédure collective dans votre secteur', `${nb(procs.length)} entreprise${procs.length > 1 ? 's' : ''} du secteur ${procs.length > 1 ? 'ont' : 'a'} fait l'objet, depuis douze mois, d'un redressement, d'une liquidation ou d'un plan de cession (BODACC, consulté le ${date}).`);
    note('Pourquoi c\'est utile : locaux, hangars, terrains, matériel ou bail commercial de ces entreprises peuvent être cédés, souvent rapidement et en dessous du marché. La vente est conduite par le mandataire ou le liquidateur judiciaire désigné par le tribunal : contactez-le en citant le nom de la société et l\'actif qui vous intéresse.' + (X.maj ? ` ${nb(X.maj)} des sites de ce rapport appartiennent à l'une de ces entreprises.` : ''));
    const P = procs.slice(0, 60);
    for (const p0 of P) {
      const m = p0.mandataire ? mjFind(p0.mandataire) : null, ct = contacts(m);
      const nat = p0.nature + (p0.date ? ' · ' + dateF(p0.date) : ''), liq = /liquidation/i.test(p0.nature);
      const pwid = tw(clean(nat), B, 7.8) + 14;
      const nm = wrap(p0.nom || 'Société', B, 11, CW - pwid - 40).slice(0, 2);
      const sub = [p0.activite, [p0.cp, p0.ville].filter(Boolean).join(' '), p0.siren ? 'SIREN ' + p0.siren : ''].filter(Boolean).join(' · ');
      const sl = wrap(sub, F, 8.6, CW - 28).slice(0, 2);
      const ml = p0.mandataire ? wrap(p0.mandataire, F, 8.6, CW - 120).slice(0, 4) : wrap('Mandataire non précisé dans l\'annonce : consultez l\'annonce BODACC ou le greffe du tribunal de commerce.', F, 8.6, CW - 120);
      const chH = ct.length ? chips(page, 0, 0, CW - 28, ct, { measure: true }) + 8 : 0;
      const h = 16 + nm.length * 14 + sl.length * 12 + 8 + ml.length * 12 + chH + 26;
      ensure(h + 8);
      rrect(page, M, y, CW, h, 12, { color: rgb(C.white), borderColor: rgb(C.ligne), borderWidth: 0.8 });
      if (liq) page.drawRectangle({ x: M, y: y - h + 12, width: 3, height: h - 24, color: rgb(C.non) });
      let yy = y - 22;
      nm.forEach((l, i) => page.drawText(l, { x: M + 14, y: yy - i * 14, size: 11, font: B, color: rgb(C.ink) }));
      pill(page, nat, W - M - 12 - pwid, y - 13, liq ? C.nonbg : C.soft2, liq ? C.non : C.th);
      yy -= nm.length * 14;
      sl.forEach((l, i) => page.drawText(l, { x: M + 14, y: yy - i * 12 + 2, size: 8.6, font: F, color: rgb(C.muet) }));
      yy -= sl.length * 12 + 8;
      page.drawText(clean(p0.mandataire ? 'Mandataire' : 'Interlocuteur'), { x: M + 14, y: yy, size: 8.2, font: B, color: rgb(C.t) });
      ml.forEach((l, i) => page.drawText(l, { x: M + 106, y: yy - i * 12, size: 8.6, font: F, color: rgb(C.ink) }));
      yy -= ml.length * 12;
      if (ct.length) { chips(page, M + 14, yy + 2, CW - 28, ct); yy -= chH; }
      if (p0.url) { const l2 = 'Annonce au BODACC'; page.drawText(l2, { x: M + 14, y: yy - 6, size: 8.4, font: B, color: rgb(C.t) }); page.drawLine({ start: { x: M + 14, y: yy - 8 }, end: { x: M + 14 + tw(l2, B, 8.4), y: yy - 8 }, thickness: 0.6, color: rgb(C.t) }); linkAt(page, M + 14, yy - 10, tw(l2, B, 8.4), 13, p0.url); }
      y -= h + 8;
    }
    if (procs.length > 60) text(`Les ${nb(procs.length - 60)} procédures suivantes, plus anciennes, sont disponibles sur demande.`, { size: 8.5, color: C.muet });
  }

  // Friches
  const frs = sites.filter(s => s.kind === 'friche');
  if (frs.length) {
    newPage(); h3('Friches recensées');
    text('Sites de l\'inventaire national des friches (Cartofriches, Cerema). Leur reconversion bénéficie souvent d\'aides publiques : fonds friches, établissements publics fonciers.', { size: 9.2, color: C.muet, after: 8 });
    table([{ label: 'SITE', w: 0.26, bold: true }, { label: 'COMMUNE', w: 0.15 }, { label: 'TYPE', w: 0.14 }, { label: 'STATUT', w: 0.15 }, { label: 'SURFACE', w: 0.1 }, { label: 'ANCIENNE ACTIVITÉ', w: 0.2 }],
      frs.slice(0, 80).map(s => [s.nom || 'Friche', comm(s), s.type || '–', s.statut || '–', s.surface ? nb(s.surface) + ' m²' : '–', s.ancienne_activite || '–']));
  }

  // =================== ANNONCES ===================
  if ((X.links && X.links.length) || (X.ench && X.ench.length)) {
    section('Annonces et ventes en cours', `Les biens mis en vente ces derniers jours n'apparaissent pas encore dans les fichiers publics. Chaque carte ouvre directement les annonces du jour correspondant à votre recherche autour de ${commune}.`);
    const carte = (t: string, d: string, u: string) => {
      const ld = wrap(d, F, 8.6, CW - 110), h = 30 + ld.length * 11.5; ensure(h + 8);
      rrect(page, M, y, CW, h, 12, { color: rgb(C.white), borderColor: rgb(C.ligne), borderWidth: 0.8 });
      page.drawText(cut(t, B, 10.5, CW - 110), { x: M + 14, y: y - 18, size: 10.5, font: B, color: rgb(C.ink) });
      ld.forEach((l, i) => page.drawText(l, { x: M + 14, y: y - 32 - i * 11.5, size: 8.6, font: F, color: rgb(C.muet) }));
      const bw = 64; rrect(page, W - M - 14 - bw, y - h / 2 + 11, bw, 22, 11, { color: rgb(C.t) });
      page.drawText('Ouvrir', { x: W - M - 14 - bw / 2 - tw('Ouvrir', B, 9) / 2, y: y - h / 2 - 3, size: 9, font: B, color: rgb(C.white) });
      linkAt(page, M, y - h, CW, h, u); y -= h + 8;
    };
    if (X.links && X.links.length) { h3('Annonces d\'immobilier d\'entreprise'); for (const [t, d, u] of X.links) carte(t, d, u); y -= 10; }
    if (X.ench && X.ench.length) { h3('Ventes aux enchères judiciaires'); text('Biens vendus sur décision de justice : la visite est organisée avant l\'audience et l\'enchère se porte par l\'intermédiaire d\'un avocat.', { size: 9, color: C.muet, after: 8 }); for (const [t, d, u] of X.ench) carte(t, d, u); }
  }

  // =================== RACCORDEMENT ===================
  section('Raccordement électrique', 'Chaque fiche indique la distance au poste électrique le plus proche recensé. Plus le site en est proche, plus le raccordement est simple, rapide et économique.');
  const kva = q.puissance_kva || 0;
  kv([
    ['Jusqu\'à 36 kVA', 'Basse tension (bureaux, petit atelier) : quelques semaines à quelques mois.'],
    ['De 36 à 250 kVA', 'Basse tension à puissance surveillée (entrepôt, atelier, commerce) : une extension du réseau peut être nécessaire.'],
    ['Au-delà de 250 kVA', 'Moyenne tension (HTA) avec poste de livraison privé sur le terrain : étude du gestionnaire de réseau, 6 à 18 mois selon les travaux.'],
    ['Plusieurs mégawatts', 'Data center, électro-intensif : raccordement direct à un poste source, à étudier très en amont avec RTE et le gestionnaire de réseau.']
  ]);
  if (kva) note(`Puissance souhaitée : ${nb(kva)} kVA. ${kva > 250 ? 'Privilégiez les sites à moins de 2 km d\'un poste électrique et demandez une étude de raccordement avant de vous engager.' : 'Cette puissance se raccorde en général sans poste dédié ; vérifiez la capacité du réseau existant auprès du gestionnaire.'} Le gestionnaire de réseau est Enedis sur la plus grande partie du territoire, EDF SEI en Corse et dans les départements d'outre-mer.`);

  // =================== MÉTHODE ===================
  section('Méthode et sources');
  kv([
    ['Terrains', 'Parcelles du cadastre d\'au moins 1 000 m² situées en zone urbaine ou à urbaniser d\'un document d\'urbanisme (Géoportail de l\'urbanisme). Les zones d\'activité sont repérées par leur intitulé et leur description.'],
    ['Bâtiments', 'Bâtiments industriels, agricoles et commerciaux d\'au moins 150 m² d\'emprise (BD TOPO, IGN), rattachés à leur parcelle.'],
    ['Disponibilité', 'Un site est retenu s\'il est disponible : terrain sans construction et sans entreprise en activité déclarée (répertoire Sirene de l\'INSEE), bien d\'une société en procédure collective ou radiée (BODACC), ou friche (Cartofriches). Les sites occupés par une entreprise en activité, y compris par leur propriétaire, sont écartés.'],
    ...(q._verif ? [['Contrôle des terrains', 'Chaque terrain proposé a été vérifié un par un sur le plan cadastral et la BD TOPO (IGN) : aucune construction de plus de 50 m² sur la parcelle. ' + (q._verif.bati ? nb(q._verif.bati) + ' parcelle' + (q._verif.bati > 1 ? 's déjà bâties ont été écartées.' : ' déjà bâtie a été écartée.') : '')]] : []),
    ['Propriétaires', 'Fichier des parcelles des personnes morales (DGFiP). Seules les sociétés, collectivités et organismes sont nommés ; les particuliers ne le sont jamais.'],
    ['Situation des sociétés', 'Procédures collectives et radiations publiées au BODACC depuis 2017 ; procédures des douze derniers mois interrogées le jour du rapport.'],
    ['Mandataires', 'Nom tiré du jugement publié au BODACC ; coordonnées issues des listes officielles des mandataires judiciaires lorsqu\'elles sont disponibles.'],
    ['Friches', 'Inventaire national Cartofriches (Cerema).'],
    ['Électricité', 'Postes électriques recensés dans OpenStreetMap.'],
    ['Images', 'Vues aériennes et plan © IGN, Géoplateforme.'],
    ['Annonces', 'Liens vers les recherches des portails d\'annonces et des sites de ventes aux enchères : les offres affichées sont celles du jour où vous cliquez.']
  ]);
  note('Ce rapport est établi à partir de sources publiques à la date indiquée. Il ne constitue ni une offre de vente, ni une évaluation, ni un certificat d\'urbanisme : la disponibilité d\'un site, son prix et ses règles de construction sont à confirmer auprès du propriétaire, de la mairie et, pour une société en procédure, du mandataire judiciaire.');

  // =================== QUATRIÈME DE COUVERTURE ===================
  {
    const p = pdf.addPage([W, H]), Wh = rgb(C.white), Wm = PDFLib.rgb(0.98, 0.9, 0.86);
    p.drawRectangle({ x: 0, y: 0, width: W, height: H, color: rgb(C.t) });
    const ls = 92; logo(p, (W - ls) / 2, H - 150, ls, Wh, rgb(C.th));
    const ctr = (s: string, yy: number, size: number, font: any, col: any) => { const l = clean(s); p.drawText(l, { x: (W - tw(l, font, size)) / 2, y: yy, size, font, color: col }); };
    ctr('TerrenUrbanisme', H - 280, 24, B, Wh);
    ctr('Merci de votre confiance', H - 330, 30, B, Wh);
    let yy = H - 370;
    wrap('Ce rapport a été établi à partir des sources publiques officielles pour vous aider à trouver le bon site, plus vite. Pour affiner la recherche ou étudier un site en particulier, nous restons à votre disposition.', F, 12, CW - 60).forEach(l => { ctr(l, yy, 12, F, Wm); yy -= 18; });
    yy -= 28;
    const bx = M + 10, bw = CW - 20;
    const lines = wrap('Le rapport d\'urbanisme TerrenUrbanisme d\'une parcelle réunit en un document les règles du PLU, les risques naturels et technologiques, les servitudes, les réseaux et les prix des ventes du secteur.', F, 11, bw - 48), bh = 62 + lines.length * 16 + 34;
    p.drawRectangle({ x: bx, y: yy - bh, width: bw, height: bh, color: rgb(C.th), borderColor: PDFLib.rgb(0.85, 0.6, 0.52), borderWidth: 0.8 });
    let by = yy - 34; ctr('Un site vous intéresse ?', by, 16, B, Wh); by -= 28;
    lines.forEach(l => { ctr(l, by, 11, F, Wm); by -= 16; });
    by -= 8; ctr('Commandez-le sur terrenurbanisme.com', by, 11.5, B, Wh);
    ctr('terrenurbanisme.com', 92, 15, B, Wh); linkAt(p, (W - tw('terrenurbanisme.com', B, 15)) / 2, 86, tw('terrenurbanisme.com', B, 15), 20, 'https://terrenurbanisme.com');
    ctr('contact@terrenurbanisme.com', 70, 11, F, Wm); linkAt(p, (W - tw('contact@terrenurbanisme.com', F, 11)) / 2, 66, tw('contact@terrenurbanisme.com', F, 11), 15, 'mailto:contact@terrenurbanisme.com');
  }

  // Pieds de page (hors couverture et quatrième)
  const total = pages.length + 1;
  pages.forEach((p, i) => {
    if (i === 0) return;
    p.drawLine({ start: { x: M, y: 46 }, end: { x: W - M, y: 46 }, thickness: 0.5, color: rgb(C.ligne) });
    const t = clean('terrenurbanisme.com · rapport ' + ref);
    p.drawText(t, { x: M, y: 32, size: 7.5, font: F, color: rgb(C.muet) });
    const pt = (i + 1) + ' / ' + total;
    p.drawText(pt, { x: W - M - tw(pt, B, 7.5), y: 32, size: 7.5, font: B, color: rgb(C.muet) });
  });
  return await pdf.save({ useObjectStreams: false });
}
