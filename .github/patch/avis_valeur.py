# Avis de valeur agences : fiche du bien, honoraires et prix net vendeur, suivi d'ouverture du rapport client avec alerte à l'agent
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)

# 1. Versions de test Netlify (deploy-preview-N--terrenurbanisme.netlify.app) autorisées à appeler la fonction
rep("    if (ORIGINS.includes(o) && res.headers.has('Access-Control-Allow-Origin'))",
    "    if ((ORIGINS.includes(o) || /^https:\\/\\/[a-z0-9-]+--terrenurbanisme\\.netlify\\.app$/.test(o)) && res.headers.has('Access-Control-Allow-Origin'))")

# 2. Suivi d'ouverture de la version client
rep("  if (req.method === 'GET' && rp) return await serveReport(rp[1]);", "  if (req.method === 'GET' && rp) return await serveReport(rp[1], url, req);")
rep("async function serveReport(slug) {", r"""// Ouverture de la version client par le client : compteur, et e-mail à l'agent à la première ouverture (si l'alerte est activée)
async function alerteOuverture(cr) {
  try {
    const to = await userEmail(cr.user_id); if (!to) return;
    const P = cr.perso || {}, cl = P.client || {}, rc = P.reco || {};
    const qui = [cl.civ, cl.prenom, cl.nom].filter(Boolean).join(' ') || 'Votre client';
    const ref = [cr.commune, cr.section, cr.numero].filter(Boolean).join(' ');
    const tel = cl.tel ? '\nSon téléphone : ' + cl.tel : '';
    const txt = 'Bonjour,\n\n' + qui + ' vient d\'ouvrir le rapport que vous lui avez envoyé (' + ref + ').\n\nC\'est le bon moment pour l\'appeler et répondre à ses questions.' + tel + '\n\nVoir le dossier : ' + SITE + '/espace-pro.html\n\nTerrenUrbanisme';
    const html = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6;color:#2A1D17"><p>Bonjour,</p><p><strong>' + qui.replace(/</g, '') + '</strong> vient d\'ouvrir le rapport que vous lui avez envoyé (' + ref.replace(/</g, '') + ').</p><p>C\'est le bon moment pour l\'appeler et répondre à ses questions.' + (cl.tel ? '<br>Son téléphone : <strong>' + String(cl.tel).replace(/</g, '') + '</strong>' : '') + '</p><p><a href="' + SITE + '/espace-pro.html" style="display:inline-block;background:#A3462C;color:#fff;text-decoration:none;font-weight:700;padding:12px 20px;border-radius:10px">Voir le dossier</a></p><p style="color:#6E625A;font-size:13px">TerrenUrbanisme</p></div>';
    const client = new SMTPClient({ connection: { hostname: Deno.env.get('SMTP_HOST') || 'ssl0.ovh.net', port: Number(Deno.env.get('SMTP_PORT') || '465'), tls: true, auth: { username: Deno.env.get('SMTP_USER') || 'contact@terrenurbanisme.com', password: Deno.env.get('SMTP_PASSWORD') } } });
    let coupe = false;
    try { await client.send({ from: 'TerrenUrbanisme <' + (Deno.env.get('SMTP_USER') || 'contact@terrenurbanisme.com') + '>', to, subject: qui + ' vient d\'ouvrir votre rapport', mimeContent: mimeParts(txt, html) }); }
    catch (e) { if (/close_notify|UnexpectedEof/i.test(String(e && e.message || e))) coupe = true; else console.error('alerte ouverture', e); }
    finally { if (!coupe) { try { await client.close(); } catch (e) {} } }
  } catch (e) { console.error('alerte ouverture', e); }
}
async function noterOuverture(cr, url, req) {
  try {
    if (url && url.searchParams.get('a') === '1') return; // l'agent qui consulte sa propre version
    const rg = req && req.headers.get('Range');
    if (rg && !/^bytes=0-/.test(rg)) return; // lecture du PDF par morceaux : une seule ouverture
    const now = Date.now();
    if (cr.vu_dernier && now - new Date(cr.vu_dernier).getTime() < 30 * 60000) return;
    const premier = !(cr.vu_nb > 0);
    await admin.from('dossiers').update({ vu_nb: (cr.vu_nb || 0) + 1, vu_dernier: new Date(now).toISOString(), ...(premier ? { vu_le: new Date(now).toISOString() } : {}) }).eq('id', cr.id);
    if (premier && cr.perso && cr.perso.reco && cr.perso.reco.alerte === true) {
      const job = alerteOuverture(cr);
      try { EdgeRuntime.waitUntil(job); } catch (e) { await job; }
    }
  } catch (e) { console.error('ouverture', e); }
}
async function serveReport(slug, url, req) {""")
rep("    const { data: cr } = await admin.from('dossiers').select('perso').gte('id', lo).lte('id', hi).limit(1).maybeSingle();",
    "    const { data: cr } = await admin.from('dossiers').select('id, user_id, perso, commune, section, numero, vu_nb, vu_dernier').gte('id', lo).lte('id', hi).limit(1).maybeSingle();")
rep("    const { data: cb } = await admin.storage.from('dossiers').download(P.path);\n",
    "    await noterOuverture(cr, url, req);\n    const { data: cb } = await admin.storage.from('dossiers').download(P.path);\n")

