# Collaborateur : modifier son profil (nom, téléphone, e-mail, photo) et demander des crédits à l'agence
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("  if (b.action === 'agent_acces') return await agentAcces(u.user, b);",
r"""  if (b.action === 'agent_acces') return await agentAcces(u.user, b);
  if (b.action === 'membre_profil') {
    if (!mbr) return jres({ error: 'membre' }, 403);
    const t = v => String(v == null ? '' : v).replace(/[<>]/g, '').trim();
    const nom = t(b.nom).slice(0, 80), row = { telephone: t(b.telephone).slice(0, 30) || null, email: t(b.email).slice(0, 120) || null };
    if (nom.length >= 2) row.nom = nom;
    if (b.photo && /^data:image\/jpeg;base64,/.test(String(b.photo)) && String(b.photo).length < 1500000) {
      const bin = atob(String(b.photo).split(',')[1]), by = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) by[i] = bin.charCodeAt(i);
      const path = mbr.user_id + '/agents/' + mbr.id + '-' + Date.now() + '.jpg';
      const up = await admin.storage.from('perso').upload(path, by, { contentType: 'image/jpeg' });
      if (!up.error) row.photo = path;
    }
    const { error: pe } = await admin.from('pro_agents').update(row).eq('id', mbr.id);
    if (pe) { console.error('profil membre', pe); return jres({ error: 'profil' }, 500); }
    // Nouveau nom : les rapports déjà établis restent rattachés au collaborateur
    if (row.nom && row.nom !== mbr.nom) await admin.from('dossiers').update({ agent: row.nom }).eq('user_id', mbr.user_id).eq('agent', mbr.nom);
    return jres({ ok: true, nom: row.nom || mbr.nom, photo: !!row.photo });
  }
  if (b.action === 'demande_credits') {
    if (!mbr) return jres({ error: 'membre' }, 403);
    const { data: ag } = await admin.from('pro_agents').select('demande_le').eq('id', mbr.id).maybeSingle();
    if (ag && ag.demande_le && Date.now() - new Date(ag.demande_le).getTime() < 3600000) return jres({ ok: true, deja: true });
    const to = await userEmail(mbr.user_id); if (!to) return jres({ error: 'agence' }, 500);
    const { data: mq } = await admin.from('marques').select('nom').eq('user_id', mbr.user_id).maybeSingle();
    const agence = (mq && mq.nom) || 'votre agence', H = v => String(v).replace(/[<>&]/g, ''), lien = SITE + '/tarifs.html#plans';
    const txt = 'Bonjour,\n\n' + mbr.nom + ', collaborateur de ' + agence + ', n\'a plus de crédits pour établir ses rapports d\'urbanisme et vous demande d\'en ajouter.\n\nAcheter des crédits : ' + lien + '\n\nDès votre achat, il peut reprendre son travail.\n\nBien cordialement,\nL\'équipe TerrenUrbanisme\ncontact@terrenurbanisme.com · terrenurbanisme.com';
    const html = `<!doctype html><html lang="fr"><body style="margin:0;background:#F9F2EE;font-family:Helvetica,Arial,sans-serif;color:#2A1D17"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F9F2EE;padding:32px 12px"><tr><td align="center"><table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#fff;border:1px solid #EFE6DF;border-radius:18px;overflow:hidden">
<tr><td style="background:#2A1D17;padding:22px 32px"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td><img src="${SITE}/apple-touch-icon.png" width="36" height="36" alt="" style="display:block;border-radius:9px"></td><td style="padding-left:12px;font-size:18px;font-weight:700;color:#F6EEE9">TerrenUrbanisme</td></tr></table></td></tr>
<tr><td style="padding:30px 32px 6px"><p style="margin:0 0 6px;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#A3462C">Demande de crédits · ${H(agence)}</p><h1 style="font-size:23px;line-height:1.3;margin:0 0 16px">${H(mbr.nom)} n'a plus de crédits</h1>
<p style="font-size:15px;line-height:1.65;margin:0 0 22px">Votre collaborateur <strong>${H(mbr.nom)}</strong> souhaite établir de nouveaux rapports d'urbanisme, mais les crédits de l'agence sont épuisés. Ajoutez des crédits pour qu'il puisse reprendre son travail.</p>
<p style="margin:0 0 22px"><a href="${lien}" style="display:inline-block;background:#A3462C;color:#fff;text-decoration:none;font-weight:700;font-size:16px;padding:14px 26px;border-radius:12px">Acheter des crédits</a></p>
<p style="font-size:13px;line-height:1.6;color:#6E625A;margin:0 0 22px">Crédits sans limite de durée, ou abonnement mensuel sans engagement. Les crédits sont partagés entre tous vos collaborateurs.</p>
<p style="font-size:15px;line-height:1.6;margin:0 0 4px">Bien cordialement,</p><p style="font-size:15px;line-height:1.5;margin:0 0 26px"><strong>L'équipe TerrenUrbanisme</strong></p></td></tr>
<tr><td style="padding:18px 32px 24px;background:#FBF8F6;border-top:1px solid #EFE6DF;font-size:12.5px;line-height:1.7;color:#8A7D74"><a href="${SITE}" style="color:#A3462C;font-weight:700;text-decoration:none">terrenurbanisme.com</a> · contact@terrenurbanisme.com<br>TerrenUrbanisme · SIREN 898 332 473</td></tr></table></td></tr></table></body></html>`;
    try { await smtpSimple([to], mbr.nom + ' vous demande des crédits TerrenUrbanisme', txt, html); } catch (e) { console.error('demande crédits', String(e && e.message || e)); return jres({ error: 'mail' }, 502); }
    await admin.from('pro_agents').update({ demande_le: new Date().toISOString() }).eq('id', mbr.id);
    return jres({ ok: true });
  }""")
# Photo du conseiller : accepte les photos rangées dans le dossier de l'agence
rep("        if (ag.photo && String(ag.photo).startsWith(dos.user_id + '/')) {", "        if (ag.photo && /^[0-9a-f-]{36}\\/agents\\//.test(String(ag.photo))) {")
open(p, 'w', encoding='utf-8').write(s); print('patch profil membre appliqué')
