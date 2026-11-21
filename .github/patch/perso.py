# Version client personnalisée par l'agence : rubriques retirées, page « Recommandation de l'agence » (prix, commentaire, photos),
# client destinataire sur la couverture. Les données du rapport sont mises en cache à la génération pour reconstruire le PDF sans tout recalculer.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:80]))
    s = s.replace(old, new)

# 1. Suivi des chapitres et pages (pour retirer des rubriques)
rep("let page, y, CHN = 0, CUR = ''; const pages = []; const toc = [];",
    "let page, y, CHN = 0, CUR = '', CURT = ''; let pages = []; let toc = [];\n  const PERSO = d.perso || null, EXC = (PERSO && PERSO.exclure) || [], SANS = (PERSO && PERSO.sans) || [];")
rep("function newPage() { page = pdf.addPage([W, H]); pages.push(page); header(page); y = H - 92; return page; }",
    "function newPage() { page = pdf.addPage([W, H]); page.__ch = CURT; pages.push(page); header(page); y = H - 92; return page; }")
rep("""  function chapter(num, title, sub) {
    CUR = String(num).padStart(2, '0') + ' · ' + title;
    newPage();
    toc.push({ num, title, page: pages.length, about: ABOUT[title] || '' });""",
"""  function chapter(num, title, sub) {
    CURT = title;
    if (EXC.includes(title)) CHN--; // rubrique retirée par l'agence : la numérotation des suivantes reste continue
    CUR = String(num).padStart(2, '0') + ' · ' + title;
    newPage();
    toc.push({ num, title, page: pages.length, about: ABOUT[title] || '', _p: page });""")
# Sommaire de la synthèse et des rubriques
rep("""    'Avertissement et sources': 'La portée de ce rapport et la liste des sources publiques consultées.'
  };""", """    'Avertissement et sources': 'La portée de ce rapport et la liste des sources publiques consultées.',
    'Recommandation de l\\'agence': 'L\\'avis de valeur de votre conseiller : son prix recommandé, son commentaire et les photos du bien.'
  };""")
rep("""      'Avertissement et sources': 'La portée de ce rapport et les sources publiques consultées.',""", """      'Avertissement et sources': 'La portée de ce rapport et les sources publiques consultées.',
      'Recommandation de l\\'agence': 'Le prix recommandé par votre conseiller, son commentaire et les photos du bien.',""")

# 2. Couverture : client destinataire
rep("""  const facts = [['Référence cadastrale', R.idu], ['Surface cadastrale', fmt(R.contenance) + ' m²'], ['Rapport établi le', d.date], ['Référence du rapport', d.orderId]];""",
"""  const CLI = PERSO && PERSO.client ? [PERSO.client.civ, PERSO.client.prenom, PERSO.client.nom].filter(Boolean).join(' ').trim() : '';
  const facts = CLI ? [['À l\\'attention de', CLI], ['Référence cadastrale', R.idu], ['Surface cadastrale', fmt(R.contenance) + ' m²'], ['Rapport établi le', d.date]]
    : [['Référence cadastrale', R.idu], ['Surface cadastrale', fmt(R.contenance) + ' m²'], ['Rapport établi le', d.date], ['Référence du rapport', d.orderId]];""")

# 3. Espèces protégées : retirables
rep("""  // Espèces protégées observées autour du terrain
  {""", """  // Espèces protégées observées autour du terrain (retirables par l'agence)
  if (!SANS.includes('especes')) {""")

# 4. Page « Recommandation de l'agence », juste après la valeur du terrain
rep("""  chapter(++CHN, 'Environnement et marché immobilier',""", """  if (PERSO && PERSO.reco && (PERSO.reco.conseille || PERSO.reco.bas || PERSO.reco.haut || PERSO.reco.commentaire || (PERSO.photos && PERSO.photos.length))) {
    const RC = PERSO.reco, eurs = v => { const n = Number(String(v || '').replace(/[^0-9]/g, '')); return n ? fmt(n) + ' €' : ''; };
    chapter(++CHN, 'Recommandation de l\\'agence', (MQ && MQ.nom ? MQ.nom : 'Votre conseiller') + (CLI ? ' · pour ' + CLI : ''));
    const cons = eurs(RC.conseille), bas = eurs(RC.bas), haut = eurs(RC.haut);
    if (cons || bas || haut) {
      h3('Notre avis de valeur');
      if (cons) {
        ensure(84);
        page.drawRectangle({ x: M, y: y - 72, width: CW, height: 72, color: C.cream });
        page.drawRectangle({ x: M, y: y - 72, width: 4, height: 72, color: C.t });
        page.drawText(clean('PRIX RECOMMANDÉ PAR L\\'AGENCE'), { x: M + 20, y: y - 24, size: 8.5, font: B, color: C.t });
        page.drawText(clean(cons), { x: M + 20, y: y - 56, size: 26, font: B, color: C.ink });
        if (bas && haut) { const fr = clean('Fourchette : ' + bas + ' à ' + haut); page.drawText(fr, { x: W - M - 20 - tw(fr, Md, 11), y: y - 50, size: 11, font: Md, color: C.muet }); }
        y -= 90;
      } else kvn([['Fourchette basse', bas], ['Fourchette haute', haut]], { lw: 0.36 });
      text('Ce prix est l\\'avis de votre conseiller, établi à partir de sa connaissance du marché local, des caractéristiques du bien et des ventes récentes. Il complète la fourchette calculée à partir des ventes publiées présentée au chapitre précédent.', { size: 9, color: C.muet });
    }
    if (RC.commentaire) { h3('Le mot de votre conseiller'); String(RC.commentaire).split(/\\n+/).filter(Boolean).forEach(par => text(par, { size: 10 })); }
    const PH = (PERSO.photos || []).filter(x => x && x.bytes);
    if (PH.length) {
      h3('Photos du bien');
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
      }
    }
  }
  chapter(++CHN, 'Environnement et marché immobilier',""")