# 3. Champs enregistrés : fiche du bien, honoraires, négociation, délai, alerte
rep("designation: t(rc.designation).slice(0, 1200),", r"""designation: t(rc.designation).slice(0, 1200), alerte: rc.alerte === true,
      fiche: (() => { const f = rc.fiche && typeof rc.fiche === 'object' ? rc.fiche : {}, o = {}; ['shab', 'sterrain', 'pieces', 'chambres', 'annee'].forEach(k => { const v = t(f[k]).replace(/[^0-9]/g, '').slice(0, 7); if (v) o[k] = v; }); if (/^[A-G]$/.test(t(f.dpe))) o.dpe = t(f.dpe); if (/^(neuf|tres_bon|bon|rafraichir|renover)$/.test(t(f.etat))) o.etat = t(f.etat); if (Array.isArray(f.atouts)) o.atouts = f.atouts.map(x => t(x).slice(0, 40)).filter(Boolean).slice(0, 12); return Object.keys(o).length ? o : null; })(),
      hono: t(rc.hono).replace(',', '.').replace(/[^0-9.]/g, '').slice(0, 5), hono_charge: rc.hono_charge === 'acquereur' ? 'acquereur' : 'vendeur', nego: t(rc.nego).replace(',', '.').replace(/[^0-9.]/g, '').slice(0, 4), delai: /^(3|6|9|12)$/.test(t(rc.delai)) ? t(rc.delai) : '',""")

# 4. Rapport : fiche du bien et calcul des prix
rep("PERSO.reco.designation || PERSO.reco.type ||", "PERSO.reco.designation || PERSO.reco.type || PERSO.reco.fiche ||")
rep("    if (TYPB || RC.designation) {\n      h3('Désignation du bien');\n      if (TYPB) kv([['Type de bien', TYPB]], { lw: 0.3 });",
r"""    const FI = RC.fiche || {}, ETAT = { neuf: 'Neuf ou récent', tres_bon: 'Très bon état', bon: 'Bon état', rafraichir: 'À rafraîchir', renover: 'À rénover' };
    const n2 = v => fmt(Number(v));
    const FROWS = [['Type de bien', TYPB], ['Surface habitable', FI.shab ? n2(FI.shab) + ' m²' : ''], ['Surface du terrain', FI.sterrain ? n2(FI.sterrain) + ' m²' : ''], ['Pièces', FI.pieces ? FI.pieces + (FI.chambres ? ' dont ' + FI.chambres + ' chambre' + (FI.chambres > 1 ? 's' : '') : '') : (FI.chambres ? FI.chambres + ' chambre' + (FI.chambres > 1 ? 's' : '') : '')], ['Année de construction', FI.annee || ''], ['Diagnostic énergétique (DPE)', FI.dpe ? 'Classe ' + FI.dpe : ''], ['État général', ETAT[FI.etat] || ''], ['Atouts', (FI.atouts || []).join(' · ')]].filter(r => r[1]);
    if (FROWS.length || RC.designation) {
      h3('Désignation du bien');
      if (FROWS.length) kv(FROWS, { lw: 0.34 });""")
rep("        text('L\\'agence affine l\\'analyse des ventes avec ce que les chiffres ne voient pas : la vue, l\\'exposition, l\\'accès, la viabilisation, la demande actuelle et l\\'état du bien.', { size: 9, color: C.muet });",
r"""        text('L\'agence affine l\'analyse des ventes avec ce que les chiffres ne voient pas : la vue, l\'exposition, l\'accès, la viabilisation, la demande actuelle et l\'état du bien.', { size: 9, color: C.muet });
        const PC = Number(String(RC.conseille || '').replace(/[^0-9]/g, '')), HP = Number(RC.hono) || 0, NG = Number(RC.nego) || 0;
        if (PC && (HP || NG || RC.delai)) {
          const rows = [['Prix de présentation' + (HP ? ' (honoraires inclus)' : ''), fmt(PC) + ' €']];
          if (HP) { const net = Math.round(PC / (1 + HP / 100) / 100) * 100; rows.push(['Honoraires de l\'agence', String(HP).replace('.', ',') + ' % · ' + fmt(PC - net) + ' € à la charge ' + (RC.hono_charge === 'acquereur' ? 'de l\'acquéreur' : 'du vendeur')]); rows.push(['Prix net vendeur', fmt(net) + ' €']); }
          if (NG) { const att = Math.round(PC * (1 - NG / 100) / 1000) * 1000; rows.push(['Marge de négociation estimée', String(NG).replace('.', ',') + ' %, soit un prix de vente attendu d\'environ ' + fmt(att) + ' €']); }
          if (RC.delai) rows.push(['Délai de vente estimé', RC.delai === '3' ? 'Moins de 3 mois' : RC.delai === '12' ? '9 à 12 mois' : (Number(RC.delai) - 3) + ' à ' + RC.delai + ' mois']);
          h3('Prix et conditions de vente'); kv(rows, { lw: 0.34 });
        }""")
open(p, 'w', encoding='utf-8').write(s); print('patch avis de valeur appliqué')
