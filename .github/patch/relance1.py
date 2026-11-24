"""Relance 24 h après une inscription sans achat : e-mail « Achetez sans surprise : vos -20 % expirent bientôt » (modèle carVertical),
remise de 20 % valable 48 h, envoyée une seule fois par adresse, aux personnes qui ont accepté de recevoir nos offres ou demandé une remise."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
CODE = r'''
// ---------- Relance des inscrits sans achat (24 h après) : remise de 20 % valable 48 h ----------
function relanceMail(tk: string, r: any) {
  const lien = REM_SITE + '/offre.html?r=' + encodeURIComponent(tk);
  const des = REM_SITE + '/desinscription.html?r=' + encodeURIComponent(tk);
  const F = 'font-family:Helvetica,Arial,sans-serif;';
  const T = '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"';
  const p = (t: string, x = '') => '<p style="margin:0 0 16px;' + F + 'font-size:16px;line-height:1.6;color:#3A2E28;text-align:justify;' + x + '">' + t + '</p>';
  const btn = (t: string) => T + ' style="margin:6px 0 22px"><tr><td align="center" bgcolor="#A3462C" style="border-radius:999px"><a href="' + lien + '" style="display:block;padding:15px 22px;' + F + 'font-size:16px;font-weight:bold;color:#FFFFFF;text-decoration:none;border-radius:999px">' + t + '</a></td></tr></table>';
  const ul = (L: string[]) => '<ul style="margin:0 0 18px;padding-left:20px;' + F + 'font-size:16px;line-height:1.6;color:#3A2E28">' + L.map(t => '<li style="margin:0 0 6px">' + t + '</li>').join('') + '</ul>';
  const parc = r.commune && r.section && r.numero ? '<div style="margin:14px auto 0;max-width:420px;' + F + 'font-size:15px;color:#6E625A">Votre terrain : <b style="color:#2A1D17">' + escH(r.commune) + ' · section ' + escH(r.section) + ' · parcelle ' + escH(r.numero) + '</b></div>' : '';
  const carte = (titre: string, txt: string, bg: string) => '<tr><td style="padding:0 0 16px">' + T + ' bgcolor="' + bg + '" style="border-radius:20px"><tr><td align="center" style="padding:26px 24px;' + F + '"><div style="font-size:22px;font-weight:bold;color:#2A1D17">' + titre + '</div><div style="margin-top:10px;font-size:15px;line-height:1.55;color:#5C4E46">' + txt + '</div></td></tr></table></td></tr>';
  const lk = 'color:#A3462C;text-decoration:underline';
  const html = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="x-apple-disable-message-reformatting"><meta name="format-detection" content="telephone=no,address=no,email=no"><title>Vos -20 % expirent bientôt</title></head><body style="margin:0;padding:0;background:#F4EFEC">'
    + '<div style="display:none;max-height:0;overflow:hidden">Avant de signer, prenez deux minutes pour vérifier que votre terrain ne cache pas de mauvaise surprise. -20 % pendant 48 heures.</div>'
    + T + ' bgcolor="#F4EFEC"><tr><td align="center" style="padding:24px 12px">'
    + T + ' style="max-width:600px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
    + '<tr><td align="center" style="padding:30px 24px 18px"><img src="' + REM_SITE + '/assets/presse/terrenurbanisme-logo.png" width="190" alt="TerrenUrbanisme" style="display:block;width:190px;max-width:60%;height:auto;border:0"></td></tr>'
    + '<tr><td style="padding:0 22px">' + T + ' bgcolor="#FBEEE8" style="border-radius:22px"><tr><td align="center" style="padding:30px 22px 32px;' + F + '">'
    + '<div style="font-size:26px;line-height:1.25;font-weight:bold;color:#2A1D17">Vous avez trouvé un terrain qui vous plaît ?</div>'
    + '<div style="margin:22px auto 0;width:150px;height:150px;border-radius:75px;background:#A3462C;color:#FFFFFF;font-size:52px;line-height:150px;font-weight:bold;letter-spacing:-2px;text-align:center">&minus;20&nbsp;%</div>'
    + parc + '</td></tr></table></td></tr>'
    + '<tr><td style="padding:26px 30px 6px">'
    + p('Avant de signer, prenez deux minutes pour vérifier que votre terrain ne cache pas de mauvaise surprise.')
    + btn('Utilisez votre remise de 20 %')
    + p('Beaucoup d\'acheteurs découvrent trop tard que leur terrain n\'est pas constructible, qu\'il se trouve en zone inondable ou qu\'une servitude bloque leur projet : simplement parce qu\'ils ont fait confiance à l\'annonce ou au vendeur.')
    + p('Avec ses rapports d\'urbanisme, TerrenUrbanisme vous aide à éviter les pièges les plus courants.')
    + p('Avec TerrenUrbanisme, vous levez le doute en quelques minutes, à partir des sources officielles de l\'État.')
    + '<p style="margin:6px 0 18px;' + F + 'font-size:19px;line-height:1.45;font-weight:bold;color:#2A1D17;text-align:center">Et aujourd\'hui, vous bénéficiez d\'une remise exceptionnelle de &minus;20&nbsp;% sur votre rapport d\'urbanisme.</p>'
    + btn('Activez votre remise de 20 %')
    + p('<b>Grâce au rapport d\'urbanisme complet, vous pouvez :</b>', 'text-align:left;margin-bottom:8px')
    + ul(['savoir si le terrain est constructible, et dans quelle zone du plan local d\'urbanisme ;', 'connaître la surface constructible, la hauteur autorisée et les reculs à respecter ;', 'repérer les risques (inondation, argiles, feu de forêt) et les servitudes ;', 'connaître le prix des terrains réellement vendus autour.'])
    + p('Et si le règlement de la zone ne peut pas être lu au moment du rapport ? Nous le régénérons sans frais pendant 30 jours.')
    + p('<b>Imaginez :</b> vous achetez un terrain qui semble parfait.')
    + p('Vous ne vérifiez pas le plan local d\'urbanisme. Le prix est intéressant, la vue est belle, le vendeur est rassurant…')
    + p('Puis vient le dépôt du permis de construire, et les mauvaises surprises : zone agricole, recul impossible à respecter, zone inondable.')
    + p('Résultat : un terrain payé au prix du constructible, sur lequel vous ne pouvez rien bâtir, et une revente au prix d\'un terrain agricole.')
    + p('<b>Maintenant, imaginez le scénario inverse :</b>', 'text-align:left;margin-bottom:8px')
    + p('Pour une fraction du prix du terrain, vous vérifiez la parcelle en quelques minutes :', 'margin-bottom:8px')
    + ul(['vous savez exactement ce que vous pouvez construire ;', 'vous pouvez éventuellement négocier un meilleur prix ;', 'vous signez le compromis sereinement, sans craindre de mauvaise surprise ni d\'exploser votre budget.'])
    + T + ' style="margin:4px 0 6px"><tr><td align="center" bgcolor="#A3462C" style="border-radius:999px"><a href="' + lien + '" style="display:block;padding:15px 22px;' + F + 'font-size:16px;font-weight:bold;color:#FFFFFF;text-decoration:none;border-radius:999px">J\'active ma remise de &minus;20&nbsp;% maintenant</a></td></tr></table>'
    + '<p style="margin:0 0 22px;' + F + 'font-size:13px;line-height:1.5;font-style:italic;color:#6E625A;text-align:center">Cette offre est valable encore 48 heures seulement, ensuite elle disparaît.</p>'
    + p('Un simple rapport aujourd\'hui peut vous éviter une erreur à plusieurs dizaines de milliers d\'euros.')
    + p('Vérifier maintenant, c\'est éviter les regrets plus tard.')
    + p('Soyez prudent, achetez en connaissance de cause.<br>L\'équipe <b>TerrenUrbanisme</b>', 'text-align:left;margin-bottom:26px')
    + '</td></tr>'
    + '<tr><td style="padding:0 22px 6px">' + T + '>'
    + carte('Des questions ?', 'Répondez simplement à cet e-mail : nous vous répondons dans les plus brefs délais.', '#FBEEE8')
    + carte('FAQ', 'Consultez notre foire aux questions <a href="' + REM_SITE + '/faq.html" style="' + lk + '">ici</a>.', '#F6F1EC')
    + '</table></td></tr>'
    + '<tr><td align="center" style="padding:14px 24px 30px;' + F + 'font-size:19px;font-weight:bold;color:#2A1D17">Plus de 34 900 communes couvertes, en France métropolitaine, en Corse et en outre-mer</td></tr>'
    + '<tr><td align="center" bgcolor="#A3462C" style="padding:26px 24px;' + F + 'font-size:13px;line-height:1.9;color:#FFFFFF">'
    + '<a href="' + REM_SITE + '/confidentialite.html" style="color:#FFFFFF;font-weight:bold;text-decoration:none">Politique de confidentialité</a><br>'
    + '<a href="' + REM_SITE + '/cgv.html" style="color:#FFFFFF;font-weight:bold;text-decoration:none">Conditions générales de vente</a><br>'
    + '<span style="color:#F6DCD2">Vous ne voulez plus recevoir ces e-mails ? <a href="' + des + '" style="color:#FFFFFF;text-decoration:underline">Désabonnez-vous</a></span><br>'
    + '<span style="color:#F6DCD2">TerrenUrbanisme · SIREN 898 332 473</span><br><span style="color:#F6DCD2">© ' + new Date().getFullYear() + ' TerrenUrbanisme. Tous droits réservés.</span>'
    + '</td></tr></table></td></tr></table></body></html>';
  const txt = ['Vous avez trouvé un terrain qui vous plaît ?', '', 'Avant de signer, prenez deux minutes pour vérifier que votre terrain ne cache pas de mauvaise surprise.', '',
    'Et aujourd\'hui, vous bénéficiez d\'une remise exceptionnelle de -20 % sur votre rapport d\'urbanisme.', (r.commune && r.section && r.numero ? 'Votre terrain : ' + r.commune + ', section ' + r.section + ', parcelle ' + r.numero : ''), '',
    'J\'active ma remise de -20 % maintenant : ' + lien, 'Cette offre est valable encore 48 heures seulement, ensuite elle disparaît.', '',
    'Grâce au rapport d\'urbanisme complet, vous pouvez :', '- savoir si le terrain est constructible, et dans quelle zone ;', '- connaître la surface constructible, la hauteur et les reculs ;', '- repérer les risques et les servitudes ;', '- connaître le prix des terrains vendus autour.', '',
    'Soyez prudent, achetez en connaissance de cause.', 'L\'équipe TerrenUrbanisme', '', 'Des questions ? Répondez simplement à cet e-mail.', 'Se désabonner : ' + des].filter((x, i, a) => !(x === '' && a[i - 1] === '')).join('\n');
  return { html, txt, des };
}
async function relancesAchat(testTo?: string) {
  const SUJ = 'Achetez sans surprise : vos -20 % expirent bientôt';
  const creer = async (email: string, parc: any) => {
    const tk = crypto.randomUUID().replace(/-/g, '');
    const r: any = { email, token: tk, taux: 20, motif: 'relance', expire_le: new Date(Date.now() + 48 * 3600000).toISOString(), insee: parc && parc.insee || null, section: parc && parc.section || null, numero: parc && parc.numero || null, commune: parc && parc.commune || null };
    const { error } = await admin.from('remises').insert(r);
    if (error) throw new Error('remise : ' + error.message);
    return r;
  };
  const envoyer = async (email: string, r: any) => { const m = relanceMail(r.token, r); await smtpSimple([email], SUJ, m.txt, m.html, ['List-Unsubscribe: <' + m.des + '>']); };
  if (testTo) { const r = await creer(testTo, { insee: '2A247', section: 'G', numero: '7', commune: 'Porto-Vecchio' }); await envoyer(testTo, r); return 1; }
  // Inscrits entre 48 h et 24 h : adresse laissée sur le site (avec accord pour nos offres, ou demande de remise), sans achat ni désinscription
  const de = new Date(Date.now() - 48 * 3600000).toISOString(), a = new Date(Date.now() - 24 * 3600000).toISOString();
  const { data: L } = await admin.from('leads').select('email, source, consentement_offres, achete, desinscrit, insee, section, numero, commune').gte('premiere_visite', de).lt('premiere_visite', a).limit(500);
  let n = 0;
  for (const l of (L || [])) {
    try {
      const email = String(l.email || '').toLowerCase();
      if (!email || l.achete || l.desinscrit || !(l.consentement_offres || l.source === 'remise')) continue;
      const { count: nd } = await admin.from('dossiers').select('id', { count: 'exact', head: true }).ilike('email', email);
      if ((nd || 0) > 0) continue;
      const { count: ds } = await admin.from('remises').select('id', { count: 'exact', head: true }).eq('email', email).eq('desinscrit', true);
      if ((ds || 0) > 0) continue;
      if (!(await onceOnly('mails/relance20_' + (await sha(email))))) continue;
      await envoyer(email, await creer(email, l.insee ? l : null)); n++;
    } catch (e) { console.error('relance', String((e as any)?.message || e).slice(0, 160)); }
  }
  return n;
}
'''
rep("async function remiseInscription(req: Request) {", CODE + "async function remiseInscription(req: Request) {")
# Taux de la remise renvoyé à la page d'offre
rep("const { data: x } = await admin.from('remises').select('email, insee, section, numero, commune, motif, expire_le, utilise_le').eq('token', tk).maybeSingle();",
    "const { data: x } = await admin.from('remises').select('email, insee, section, numero, commune, motif, expire_le, utilise_le, taux').eq('token', tk).maybeSingle();")
rep("motif: x.motif, expire_le: x.expire_le });", "motif: x.motif, expire_le: x.expire_le, taux: x.taux || 15 });")
rep("if (b.desinscription) { await admin.from('remises').update({ desinscrit: true }).eq('email', x.email); return jres({ ok: true, desinscrit: true }); }",
    "if (b.desinscription) { await admin.from('remises').update({ desinscrit: true }).eq('email', x.email); try { await admin.from('leads').update({ desinscrit: true }).eq('email', String(x.email || '').toLowerCase()); } catch (e) {} return jres({ ok: true, desinscrit: true }); }")
# Tâche planifiée (toutes les heures) et envoi de test
rep("  if (url.searchParams.get('rappels') && adminKey && safeEq(req.headers.get('x-tu-admin'), adminKey)) {",
    """  if (url.searchParams.get('relance') && adminKey && safeEq(req.headers.get('x-tu-admin'), adminKey)) {
    const to = url.searchParams.get('relance') === 'test' ? String(url.searchParams.get('to') || '') : '';
    if (to && to !== 'contact@terrenurbanisme.com') return new Response('test réservé à contact@terrenurbanisme.com', { status: 400 });
    try { const n = await relancesAchat(to || undefined); return new Response('relances envoyées : ' + n); } catch (e) { console.error('relances', e); return new Response(String((e as any)?.message || e).slice(0, 300), { status: 500 }); }
  }
  if (url.searchParams.get('rappels') && adminKey && safeEq(req.headers.get('x-tu-admin'), adminKey)) {""")
open(p, 'w', encoding='utf-8').write(s); print('ok relance1')