# 5. Retrait des rubriques décochées avant le sommaire
rep("""  // Sommaire détaillé (page 2)
  {""", """  // Rubriques retirées par l'agence : pages supprimées, sommaire recalculé
  if (EXC.length) {
    const rm = pages.filter(pg => EXC.includes(pg.__ch));
    for (const pg of rm) { const i = pdf.getPages().indexOf(pg); if (i >= 0) pdf.removePage(i); }
    pages = pages.filter(pg => !rm.includes(pg));
    toc = toc.filter(t => !EXC.includes(t.title));
    toc.forEach(t => { if (t._p) t.page = pdf.getPages().indexOf(t._p) + 1; else t.page -= rm.length; });
  }
  // Sommaire détaillé (page 2)
  {""")

# 6. Mise en cache des données du rapport (pour la version client)
rep("""    const { d, pdf } = await makeReport(m, { orderRef, email, leger: !!leger, marque: marqueV || undefined });
    const path = `${dossierDir(m.user_id, origine)}/${sessionId}.pdf`;""", """    const { d, pdf } = await makeReport(m, { orderRef, email, leger: !!leger, marque: marqueV || undefined });
    const path = `${dossierDir(m.user_id, origine)}/${sessionId}.pdf`;
    if (m.user_id) { try { await cacheD(sessionId, d); } catch (e) { console.warn('cache données', String(e && e.message || e).slice(0, 160)); } }""")

