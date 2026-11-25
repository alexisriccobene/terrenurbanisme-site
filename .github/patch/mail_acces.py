# E-mail d'accès collaborateur : mise en page professionnelle et signature TerrenUrbanisme
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
i = s.index("  const txt = 'Bonjour ' + ag.nom + ',\\n\\n' + agence")
j = s.index("  try {\n    const client = new SMTPClient", i)
new = r"""  const pre = String(ag.nom).trim().split(/\s+/)[0] || ag.nom, H = v => String(v).replace(/[<>&]/g, '');
  const txt = 'Bonjour ' + pre + ',\n\n' + agence + ' vous a ouvert un accès personnel à TerrenUrbanisme, l\'outil de l\'agence pour établir vos rapports d\'urbanisme et vos avis de valeur.\n\nCréez votre accès (choix du mot de passe) : ' + lien + '\n\nVotre identifiant : ' + em + '\nEnsuite, connexion sur ' + SITE + '/connexion.html\n\nCe lien est personnel et valable une heure. Passé ce délai, demandez à votre agence de vous le renvoyer.\n\nBien cordialement,\nL\'équipe TerrenUrbanisme\ncontact@terrenurbanisme.com · terrenurbanisme.com';
  const html = `<!doctype html><html lang="fr"><body style="margin:0;background:#F9F2EE;font-family:Helvetica,Arial,sans-serif;color:#2A1D17">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F9F2EE;padding:32px 12px"><tr><td align="center">
<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#fff;border:1px solid #EFE6DF;border-radius:18px;overflow:hidden">
<tr><td style="background:#2A1D17;padding:22px 32px"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="vertical-align:middle"><img src="${SITE}/apple-touch-icon.png" width="36" height="36" alt="" style="display:block;border-radius:9px"></td><td style="vertical-align:middle;padding-left:12px;font-size:18px;font-weight:700;color:#F6EEE9">TerrenUrbanisme</td></tr></table></td></tr>
<tr><td style="padding:30px 32px 6px"><p style="margin:0 0 6px;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#A3462C">Accès collaborateur · ${H(agence)}</p>
<h1 style="font-size:23px;line-height:1.3;margin:0 0 16px">Bienvenue ${H(pre)}, votre accès est prêt</h1>
<p style="font-size:15px;line-height:1.65;margin:0 0 18px"><strong>${H(agence)}</strong> vous a ouvert un accès personnel à TerrenUrbanisme, l'outil de l'agence pour établir vos rapports d'urbanisme et vos avis de valeur.</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background:#FBF3EF;border-radius:12px"><tr><td style="padding:16px 18px;font-size:14px;line-height:1.7">
&#10003;&nbsp; Vos rapports sont établis <strong>à votre nom</strong>, avec votre photo et vos coordonnées<br>
&#10003;&nbsp; Ils sont décomptés sur les crédits de l'agence<br>
&#10003;&nbsp; Vous suivez vos envois et savez quand vos clients ouvrent leur rapport</td></tr></table>
<p style="margin:0 0 10px"><a href="${lien}" style="display:inline-block;background:#A3462C;color:#fff;text-decoration:none;font-weight:700;font-size:16px;padding:14px 26px;border-radius:12px">Créer mon accès</a></p>
<p style="font-size:13px;line-height:1.6;color:#6E625A;margin:0 0 20px">Vous choisissez votre mot de passe et arrivez directement sur votre tableau de bord.</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;border-top:1px solid #EFE6DF;border-bottom:1px solid #EFE6DF"><tr><td style="padding:12px 0;font-size:14px;color:#6E625A">Votre identifiant</td><td align="right" style="padding:12px 0;font-size:14px;font-weight:700">${H(em)}</td></tr></table>
<p style="font-size:12.5px;line-height:1.6;color:#8A7D74;margin:0 0 22px">Ce lien est personnel et valable une heure. Passé ce délai, demandez à votre agence de vous le renvoyer depuis son espace.</p>
<p style="font-size:15px;line-height:1.6;margin:0 0 4px">Bien cordialement,</p>
<p style="font-size:15px;line-height:1.5;margin:0 0 26px"><strong>L'équipe TerrenUrbanisme</strong><br><span style="font-size:13.5px;color:#6E625A">Rapports d'urbanisme et avis de valeur pour les professionnels de l'immobilier</span></p></td></tr>
<tr><td style="padding:18px 32px 24px;background:#FBF8F6;border-top:1px solid #EFE6DF;font-size:12.5px;line-height:1.7;color:#8A7D74"><a href="${SITE}" style="color:#A3462C;font-weight:700;text-decoration:none">terrenurbanisme.com</a> · <a href="mailto:contact@terrenurbanisme.com" style="color:#8A7D74">contact@terrenurbanisme.com</a><br>TerrenUrbanisme · SIREN 898 332 473</td></tr>
</table></td></tr></table></body></html>`;
"""
s = s[:i] + new + s[j:]
s = s.replace("subject: 'Votre accès TerrenUrbanisme · ' + agence", "subject: pre + ', votre accès TerrenUrbanisme est prêt · ' + agence")
open(p, 'w', encoding='utf-8').write(s); print('patch mail accès appliqué')
