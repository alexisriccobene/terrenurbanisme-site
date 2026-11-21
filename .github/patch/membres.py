# Accès individuels des collaborateurs : chaque agent a son compte, ses rapports sont signés à son nom et décomptés sur les crédits de l'agence
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)

rep("function demoIllimite(user) { const em = String(user && user.email || '').toLowerCase(); return !!em && DEMO_COMPTES.includes(em); }",
    "function demoIllimite(user) { if (user && user.__demo === true) return true; const em = String(user && user.email || '').toLowerCase(); return !!em && DEMO_COMPTES.includes(em); }")

rep("""  const b = await req.json().catch(() => ({}));
  if (b.action === 'redeem') return await redeemInvite(u.user, String(b.code || ''));""",
r"""  const b = await req.json().catch(() => ({}));
  // Collaborateur d'une agence : agit pour l'agence, sous son propre nom
  const { data: mbr } = await admin.from('pro_agents').select('id, user_id, nom').eq('member_id', u.user.id).limit(1).maybeSingle();
  let uu = u;
  if (mbr) {
    const oem = await userEmail(mbr.user_id);
    uu = { user: { ...u.user, id: mbr.user_id, __demo: demoIllimite({ email: oem }) } };
  }
  if (b.action === 'mon_agence') {
    if (!mbr) return jres({ agence: null });
    const [{ data: mq }, { data: cp }] = await Promise.all([admin.from('marques').select('nom').eq('user_id', mbr.user_id).maybeSingle(), admin.from('comptes').select('credits_abonnement, credits_achetes, statut_abonnement').eq('user_id', mbr.user_id).maybeSingle()]);
    const sub = cp && ['active', 'trialing'].includes(cp.statut_abonnement || '');
    return jres({ agence: (mq && mq.nom) || 'Votre agence', owner: mbr.user_id, nom: mbr.nom, illimite: uu.user.__demo === true, total: cp ? (sub ? (cp.credits_abonnement || 0) : 0) + (cp.credits_achetes || 0) : 0 });
  }
  if (b.action === 'agent_acces') return await agentAcces(u.user, b);
  if (mbr && (b.action === 'personnaliser' || b.action === 'apercu_dossier')) {
    const { data: dz } = await admin.from('dossiers').select('user_id, agent').eq('id', String(b.id || '')).maybeSingle();
    if (!dz || dz.user_id !== mbr.user_id || dz.agent !== mbr.nom) return jres({ error: 'dossier' }, 404);
    b.__px = u.user.id;
  }
  if (b.action === 'redeem') return await redeemInvite(u.user, String(b.code || ''));""")
rep("  if (b.action === 'personnaliser') return await personnaliser(u.user, b);", "  if (b.action === 'personnaliser') return await personnaliser(uu.user, b);")
rep("    if (!dos || dos.user_id !== u.user.id || !dos.pdf_path) return jres({ error: 'dossier' }, 404);", "    if (!dos || dos.user_id !== uu.user.id || !dos.pdf_path) return jres({ error: 'dossier' }, 404);")
rep("  return await generateWithCredit(u, b);\n}", "  if (mbr) b.agent = mbr.nom;\n  return await generateWithCredit(uu, b);\n}")

# Photos envoyées par le collaborateur (dossier de stockage à son nom)
rep("    if (!path.startsWith(user.id + '/')) continue;", "    if (!path.startsWith(user.id + '/') && !(b.__px && path.startsWith(b.__px + '/'))) continue;")
rep("photos: (b.photos || []).filter(x => String(x || '').startsWith(user.id + '/')).slice(0, 8),", "photos: (b.photos || []).filter(x => String(x || '').startsWith(user.id + '/') || (b.__px && String(x || '').startsWith(b.__px + '/'))).slice(0, 8),")
rep("    if (!String(path).startsWith(dos.user_id + '/')) continue;", "    if (!/^[0-9a-f-]{36}\\//.test(String(path))) continue;")

