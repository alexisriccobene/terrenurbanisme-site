# Remise de bienvenue de 15 % : inscription par e-mail (fenêtre du site), envoi de l'e-mail, lecture du lien, désinscription, remise marquée comme utilisée au paiement
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:80], s.count(a))
    s = s.replace(a, b)

FN = r'''
const REM_SITE = 'https://terrenurbanisme.com';
function remiseMail(tk: string, r: any) {
  const lien = REM_SITE + '/offre.html?r=' + encodeURIComponent(tk);
  const des = REM_SITE + '/desinscription.html?r=' + encodeURIComponent(tk);
  const parc = r.commune && r.section && r.numero ? escH(r.commune) + ' · section ' + escH(r.section) + ' · parcelle ' + escH(r.numero) : '';
  const btn = (t: string) => '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin:22px 0"><tr><td align="center" bgcolor="#A3462C" style="border-radius:999px"><a href="' + lien + '" style="display:block;padding:16px 22px;font-family:Arial,sans-serif;font-size:17px;font-weight:bold;color:#FFFFFF;text-decoration:none;border-radius:999px">' + t + '</a></td></tr></table>';
  const li = (t: string, d: string) => '<tr><td width="28" valign="top" style="padding:8px 0;font-family:Arial,sans-serif;font-size:17px;color:#A3462C;font-weight:bold">&#10003;</td><td style="padding:8px 0;font-family:Arial,sans-serif;font-size:16px;line-height:1.5;color:#2A1D17"><b>' + t + '</b> ' + d + '</td></tr>';
  const html = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Votre remise de 15 %</title></head><body style="margin:0;padding:0;background:#F4EFEC">'
    + '<div style="display:none;max-height:0;overflow:hidden">Votre remise de 15 % sur le rapport d\'urbanisme de votre terrain, valable 14 jours.</div>'
    + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#F4EFEC"><tr><td align="center" style="padding:24px 12px">'
    + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
    + '<tr><td align="center" style="padding:30px 24px 10px"><img src="' + REM_SITE + '/assets/presse/terrenurbanisme-logo.png" width="220" alt="TerrenUrbanisme" style="display:block;width:220px;max-width:70%;height:auto;border:0"></td></tr>'
    + '<tr><td style="padding:14px 22px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FBEEE8" style="border-radius:22px"><tr><td align="center" style="padding:30px 24px 10px;font-family:Arial,sans-serif">'
    + '<div style="font-size:28px;line-height:1.2;font-weight:bold;color:#2A1D17">Bonjour, voici votre remise de 15 %</div>'
    + (parc ? '<div style="margin-top:14px;display:inline-block;background:#FFFFFF;border:1px solid #F0D5C8;border-radius:10px;padding:8px 14px;font-size:14px;color:#2A1D17">' + parc + '</div>' : '')
    + btn('Activer ma remise de 15 %') + '</td></tr></table></td></tr>'
    + '<tr><td style="padding:10px 30px 0;font-family:Arial,sans-serif;font-size:16px;line-height:1.6;color:#2A1D17">'
    + '<p style="margin:0 0 14px">Vous bénéficiez d\'une <b>remise de 15 %</b> pour vérifier un terrain avec <b>TerrenUrbanisme</b> avant d\'acheter, de vendre ou de construire.</p>'
    + '<p style="margin:0 0 14px">Un terrain se paie des dizaines de milliers d\'euros. Une zone agricole, une servitude ou un risque découverts après la signature coûtent bien plus cher que leur vérification.</p></td></tr>'
    + '<tr><td style="padding:6px 22px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFF8EC" style="border-radius:20px"><tr><td style="padding:20px 22px;font-family:Arial,sans-serif;font-size:15px;line-height:1.55;color:#2A1D17"><b style="color:#A3462C">Notre engagement</b><br>Chaque information provient des sources officielles et est datée. Si une source ne répond pas au moment du rapport, nous le régénérons sans frais pendant 30 jours.</td></tr></table></td></tr>'
    + '<tr><td style="padding:22px 30px 0;font-family:Arial,sans-serif"><div style="font-size:21px;font-weight:bold;color:#2A1D17;margin-bottom:6px">Avec votre remise, découvrez :</div><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
    + li('La vraie zone du PLU,', 'pas celle de l\'annonce : un terrain vendu « constructible » peut être en zone agricole.')
    + li('Ce que vous pouvez construire :', 'surface, hauteur, reculs, emprise et implantation de la maison.')
    + li('Les risques et les servitudes :', 'inondation, argiles, monuments, lignes électriques, droit de préemption.')
    + li('Le juste prix :', 'les ventes réelles autour du terrain et le prix au m² de la commune.')
    + '</table>' + btn('Vérifier mon terrain avec −15 %')
    + '<p style="margin:0 0 6px;font-size:14px;color:#6E625A;text-align:center">Remise valable 14 jours, sur un rapport ou un lot de 2 ou 3 rapports.</p></td></tr>'
    + '<tr><td style="padding:22px 22px 6px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FBEEE8" style="border-radius:20px"><tr><td align="center" style="padding:24px;font-family:Arial,sans-serif;color:#2A1D17"><div style="font-size:19px;font-weight:bold">Une question ?</div><div style="font-size:15px;line-height:1.55;margin-top:8px">Répondez simplement à cet e-mail : nous vous répondons rapidement.<br>Ou consultez nos <a href="' + REM_SITE + '/faq.html" style="color:#A3462C;font-weight:bold">questions fréquentes</a>.</div></td></tr></table></td></tr>'
    + '<tr><td style="padding:16px 22px 26px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#A3462C" style="border-radius:20px"><tr><td align="center" style="padding:24px 20px;font-family:Arial,sans-serif;font-size:13px;line-height:1.7;color:#FBE4DC">'
    + '<a href="' + REM_SITE + '/confidentialite.html" style="color:#FFFFFF;font-weight:bold;text-decoration:none">Politique de confidentialité</a> &nbsp;·&nbsp; <a href="' + REM_SITE + '/cgv.html" style="color:#FFFFFF;font-weight:bold;text-decoration:none">Conditions générales de vente</a><br>'
    + 'Vous ne souhaitez plus recevoir nos e-mails ? <a href="' + des + '" style="color:#FFFFFF">Se désinscrire</a><br>TerrenUrbanisme · SIREN 898 332 473 · contact@terrenurbanisme.com</td></tr></table></td></tr>'
    + '</table></td></tr></table></body></html>';
  const txt = 'Bonjour,\n\nVoici votre remise de 15 % pour vérifier un terrain avec TerrenUrbanisme avant d\'acheter, de vendre ou de construire.\n' + (parc ? '\nVotre terrain : ' + r.commune + ' · section ' + r.section + ' · parcelle ' + r.numero + '\n' : '') + '\nActiver ma remise : ' + lien + '\n\nRemise valable 14 jours, sur un rapport ou un lot de 2 ou 3 rapports.\n\nUne question ? Répondez simplement à cet e-mail.\n\nSe désinscrire : ' + des + '\nTerrenUrbanisme · SIREN 898 332 473';
  return { html, txt, des };
}
async function remiseInscription(req: Request) {
  let b: any = {}; try { b = JSON.parse(await req.text()); } catch (e) { return jres({ error: 'format' }, 400); }
  const t = (v: any, n: number) => String(v == null ? '' : v).replace(/[\u0000-\u001f]+/g, ' ').trim().slice(0, n);
  if (t(b.site_web, 10)) return jres({ ok: true });
  const email = t(b.email, 120).toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(email)) return jres({ error: 'email' }, 400);
  const ip = t((req.headers.get('x-forwarded-for') || '').split(',')[0], 60);
  const depuis = new Date(Date.now() - 3600000).toISOString();
  const { count } = await admin.from('remises').select('id', { count: 'exact', head: true }).gte('created_at', depuis);
  if ((count || 0) >= 120) return jres({ error: 'limite' }, 429);
  if (ip) { const { count: c2 } = await admin.from('remises').select('id', { count: 'exact', head: true }).eq('ip', ip).gte('created_at', depuis); if ((c2 || 0) >= 5) return jres({ error: 'limite' }, 429); }
  const insee = /^(?:\d{2}|2[AB])\d{3}$/.test(t(b.insee, 5).toUpperCase()) ? t(b.insee, 5).toUpperCase() : null;
  const r: any = { email, ip, motif: t(b.motif, 20) || null, insee, section: insee ? t(b.section, 2).toUpperCase() : null, numero: insee ? t(b.numero, 4) : null, commune: insee ? t(b.commune, 80) : null };
  // Une remise en cours pour cette adresse : on renvoie la même, sans en créer une nouvelle
  const { data: ex } = await admin.from('remises').select('*').eq('email', email).is('utilise_le', null).gt('expire_le', new Date().toISOString()).order('created_at', { ascending: false }).limit(1).maybeSingle();
  let tk = ex && ex.token;
  if (!tk) {
    tk = crypto.randomUUID().replace(/-/g, '');
    const { error: ie } = await admin.from('remises').insert({ ...r, token: tk });
    if (ie) { console.error('remise', ie.message); return jres({ error: 'serveur' }, 500); }
  } else if (insee && !ex.insee) { await admin.from('remises').update({ insee: r.insee, section: r.section, numero: r.numero, commune: r.commune }).eq('token', tk); Object.assign(ex, r); }
  const m = remiseMail(tk, ex || r);
  try { await smtpSimple([email], 'Votre remise de 15 % sur votre rapport d\'urbanisme', m.txt, m.html); }
  catch (e) { console.error('remise mail', String((e as any)?.message || e).slice(0, 160)); return jres({ error: 'envoi' }, 502); }
  return jres({ ok: true });
}
async function remiseInfo(req: Request) {
  let b: any = {}; try { b = JSON.parse(await req.text()); } catch (e) { return jres({ error: 'format' }, 400); }
  const tk = String(b.r || '').replace(/[^a-f0-9]/gi, '').slice(0, 64);
  if (!tk) return jres({ ok: false });
  const { data: x } = await admin.from('remises').select('email, insee, section, numero, commune, motif, expire_le, utilise_le').eq('token', tk).maybeSingle();
  if (!x) return jres({ ok: false });
  if (b.desinscription) { await admin.from('remises').update({ desinscrit: true }).eq('email', x.email); return jres({ ok: true, desinscrit: true }); }
  const ok = !x.utilise_le && new Date(x.expire_le).getTime() > Date.now();
  return jres({ ok, utilise: !!x.utilise_le, email: x.email, insee: x.insee, section: x.section, numero: x.numero, commune: x.commune, motif: x.motif, expire_le: x.expire_le });
}
'''
rep("""async function handle(req) {
  const url = new URL(req.url);
""", FN + """async function handle(req) {
  const url = new URL(req.url);
  if (req.method === 'POST' && url.searchParams.get('remise') === '1') return await remiseInscription(req);
  if (req.method === 'POST' && url.searchParams.get('remise') === 'info') return await remiseInfo(req);
""")
# Paiement réussi avec une remise : la remise ne peut plus servir
a = "  if ((ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded') && o.metadata && (o.metadata.user_id || o.metadata.guest)"
rep(a, "  if ((ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded') && o.metadata && o.metadata.remise && o.payment_status === 'paid') { admin.from('remises').update({ utilise_le: new Date().toISOString(), session_id: o.id }).eq('token', String(o.metadata.remise)).is('utilise_le', null).then((x: any) => { if (x && x.error) console.error('remise utilisée', x.error.message); }); }\n" + a)
open(p, 'w', encoding='utf-8').write(s); print('patch remise appliqué')
