// Modèles des e-mails de prospection TerrenUrbanisme (un par cible)
const PROSPECT_TPL = (() => {
  const H = v => String(v == null ? '' : v).replace(/[<>&"]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;' }[c]));
  const btn = (href, t, ghost) => `<a href="${href}" style="display:inline-block;${ghost ? 'background:#fff;color:#A3462C;border:2px solid #A3462C;padding:12px 22px' : 'background:#A3462C;color:#fff;border:2px solid #A3462C;padding:12px 22px'};text-decoration:none;font-weight:700;font-size:15px;border-radius:12px;margin:0 8px 10px 0">${t}</a>`;
  const li = a => `<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 18px">${a.map(x => `<tr><td valign="top" style="padding:0 10px 9px 0;color:#A3462C;font-weight:800;font-size:15px">✓</td><td style="padding:0 0 9px;font-size:15px;line-height:1.55">${x}</td></tr>`).join('')}</table>`;
  const P = t => `<p style="font-size:15px;line-height:1.65;margin:0 0 16px">${t}</p>`;
  const box = t => `<div style="background:#FBF3EF;border-left:4px solid #A3462C;border-radius:10px;padding:14px 18px;margin:0 0 20px;font-size:15px;line-height:1.6">${t}</div>`;
  const utm = (u, c) => u + (u.includes('?') ? '&' : '?') + 'utm_source=prospection&utm_medium=email&utm_campaign=' + c;
  const T = {
    agence: c => ({
      objet: 'Ce terrain est-il vraiment constructible ? Votre client vous le demandera',
      pre: 'Rapport d\'urbanisme et avis de valeur à votre nom, prêts en quelques minutes.',
      eyebrow: 'Agences immobilières',
      titre: 'Un mandat mal renseigné peut vous coûter la vente',
      corps: P('Bonjour,') +
        P('Une servitude oubliée, une zone du PLU mal lue, un terrain en zone inondable : il suffit d\'une information erronée pour qu\'une vente tombe chez le notaire, ou qu\'un acquéreur se retourne contre l\'agence des mois plus tard.') +
        P('<strong>TerrenUrbanisme</strong> établit en quelques minutes le rapport d\'urbanisme complet de n\'importe quelle parcelle en France : zone et règlement du PLU lus dans le texte, risques, servitudes, loi Littoral et loi Montagne, monuments historiques, réseaux et ventes réelles du secteur.') +
        `<p style="font-size:15px;font-weight:700;margin:0 0 10px">Et pour votre agence, c'est votre document :</p>` +
        li(['Votre logo et votre conseiller, avec sa photo, sur la couverture', 'Votre avis de valeur : fiche du bien, prix recommandé, honoraires et prix net vendeur, à côté de notre analyse des ventes', 'Vous choisissez les rubriques montrées au client, puis vous l\'envoyez en un clic, avec une alerte dès qu\'il l\'ouvre', 'Un tableau de bord pour suivre l\'activité de chaque collaborateur']) +
        box('<strong>1 à 2 heures de recherches site par site, remplacées par 3 minutes.</strong> Combien vaut une heure de votre temps ? Avec un pack de 50 crédits, le rapport revient à 5 € : bien moins qu\'une vente qui échoue.') +
        `<p style="margin:0 0 8px">${btn(c.video || utm('https://terrenurbanisme.com/agences-immobilieres.html', 'agences'), 'Voir la vidéo (2 min)')}${btn(utm('https://terrenurbanisme.com/exemple.html', 'agences'), 'Voir un exemple de rapport', true)}</p>` +
        P('Prêt à l\'essayer sur l\'un de vos mandats ? <a href="' + utm('https://terrenurbanisme.com/tarifs.html', 'agences') + '" style="color:#A3462C;font-weight:700">Créez votre espace agence</a> en deux minutes, ou répondez simplement à ce message.'),
    }),
    mandataire: c => ({
      objet: 'Agent indépendant : un rapport d\'urbanisme à votre nom pour chaque mandat',
      pre: 'Le niveau de sécurité d\'une grande agence, sans le service juridique.',
      eyebrow: 'Agents immobiliers indépendants',
      titre: 'Seul face au client, vous n\'avez pas le droit à l\'erreur',
      corps: P('Bonjour,') +
        P('En indépendant, pas de service juridique ni d\'assistante pour vérifier un PLU avant de rentrer un mandat. Pourtant, c\'est votre nom qui engage votre responsabilité si un terrain annoncé constructible ne l\'est pas.') +
        P('<strong>TerrenUrbanisme</strong> établit en quelques minutes le rapport d\'urbanisme complet de la parcelle : zone et règlement du PLU, risques, servitudes, loi Littoral et loi Montagne, réseaux, ventes réelles du secteur.') +
        li(['Votre nom, votre photo et vos coordonnées sur la couverture', 'Votre avis de valeur, vos honoraires et le prix net vendeur, à côté de notre analyse du marché', 'L\'envoi au client en un clic, avec une alerte dès qu\'il ouvre le rapport', 'Un document de plus de 40 pages qui vous place au niveau des grandes enseignes']) +
        box('<strong>3 minutes au lieu d\'une demi-journée de recherches.</strong> Avec un pack de 50 crédits, le rapport revient à 5 € : le prix d\'un café pour un mandat sécurisé et un vendeur rassuré.') +
        `<p style="margin:0 0 8px">${btn(c.video || utm('https://terrenurbanisme.com/agences-immobilieres.html', 'mandataires'), 'Voir la vidéo (2 min)')}${btn(utm('https://terrenurbanisme.com/exemple.html', 'mandataires'), 'Voir un exemple de rapport', true)}</p>` +
        P('<a href="' + utm('https://terrenurbanisme.com/tarifs.html', 'mandataires') + '" style="color:#A3462C;font-weight:700">Créez votre espace</a> en deux minutes, ou répondez à ce message pour toute question.'),
    }),
    mairie: c => ({
      objet: '« Mon terrain est-il constructible ? » : la réponse, directement sur le site de la mairie',
      pre: 'Moins d\'appels au service urbanisme, des habitants mieux informés.',
      eyebrow: 'Communes',
      titre: 'Votre service urbanisme répond-il chaque jour à la même question ?',
      corps: P('Madame, Monsieur,') +
        P('« Mon terrain est-il constructible ? », « Puis-je faire une piscine ? », « Quelle est ma zone ? » : ces appels occupent chaque semaine des heures au service urbanisme. Et un habitant mal informé, c\'est un dossier incomplet, une construction non conforme, parfois un contentieux.') +
        P('<strong>TerrenUrbanisme</strong> permet à vos habitants d\'obtenir, depuis le site de la mairie, le rapport d\'urbanisme complet de leur parcelle en quelques minutes : zone et règlement du PLU, risques, servitudes, réseaux, démarches à suivre.') +
        li(['Un bouton « Analyser mon terrain » sur le site de la mairie, ou votre propre bouton avec notre lien', 'Un rapport aux couleurs de la commune : logo et coordonnées de la mairie', 'Un espace mairie pour suivre chaque demande, parcelle par parcelle', 'Les rapports couvrent uniquement les parcelles de votre commune']) +
        box('<strong>Un service public de plus pour vos habitants, sans recrutement ni développement.</strong> La mise en place prend quelques minutes à votre webmaster, et le stock de rapports s\'adapte au nombre d\'habitants.') +
        `<p style="margin:0 0 8px">${btn(c.video || utm('https://terrenurbanisme.com/mairies.html', 'mairies'), 'Voir la vidéo (1 min 20)')}${btn(utm('https://terrenurbanisme.com/mairies.html', 'mairies'), 'Découvrir l\'offre communale', true)}</p>` +
        P('Nous pouvons vous présenter le service en visioconférence, sur une parcelle de votre commune : répondez simplement à ce message.'),
    }),
    expert: c => ({
      objet: 'Vos expertises : l\'urbanisme de la parcelle analysé en 3 minutes',
      pre: 'PLU, servitudes, risques et ventes réelles du secteur, dans un seul rapport.',
      eyebrow: 'Experts immobiliers',
      titre: 'Une constructibilité mal évaluée fausse toute l\'expertise',
      corps: P('Bonjour,') +
        P('Entre un terrain constructible et un terrain qui ne l\'est pas, la valeur peut varier de un à dix. Une servitude, une zone de risque ou une règle du PADDUC oubliée, et c\'est la crédibilité de votre rapport d\'expertise qui est en jeu.') +
        P('<strong>TerrenUrbanisme</strong> réunit en quelques minutes tout l\'urbanisme de la parcelle : zone et règlement du PLU lus dans le texte, prescriptions, servitudes d\'utilité publique, risques naturels et technologiques, loi Littoral et loi Montagne, monuments historiques, ainsi que les ventes réelles du secteur (DVF).') +
        li(['Des sources officielles citées, que vous pouvez joindre en annexe de vos expertises', 'Les extraits du règlement de la zone, pour justifier vos hypothèses', 'Les ventes comparables autour de la parcelle', 'Votre logo sur les rapports avec les crédits professionnels']) +
        box('<strong>Une à deux heures de recherches remplacées par 3 minutes</strong>, pour un rapport qui revient à 5 € avec un pack de 50 crédits.') +
        `<p style="margin:0 0 8px">${btn(utm('https://terrenurbanisme.com/exemple.html', 'experts'), 'Voir un exemple de rapport')}${btn(utm('https://terrenurbanisme.com/tarifs.html', 'experts'), 'Voir les crédits professionnels', true)}</p>` +
        P('Une question, ou une démonstration sur l\'un de vos dossiers ? Répondez simplement à ce message.'),
    }),
  };
  function build(cible, c) {
    const t = (T[cible] || T.agence)(c || {});
    const stop = c && c.stop ? c.stop : '#';
    const html = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${H(t.objet)}</title></head><body style="margin:0;background:#F9F2EE;font-family:Helvetica,Arial,sans-serif;color:#2A1D17"><div style="display:none;max-height:0;overflow:hidden;opacity:0">${H(t.pre)}</div><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F9F2EE;padding:28px 12px"><tr><td align="center"><table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border:1px solid #EFE6DF;border-radius:18px;overflow:hidden">
<tr><td style="background:#2A1D17;padding:20px 30px"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td><img src="https://terrenurbanisme.com/apple-touch-icon.png" width="36" height="36" alt="" style="display:block;border-radius:9px"></td><td style="padding-left:12px;font-size:18px;font-weight:700;color:#F6EEE9">TerrenUrbanisme</td></tr></table></td></tr>
<tr><td style="padding:28px 30px 8px"><p style="margin:0 0 6px;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#A3462C">${H(t.eyebrow)}</p><h1 style="font-size:24px;line-height:1.3;margin:0 0 18px">${H(t.titre)}</h1>${t.corps}
<p style="font-size:15px;line-height:1.6;margin:8px 0 4px">Bien cordialement,</p><p style="font-size:15px;line-height:1.5;margin:0 0 24px"><strong>L'équipe TerrenUrbanisme</strong><br><span style="font-size:13.5px;color:#6E625A">Rapports d'urbanisme pour les professionnels de l'immobilier et les communes</span></p></td></tr>
<tr><td style="padding:18px 30px 22px;background:#FBF8F6;border-top:1px solid #EFE6DF;font-size:12.5px;line-height:1.7;color:#8A7D74"><a href="https://terrenurbanisme.com/?utm_source=prospection&amp;utm_medium=email" style="color:#A3462C;font-weight:700;text-decoration:none">terrenurbanisme.com</a> · contact@terrenurbanisme.com<br>TerrenUrbanisme · SIREN 898 332 473<br>Vous recevez ce message en tant que professionnel. <a href="${stop}" style="color:#8A7D74">Ne plus recevoir nos messages</a></td></tr></table></td></tr></table></body></html>`;
    const txt = (t.corps.replace(/<br>/g, '\n').replace(/<\/p>|<\/tr>|<\/div>/g, '\n\n').replace(/<a [^>]*href="([^"]+)"[^>]*>([^<]+)<\/a>/g, '$2 : $1').replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/\n{3,}/g, '\n\n').trim()) + '\n\nBien cordialement,\nL\'équipe TerrenUrbanisme\ncontact@terrenurbanisme.com · terrenurbanisme.com\n\nNe plus recevoir nos messages : ' + stop;
    return { objet: t.objet, html, txt };
  }
  return { build, cibles: Object.keys(T) };
})();

// ---------- Prospection directe : un e-mail à la fois depuis contact@terrenurbanisme.com ----------
async function prospCfg() { const { data } = await admin.from('prospection_cfg').select('*').eq('id', 1).maybeSingle(); return data; }
function heureParis() { const p = new Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris', hour: '2-digit', minute: '2-digit', weekday: 'short', hour12: false }).formatToParts(new Date()); const g = t => (p.find(x => x.type === t) || {}).value || ''; return { h: Number(g('hour')) + Number(g('minute')) / 60, j: g('weekday') }; }
async function prospEnvoyer(P, cfg, test) {
  const stop = SITE + '/desinscription/' + P.token;
  const video = P.cible === 'mairie' ? cfg.video_mairies : cfg.video_agences;
  const m = PROSPECT_TPL.build(P.cible, { stop, video: video || null, societe: P.societe, ville: P.ville });
  const to = test ? test : P.email;
  await smtpSimple([to], m.objet, m.txt, m.html, ['List-Unsubscribe: <' + stop + '>', 'Reply-To: contact@terrenurbanisme.com']);
  return m.objet;
}
async function handleProspection(req, url) {
  const cfg = await prospCfg(); if (!cfg || !safeEq(String(url.searchParams.get('k') || ''), cfg.cle)) return jres({ error: 'cle' }, 403);
  const op = url.searchParams.get('prospection');
  if (op === 'test') {
    // Envoi d'essai : uniquement vers la boîte TerrenUrbanisme
    const out = [];
    for (const c of PROSPECT_TPL.cibles) out.push(await prospEnvoyer({ cible: c, token: '00000000-0000-0000-0000-000000000000', email: 'contact@terrenurbanisme.com' }, cfg, 'contact@terrenurbanisme.com'));
    return jres({ ok: true, envoyes: out });
  }
  if (op === 'import') {
    const tok = Deno.env.get('GITHUB_TOKEN'); if (!tok) return jres({ error: 'token' }, 500);
    const r = await fetch('https://api.github.com/repos/alexisriccobene/terrenurbanisme-brevo/contents/export/contacts.csv', { headers: { Authorization: 'Bearer ' + tok, Accept: 'application/vnd.github.raw', 'User-Agent': 'TerrenUrbanisme' } });
    if (!r.ok) return jres({ error: 'github ' + r.status }, 502);
    const lines = (await r.text()).split(/\r?\n/).filter(Boolean); lines.shift();
    const parse = l => { const o = []; let cur = '', q = false; for (const ch of l) { if (ch === '"') q = !q; else if (ch === ',' && !q) { o.push(cur); cur = ''; } else cur += ch; } o.push(cur); return o; };
    const CIB = [['mandataire', 'mandataire'], ['mairie', 'mairie'], ['agence', 'agence'], ['expert', 'expert'], ['notaire', 'notaire'], ['diagnost', 'diagnostiqueur'], ['géom', 'geometre'], ['architect', 'architecte'], ['artisan', 'artisan'], ['courtier', 'courtier']];
    const PR = { mandataire: 1, mairie: 1, agence: 2, expert: 2 };
    const rows = lines.map(parse).filter(a => /@/.test(a[0] || '')).map(a => { const ls = (a[1] || '').toLowerCase(); const c = (CIB.find(x => ls.includes(x[0])) || [0, 'autre'])[1]; return { email: a[0].trim().toLowerCase(), cible: c, listes: a[1] || null, societe: a[2] || null, ville: a[3] || null, departement: a[4] || null, priorite: PR[c] || 5, statut: a[7] === '1' ? 'stop' : 'attente' }; });
    let n = 0; for (let i = 0; i < rows.length; i += 500) { const { error } = await admin.from('prospects').upsert(rows.slice(i, i + 500), { onConflict: 'email', ignoreDuplicates: true }); if (error) return jres({ error: error.message, fait: n }, 500); n += Math.min(500, rows.length - i); }
    return jres({ ok: true, lignes: rows.length });
  }
  if (op !== 'tick') return jres({ error: 'op' }, 400);
  if (!cfg.actif) return jres({ ok: true, pause: true });
  const { h, j } = heureParis();
  if (/^(sam|dim)/i.test(j) || h < Number(cfg.heure_debut) || h >= Number(cfg.heure_fin)) return jres({ ok: true, hors_horaires: true });
  if (Math.random() > Number(cfg.proba)) return jres({ ok: true, attente: true });
  const debut = new Date(); debut.setUTCHours(0, 0, 0, 0);
  const { count } = await admin.from('prospects').select('email', { count: 'exact', head: true }).gte('envoye_le', debut.toISOString());
  if ((count || 0) >= cfg.quota_jour) return jres({ ok: true, quota: count });
  const { data: L } = await admin.from('prospects').select('*').eq('statut', 'attente').in('cible', cfg.cibles || []).order('priorite', { ascending: true }).limit(30);
  if (!L || !L.length) return jres({ ok: true, vide: true });
  const P = L[Math.floor(Math.random() * L.length)];
  const { data: lock } = await admin.from('prospects').update({ statut: 'envoi', envoye_le: new Date().toISOString() }).eq('email', P.email).eq('statut', 'attente').select('email');
  if (!lock || !lock.length) return jres({ ok: true, concurrence: true });
  try { await prospEnvoyer(P, cfg, null); await admin.from('prospects').update({ statut: 'envoye' }).eq('email', P.email); return jres({ ok: true, envoye: P.cible }); }
  catch (e) { const m = String(e && e.message || e).slice(0, 200); await admin.from('prospects').update({ statut: 'erreur', erreur: m }).eq('email', P.email); console.error('prospection', m); return jres({ ok: false, erreur: m }); }
}
async function handleDesinscription(tok) {
  const page = (t) => new Response(`<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TerrenUrbanisme</title></head><body style="margin:0;background:#F9F2EE;font-family:Helvetica,Arial,sans-serif;color:#2A1D17;display:flex;min-height:100vh;align-items:center;justify-content:center;padding:20px"><div style="max-width:460px;background:#fff;border:1px solid #EFE6DF;border-radius:18px;padding:32px;text-align:center"><p style="font-size:20px;font-weight:700;margin:0 0 10px">TerrenUrbanisme</p><p style="font-size:15px;line-height:1.6;margin:0">${t}</p></div></body></html>`, { headers: { 'content-type': 'text/html; charset=utf-8' } });
  if (!/^[0-9a-f-]{36}$/.test(tok)) return page('Lien invalide.');
  await admin.from('prospects').update({ statut: 'stop', stop_le: new Date().toISOString() }).eq('token', tok);
  return page('C\'est noté : vous ne recevrez plus nos messages.');
}
