# Espace mairie : identité de la commune modifiable (logo, adresse, téléphone, e-mail, site), alerte e-mail quand il reste 10 rapports
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("logo: V.logo_url || null, centre: V.centre || null };",
    "logo: V.logo_url || null, centre: V.centre || null, adresse: V.adresse || null, telephone: V.telephone || null, email: V.email_contact || null, site: V.site || null };")
rep("  if (b.action === 'demo_lien') {",
r"""  if (b.action === 'profil') {
    if (!V.cle_espace || !safeEq(String(b.k || ''), V.cle_espace)) return jres({ error: 'cle' }, 403);
    const T = (v, n) => String(v == null ? '' : v).replace(/[<>]/g, '').trim().slice(0, n) || null;
    const up = { adresse: T(b.adresse, 200), telephone: T(b.telephone, 30), email_contact: T(b.email, 160), site: T(b.site, 200) };
    if (up.email_contact && !/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(up.email_contact)) return jres({ error: 'email' }, 400);
    if (b.logo === null) { up.logo_url = null; up.logo_path = null; }
    else if (typeof b.logo === 'string' && b.logo) {
      const m = b.logo.match(/^data:image\/(png|jpeg);base64,([A-Za-z0-9+/=]+)$/);
      if (!m || m[2].length > 700000) return jres({ error: 'logo' }, 400);
      const bytes = Uint8Array.from(atob(m[2]), c => c.charCodeAt(0)), ext = m[1] === 'png' ? 'png' : 'jpg';
      const path = 'villes/' + V.slug + '-' + Date.now() + '.' + ext;
      const { error: ue } = await admin.storage.from('logos').upload(path, bytes, { contentType: 'image/' + m[1], upsert: true });
      if (ue) { console.error('logo commune', ue.message); return jres({ error: 'logo' }, 500); }
      up.logo_path = path; up.logo_url = b.logo;
    }
    if (V.demo && (b.formule_demo === 'credits' || b.formule_demo === 'abo')) up.credits = b.formule_demo === 'credits' ? 9 : null;
    const { error: e2 } = await admin.from('villes').update(up).eq('slug', V.slug);
    if (e2) { console.error('profil commune', e2.message); return jres({ error: 'maj' }, 500); }
    return jres({ ok: true });
  }
  if (b.action === 'demo_lien') {""")
rep("if (re || reste == null) return jres({ error: 'credits_epuises' }, 402); }",
    "if (re || reste == null) return jres({ error: 'credits_epuises' }, 402); if (reste === 10 || reste === 0) alerteStockVille(V, reste); }")
rep("async function villeCfg(slug) {",
r"""// Stock de rapports de la commune : e-mail automatique quand il reste 10 rapports, puis quand il est épuisé
async function alerteStockVille(V, reste) {
  try {
    const to = [V.email_contact].concat(V.emails_notif || []).map(x => String(x || '').trim().toLowerCase()).filter((x, i, a) => /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/.test(x) && a.indexOf(x) === i);
    if (!to.length) { console.warn('stock commune : aucune adresse', V.slug); return; }
    const H = v => String(v).replace(/[<>&]/g, ''), lib = 'Mairie de ' + V.nom, lien = SITE + '/mairies.html#offre', esp = SITE + '/espace-mairie.html';
    const t1 = reste ? 'Il ne vous reste plus que ' + reste + ' rapports' : 'Votre stock de rapports est épuisé';
    const t2 = reste ? 'Votre espace mairie affiche 10 rapports restants. Pensez à recharger votre stock pour que vos habitants puissent continuer à analyser leur terrain depuis le site de la commune.' : 'Vos habitants ne peuvent plus obtenir leur rapport d\'urbanisme depuis le site de la commune. Rechargez votre stock pour rétablir le service.';
    const txt = 'Bonjour,\n\n' + t1 + ' sur votre espace mairie TerrenUrbanisme.\n\n' + t2 + '\n\nRecharger le stock : ' + lien + '\nVotre espace mairie : ' + esp + '\n\nBien cordialement,\nL\'équipe TerrenUrbanisme\ncontact@terrenurbanisme.com · terrenurbanisme.com';
    const html = `<!doctype html><html lang="fr"><body style="margin:0;background:#F9F2EE;font-family:Helvetica,Arial,sans-serif;color:#2A1D17"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F9F2EE;padding:32px 12px"><tr><td align="center"><table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#fff;border:1px solid #EFE6DF;border-radius:18px;overflow:hidden">
<tr><td style="background:#2A1D17;padding:22px 32px"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td><img src="${SITE}/apple-touch-icon.png" width="36" height="36" alt="" style="display:block;border-radius:9px"></td><td style="padding-left:12px;font-size:18px;font-weight:700;color:#F6EEE9">TerrenUrbanisme</td></tr></table></td></tr>
<tr><td style="padding:30px 32px 6px"><p style="margin:0 0 6px;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#A3462C">Stock de rapports · ${H(lib)}</p><h1 style="font-size:23px;line-height:1.3;margin:0 0 16px">${H(t1)}</h1>
<p style="font-size:15px;line-height:1.65;margin:0 0 4px">Bonjour,</p><p style="font-size:15px;line-height:1.65;margin:0 0 22px">${H(t2)}</p>
<p style="margin:0 0 14px"><a href="${lien}" style="display:inline-block;background:#A3462C;color:#fff;text-decoration:none;font-weight:700;font-size:16px;padding:14px 26px;border-radius:12px">Recharger le stock</a></p>
<p style="font-size:13.5px;line-height:1.6;margin:0 0 22px"><a href="${esp}" style="color:#A3462C;font-weight:700">Ouvrir votre espace mairie</a></p>
<p style="font-size:15px;line-height:1.6;margin:0 0 4px">Bien cordialement,</p><p style="font-size:15px;line-height:1.5;margin:0 0 26px"><strong>L'équipe TerrenUrbanisme</strong></p></td></tr>
<tr><td style="padding:18px 32px 24px;background:#FBF8F6;border-top:1px solid #EFE6DF;font-size:12.5px;line-height:1.7;color:#8A7D74"><a href="${SITE}" style="color:#A3462C;font-weight:700;text-decoration:none">terrenurbanisme.com</a> · contact@terrenurbanisme.com<br>TerrenUrbanisme · SIREN 898 332 473</td></tr></table></td></tr></table></body></html>`;
    await smtpSimple(to, reste ? lib + ' : plus que ' + reste + ' rapports disponibles' : lib + ' : stock de rapports épuisé', txt, html);
  } catch (e) { console.error('alerte stock commune', String(e && e.message || e)); }
}
async function villeCfg(slug) {""")
open(p, 'w', encoding='utf-8').write(s); print('patch mairie profil appliqué')