# 7. Fonctions de cache et action « personnaliser »
rep("""// ---------- Génération d'un rapport avec un crédit ----------
async function handleUserPost(req) {""", """// ---------- Version client personnalisée (agences) ----------
const SERK = (k, v) => v instanceof Uint8Array ? { __u8: b64(v) } : v;
const DESK = (k, v) => v && typeof v === 'object' && typeof v.__u8 === 'string' ? Uint8Array.from(atob(v.__u8), c => c.charCodeAt(0)) : v;
async function gz(bytes, dir) { const cs = dir ? new CompressionStream('gzip') : new DecompressionStream('gzip'); return new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(cs)).arrayBuffer()); }
async function cacheD(sessionId, d) {
  const { perso, ...rest } = d;
  const raw = new TextEncoder().encode(JSON.stringify(rest, SERK));
  const { error } = await admin.storage.from('dossiers').upload('cache/d/' + sessionId + '.json.gz', await gz(raw, true), { contentType: 'application/gzip', upsert: true });
  if (error) throw error;
}
async function loadD(sessionId) {
  const { data } = await admin.storage.from('dossiers').download('cache/d/' + sessionId + '.json.gz');
  if (!data) return null;
  return JSON.parse(new TextDecoder().decode(await gz(new Uint8Array(await data.arrayBuffer()), false)), DESK);
}
const CHAP_PERSO = ['Identification de la parcelle', 'Règles d\\'urbanisme applicables', 'Ce que vous pouvez construire', 'Règles propres à la Corse', 'Loi Littoral et loi Montagne', 'Risques naturels et technologiques', 'Le terrain : accès, relief et réseaux', 'Valeur de marché', 'Conditions de vente du terrain', 'Environnement et marché immobilier', 'Historique du site', 'Opportunités autour du terrain', 'Votre projet, étape par étape', 'État des risques (ERP) pré-rempli', 'Professionnels recommandés'];
async function personnaliser(user, b) {
  const { data: dos } = await admin.from('dossiers').select('id, user_id, stripe_session_id, commune, section, numero, pdf_path, origine').eq('id', String(b.id || '')).maybeSingle();
  if (!dos || dos.user_id !== user.id) return jres({ error: 'dossier' }, 404);
  const d = await loadD(dos.stripe_session_id);
  if (!d) return jres({ error: 'ancien' }, 409);
  const t = v => String(v == null ? '' : v).replace(/[<>]/g, '').trim();
  const exclure = (Array.isArray(b.exclure) ? b.exclure : []).map(String).filter(x => CHAP_PERSO.includes(x));
  const sans = (Array.isArray(b.sans) ? b.sans : []).map(String).filter(x => ['especes'].includes(x));
  const rc = b.reco || {}, cl = b.client || {};
  const photos = [];
  for (const ph of (Array.isArray(b.photos) ? b.photos : []).slice(0, 8)) {
    const path = String(ph || '');
    if (!path.startsWith(user.id + '/')) continue;
    const { data: blob } = await admin.storage.from('perso').download(path);
    if (!blob) continue;
    const bytes = new Uint8Array(await blob.arrayBuffer());
    const png = bytes[0] === 0x89 && bytes[1] === 0x50, jpg = bytes[0] === 0xFF && bytes[1] === 0xD8;
    if ((png || jpg) && bytes.length < 6 * 1024 * 1024) photos.push({ bytes, png });
  }
  d.perso = { exclure, sans, photos,
    reco: { bas: t(rc.bas).slice(0, 20), haut: t(rc.haut).slice(0, 20), conseille: t(rc.conseille).slice(0, 20), commentaire: t(rc.commentaire).slice(0, 3000) },
    client: { civ: t(cl.civ).slice(0, 10), prenom: t(cl.prenom).slice(0, 60), nom: t(cl.nom).slice(0, 60), email: t(cl.email).slice(0, 120), tel: t(cl.tel).slice(0, 30) } };
  try { d.marque = await loadMarque(user.id) || d.marque; } catch (e) {}
  const fonts = await loadFonts();
  const pdf = await buildReport(PDFLib, d, { fonts, fontkit, annex: null });
  const path = `${dos.user_id}/client/${dos.stripe_session_id}.pdf`;
  const { error: ue } = await admin.storage.from('dossiers').upload(path, pdf, { contentType: 'application/pdf', upsert: true });
  if (ue) { console.error('version client', ue); return jres({ error: 'stockage' }, 500); }
  await admin.from('dossiers').update({ perso: { exclure, sans, reco: d.perso.reco, client: d.perso.client, photos: (b.photos || []).slice(0, 8), at: new Date().toISOString() } }).eq('id', dos.id);
  const nom = [d.perso.client.prenom, d.perso.client.nom].filter(Boolean).join('-') || 'client';
  const file = `Rapport-${d.ref.commune}-${d.ref.section}-${d.ref.numero}-${nom}.pdf`.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/[^A-Za-z0-9.-]+/g, '-');
  const { data: su } = await admin.storage.from('dossiers').createSignedUrl(path, 7 * 24 * 3600, { download: file });
  const { data: sv } = await admin.storage.from('dossiers').createSignedUrl(path, 7 * 24 * 3600);
  return jres({ ok: true, url: su && su.signedUrl, view: sv && sv.signedUrl, pages: (pdf.length / 1024 / 1024).toFixed(1) });
}
// ---------- Génération d'un rapport avec un crédit ----------
async function handleUserPost(req) {""")
rep("""  if (b.action === 'relance') { const n = await relancerBloques(""", """  if (b.action === 'personnaliser') return await personnaliser(u.user, b);
  if (b.action === 'apercu_dossier') {
    const { data: dos } = await admin.from('dossiers').select('id, user_id, stripe_session_id, pdf_path, perso').eq('id', String(b.id || '')).maybeSingle();
    if (!dos || dos.user_id !== u.user.id || !dos.pdf_path) return jres({ error: 'dossier' }, 404);
    const { data: sv } = await admin.storage.from('dossiers').createSignedUrl(dos.pdf_path, 3600);
    const { data: ex } = await admin.storage.from('dossiers').list('cache/d', { search: dos.stripe_session_id });
    return jres({ view: sv && sv.signedUrl, perso: dos.perso || null, pret: !!(ex && ex.length), chapitres: CHAP_PERSO });
  }
  if (b.action === 'relance') { const n = await relancerBloques(""")
# Dernière page : plus d'abonnement
s = s.replace("Abonnements à partir de 29 € par mois, votre logo sur les rapports, offre communale pour les mairies et partenariats sur mesure.", "Crédits professionnels sans abonnement dès 3,50 € le rapport, votre logo sur les rapports, offre communale pour les mairies et partenariats sur mesure.")
open(p, 'w', encoding='utf-8').write(s); print('patch perso appliqué')
