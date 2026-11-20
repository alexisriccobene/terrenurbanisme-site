# Version client : fabrication confiée à GitHub (pas de limite de calcul), suivi par le back-office
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:80]))
    s = s.replace(old, new)
# 1. personnaliser : enregistre la demande puis déclenche GitHub
rep("""  try { d.marque = await loadMarque(user.id) || d.marque; } catch (e) {}
  const fonts = await loadFonts();
  const pdf = await buildReport(PDFLib, d, { fonts, fontkit, annex: null });
  const path = `${dos.user_id}/client/${dos.stripe_session_id}.pdf`;
  const { error: ue } = await admin.storage.from('dossiers').upload(path, pdf, { contentType: 'application/pdf', upsert: true });
  if (ue) { console.error('version client', ue); return jres({ error: 'stockage' }, 500); }
  await admin.from('dossiers').update({ perso: { exclure, sans, reco: d.perso.reco, client: d.perso.client, photos: (b.photos || []).slice(0, 8), at: new Date().toISOString() } }).eq('id', dos.id);
  const nom = [d.perso.client.prenom, d.perso.client.nom].filter(Boolean).join('-') || 'client';""", """  const req = { exclure, sans, reco: d.perso.reco, client: d.perso.client, photos: (b.photos || []).filter(x => String(x || '').startsWith(user.id + '/')).slice(0, 8), at: new Date().toISOString(), status: 'en_cours' };
  await admin.from('dossiers').update({ perso: req }).eq('id', dos.id);
  const tok = Deno.env.get('GITHUB_TOKEN');
  if (tok) {
    try {
      const g = await fetch(`https://api.github.com/repos/${GH_REPO()}/dispatches`, { method: 'POST', headers: { Authorization: 'Bearer ' + tok, Accept: 'application/vnd.github+json', 'User-Agent': 'TerrenUrbanisme', 'content-type': 'application/json' }, body: JSON.stringify({ event_type: 'version_client', client_payload: { id: dos.id } }) });
      if (g.ok) return jres({ ok: true, pending: true });
      console.warn('version client GitHub', g.status);
    } catch (e) { console.warn('version client GitHub', String(e && e.message || e).slice(0, 160)); }
  }
  return await buildPerso(dos.id);
}
// Fabrication de la version client (appelée par GitHub, sans limite de calcul)
async function buildPerso(dossierId) {
  const { data: dos } = await admin.from('dossiers').select('id, user_id, stripe_session_id, perso').eq('id', dossierId).maybeSingle();
  if (!dos || !dos.perso) return jres({ error: 'dossier' }, 404);
  const d = await loadD(dos.stripe_session_id);
  if (!d) return jres({ error: 'ancien' }, 409);
  const P = dos.perso, photos = [];
  for (const path of (P.photos || []).slice(0, 8)) {
    if (!String(path).startsWith(dos.user_id + '/')) continue;
    const { data: blob } = await admin.storage.from('perso').download(path);
    if (!blob) continue;
    const bytes = new Uint8Array(await blob.arrayBuffer());
    const png = bytes[0] === 0x89 && bytes[1] === 0x50, jpg = bytes[0] === 0xFF && bytes[1] === 0xD8;
    if ((png || jpg) && bytes.length < 6 * 1024 * 1024) photos.push({ bytes, png });
  }
  d.perso = { exclure: P.exclure || [], sans: P.sans || [], reco: P.reco || {}, client: P.client || {}, photos };
  try { d.marque = await loadMarque(dos.user_id) || d.marque; } catch (e) {}
  const fonts = await loadFonts();
  const pdf = await buildReport(PDFLib, d, { fonts, fontkit, annex: null });
  const path = `${dos.user_id}/client/${dos.stripe_session_id}.pdf`;
  const { error: ue } = await admin.storage.from('dossiers').upload(path, pdf, { contentType: 'application/pdf', upsert: true });
  if (ue) { console.error('version client', ue); await admin.from('dossiers').update({ perso: { ...P, status: 'erreur' } }).eq('id', dos.id); return jres({ error: 'stockage' }, 500); }
  const nom = [d.perso.client.prenom, d.perso.client.nom].filter(Boolean).join('-') || 'client';""")
rep("""  const { data: su } = await admin.storage.from('dossiers').createSignedUrl(path, 7 * 24 * 3600, { download: file });
  const { data: sv } = await admin.storage.from('dossiers').createSignedUrl(path, 7 * 24 * 3600);
  return jres({ ok: true, url: su && su.signedUrl, view: sv && sv.signedUrl, pages: (pdf.length / 1024 / 1024).toFixed(1) });""",
"""  await admin.from('dossiers').update({ perso: { ...P, status: 'pret', path, file, fait: new Date().toISOString() } }).eq('id', dos.id);
  return jres({ ok: true, path });""")
# 2. apercu_dossier : liens de la version client quand elle est prête
rep("""    return jres({ view: sv && sv.signedUrl, perso: dos.perso || null, pret: !!(ex && ex.length), chapitres: CHAP_PERSO });""",
"""    let client = null;
    if (dos.perso && dos.perso.status === 'pret' && dos.perso.path) {
      const { data: cu } = await admin.storage.from('dossiers').createSignedUrl(dos.perso.path, 7 * 24 * 3600, { download: dos.perso.file || 'Rapport-client.pdf' });
      const { data: cv } = await admin.storage.from('dossiers').createSignedUrl(dos.perso.path, 7 * 24 * 3600);
      client = { url: cu && cu.signedUrl, view: cv && cv.signedUrl };
    }
    return jres({ view: sv && sv.signedUrl, perso: dos.perso || null, pret: !!(ex && ex.length), chapitres: CHAP_PERSO, client });""")
# 3. Route d'administration ?perso=<id> (GitHub)
rep("""    if (url.searchParams.get('regen')) {""", """    if (url.searchParams.get('perso')) {
      try { return await buildPerso(url.searchParams.get('perso')); }
      catch (e) { console.error('version client', e); return new Response('erreur : ' + String(e && e.stack || e).slice(0, 800), { status: 500 }); }
    }
    if (url.searchParams.get('regen')) {""")
rep("""url.searchParams.get('regen') || url.searchParams.get('sweep') ||""", """url.searchParams.get('regen') || url.searchParams.get('perso') || url.searchParams.get('sweep') ||""")
open(p, 'w', encoding='utf-8').write(s); print('patch perso2 appliqué')