# Création de l'accès d'un collaborateur par l'agence
rep("// ---------- Essai offert : lien d'invitation", r"""// ---------- Accès individuel d'un collaborateur (créé par l'agence) ----------
async function agentAcces(owner, b) {
  const { data: ag } = await admin.from('pro_agents').select('id, user_id, nom, email, member_id').eq('id', b.agent_id).maybeSingle();
  if (!ag || ag.user_id !== owner.id) return jres({ error: 'agent' }, 404);
  const em = String(ag.email || '').trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) return jres({ error: 'email' }, 400);
  if (em === String(owner.email || '').toLowerCase()) return jres({ error: 'email_agence' }, 400);
  let mid = null;
  const cr = await admin.auth.admin.createUser({ email: em, email_confirm: true });
  if (cr.data && cr.data.user) mid = cr.data.user.id;
  else {
    const gl = await admin.auth.admin.generateLink({ type: 'magiclink', email: em });
    mid = gl.data && gl.data.user && gl.data.user.id;
  }
  if (!mid) return jres({ error: 'compte' }, 500);
  const { data: deja } = await admin.from('pro_agents').select('id, user_id').eq('member_id', mid).maybeSingle();
  if (deja && deja.id !== ag.id) return jres({ error: 'deja_membre' }, 409);
  await admin.from('pro_agents').update({ member_id: mid, acces_le: new Date().toISOString() }).eq('id', ag.id);
  const { data: mq } = await admin.from('marques').select('nom').eq('user_id', owner.id).maybeSingle();
  const agence = (mq && mq.nom) || 'Votre agence';
  const lien = SITE + '/connexion.html?mode=premier';
  const txt = 'Bonjour ' + ag.nom + ',\n\n' + agence + ' vous a créé un accès personnel à TerrenUrbanisme.\n\nVos rapports d\'urbanisme seront établis à votre nom et décomptés sur les crédits de l\'agence.\n\n1. Ouvrez ce lien : ' + lien + '\n2. Indiquez votre adresse e-mail : ' + em + '\n3. Choisissez votre mot de passe avec le lien reçu.\n\nTerrenUrbanisme';
  const html = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6;color:#2A1D17"><p>Bonjour ' + ag.nom.replace(/</g, '') + ',</p><p><strong>' + agence.replace(/</g, '') + '</strong> vous a créé un accès personnel à TerrenUrbanisme.</p><p>Vos rapports d\'urbanisme seront établis à votre nom et décomptés sur les crédits de l\'agence.</p><p><a href="' + lien + '" style="display:inline-block;background:#A3462C;color:#fff;text-decoration:none;font-weight:700;padding:12px 20px;border-radius:10px">Créer mon mot de passe</a></p><p style="color:#6E625A;font-size:13px">Indiquez l\'adresse ' + em + ', puis suivez le lien reçu pour choisir votre mot de passe.</p></div>';
  try {
    const client = new SMTPClient({ connection: { hostname: Deno.env.get('SMTP_HOST') || 'ssl0.ovh.net', port: Number(Deno.env.get('SMTP_PORT') || '465'), tls: true, auth: { username: Deno.env.get('SMTP_USER') || 'contact@terrenurbanisme.com', password: Deno.env.get('SMTP_PASSWORD') } } });
    let coupe = false;
    try { await client.send({ from: 'TerrenUrbanisme <' + (Deno.env.get('SMTP_USER') || 'contact@terrenurbanisme.com') + '>', to: em, subject: agence + ' vous a créé un accès TerrenUrbanisme', mimeContent: mimeParts(txt, html) }); }
    catch (e) { if (/close_notify|UnexpectedEof/i.test(String(e && e.message || e))) coupe = true; else throw e; }
    finally { if (!coupe) { try { await client.close(); } catch (e) {} } }
  } catch (e) { console.error('accès agent', e); return jres({ ok: true, mail: false }); }
  return jres({ ok: true, mail: true });
}
// ---------- Essai offert : lien d'invitation""")
open(p, 'w', encoding='utf-8').write(s); print('patch membres appliqué')
