# E-mail de remise : nouvelle mise en page (parcelle en 3 cases, pied de page sobre)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index('function remiseMail(tk: string, r: any) {'); b = s.index('\nasync function remiseInscription', a)
NEW = r'''function remiseMail(tk: string, r: any) {
  const lien = REM_SITE + '/offre.html?r=' + encodeURIComponent(tk);
  const des = REM_SITE + '/desinscription.html?r=' + encodeURIComponent(tk);
  const F = 'font-family:Helvetica,Arial,sans-serif;';
  const T = '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"';
  let fin = '';
  try { if (r.expire_le) fin = new Date(r.expire_le).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', timeZone: 'Europe/Paris' }); } catch (e) {}
  const cell = (k: string, v: string, w: string) => '<td width="' + w + '" align="center" valign="top" style="padding:14px 6px;' + (w !== '46%' ? 'border-left:1px solid #EBD5CB;' : '') + F + '"><div style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#9A8A80;font-weight:bold">' + k + '</div><div style="margin-top:6px;font-size:19px;line-height:1.2;font-weight:bold;color:#2A1D17">' + v + '</div></td>';
  const parc = r.commune && r.section && r.numero
    ? '<tr><td style="padding:0 28px 6px">' + T + ' style="border:1px solid #EBD5CB;border-radius:16px;background:#FFFFFF"><tr>' + cell('Commune', escH(r.commune), '46%') + cell('Section', escH(r.section), '27%') + cell('Parcelle', escH(r.numero), '27%') + '</tr></table></td></tr>' : '';
  const btn = (t: string) => T + ' style="margin:22px 0 6px"><tr><td align="center" bgcolor="#A3462C" style="border-radius:999px"><a href="' + lien + '" style="display:block;padding:17px 22px;' + F + 'font-size:17px;font-weight:bold;color:#FFFFFF;text-decoration:none;border-radius:999px">' + t + '</a></td></tr></table>';
  const li = (t: string, d: string) => '<tr><td width="34" valign="top" style="padding:12px 0 12px"><div style="width:24px;height:24px;border-radius:12px;background:#FBEEE8;color:#A3462C;' + F + 'font-size:13px;font-weight:bold;line-height:24px;text-align:center">&#10003;</div></td><td style="padding:12px 0;border-bottom:1px solid #F3E6E0;' + F + 'font-size:15px;line-height:1.5;color:#5C4E46"><b style="color:#2A1D17">' + t + '</b><br>' + d + '</td></tr>';
  const lk = 'color:#A3462C;text-decoration:none;font-weight:bold';
  const html = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="x-apple-disable-message-reformatting"><meta name="format-detection" content="telephone=no,address=no,email=no"><title>Votre remise de 15 %</title></head><body style="margin:0;padding:0;background:#F4EFEC">'
    + '<div style="display:none;max-height:0;overflow:hidden">Votre remise de 15 % sur le rapport d\'urbanisme de votre terrain' + (fin ? ', valable jusqu\'au ' + fin : '') + '.</div>'
    + T + ' bgcolor="#F4EFEC"><tr><td align="center" style="padding:28px 12px">'
    + T + ' style="max-width:600px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
    + '<tr><td align="center" style="padding:30px 24px 6px"><img src="' + REM_SITE + '/assets/presse/terrenurbanisme-logo.png" width="190" alt="TerrenUrbanisme" style="display:block;width:190px;max-width:60%;height:auto;border:0"></td></tr>'
    + '<tr><td align="center" style="padding:22px 28px 0;' + F + '">'
    + '<div style="display:inline-block;background:#FBEEE8;color:#A3462C;border-radius:999px;padding:6px 14px;font-size:12px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase">Remise de bienvenue</div>'
    + '<div style="margin-top:14px;font-size:64px;line-height:1;font-weight:bold;color:#A3462C;letter-spacing:-2px">&minus;15&nbsp;%</div>'
    + '<div style="margin-top:12px;font-size:24px;line-height:1.25;font-weight:bold;color:#2A1D17">Votre remise est prête</div>'
    + '<div style="margin:10px auto 22px;max-width:440px;font-size:15px;line-height:1.55;color:#6E625A">Sur le rapport d\'urbanisme complet de votre terrain, ou sur un lot de 2 ou 3 rapports.</div></td></tr>'
    + parc
    + '<tr><td style="padding:0 28px">' + btn('Activer ma remise') + '<div style="' + F + 'font-size:13px;color:#9A8A80;text-align:center">' + (fin ? 'Valable jusqu\'au ' + fin + ' · une seule utilisation' : 'Valable 14 jours · une seule utilisation') + '</div></td></tr>'
    + '<tr><td style="padding:30px 28px 0"><div style="height:1px;background:#F0E3DC;font-size:0;line-height:0">&nbsp;</div></td></tr>'
    + '<tr><td style="padding:26px 28px 0;' + F + '"><div style="font-size:19px;font-weight:bold;color:#2A1D17">Ce que vous saurez avant de signer</div>'
    + T + ' style="margin-top:6px">'
    + li('La vraie zone du PLU', 'Pas celle de l\'annonce : un terrain vendu « constructible » peut être en zone agricole.')
    + li('Ce que vous pouvez construire', 'Surface, hauteur, reculs, emprise et implantation de la maison.')
    + li('Les risques et les servitudes', 'Inondation, argiles, monuments, lignes électriques, droit de préemption.')
    + li('Le juste prix', 'Les ventes réelles autour du terrain et le prix au m² de la commune.')
    + '</table></td></tr>'
    + '<tr><td style="padding:22px 28px 0">' + T + ' bgcolor="#FBEEE8" style="border-radius:16px"><tr><td style="padding:18px 20px;' + F + 'font-size:14px;line-height:1.55;color:#5C4E46"><b style="color:#2A1D17">Des données officielles et datées.</b> Si une source ne répond pas au moment du rapport, nous le régénérons sans frais pendant 30 jours.</td></tr></table></td></tr>'
    + '<tr><td style="padding:4px 28px 30px">' + btn('Vérifier mon terrain à −15 %') + '</td></tr>'
    + '</table>'
    + T + ' style="max-width:600px"><tr><td align="center" style="padding:24px 20px 8px;' + F + 'font-size:13px;line-height:1.8;color:#8A7B72">'
    + '<div style="font-size:14px;color:#2A1D17;font-weight:bold">Une question ?</div><div>Répondez simplement à cet e-mail, ou écrivez-nous :</div>'
    + '<div><a href="mailto:contact@terrenurbanisme.com" style="' + lk + '">contact@terrenurbanisme.com</a></div><div><a href="' + REM_SITE + '" style="' + lk + '">terrenurbanisme.com</a></div>'
    + '<div style="margin-top:14px"><a href="' + REM_SITE + '/faq.html" style="color:#8A7B72;text-decoration:underline">Questions fréquentes</a> &nbsp;·&nbsp; <a href="' + REM_SITE + '/confidentialite.html" style="color:#8A7B72;text-decoration:underline">Confidentialité</a> &nbsp;·&nbsp; <a href="' + REM_SITE + '/cgv.html" style="color:#8A7B72;text-decoration:underline">CGV</a></div>'
    + '<div style="margin-top:6px">TerrenUrbanisme · SIREN 898 332 473</div>'
    + '<div style="margin-top:6px">Vous ne souhaitez plus recevoir nos e-mails ? <a href="' + des + '" style="color:#8A7B72;text-decoration:underline">Se désinscrire</a></div>'
    + '</td></tr></table>'
    + '</td></tr></table></body></html>';
  const txt = 'Bonjour,\n\nVotre remise de 15 % est prête, sur le rapport d\'urbanisme complet de votre terrain ou sur un lot de 2 ou 3 rapports.\n' + (r.commune && r.section && r.numero ? '\nCommune : ' + r.commune + '\nSection : ' + r.section + '\nParcelle : ' + r.numero + '\n' : '') + '\nActiver ma remise : ' + lien + '\n\n' + (fin ? 'Valable jusqu\'au ' + fin + ', une seule utilisation.' : 'Valable 14 jours, une seule utilisation.') + '\n\nUne question ? Répondez simplement à cet e-mail.\ncontact@terrenurbanisme.com\n\nSe désinscrire : ' + des + '\nTerrenUrbanisme · SIREN 898 332 473';
  return { html, txt, des };
}'''
s = s[:a] + NEW + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('patch remise_mail2 appliqué')
