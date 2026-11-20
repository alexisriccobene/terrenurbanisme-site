# Accès collaborateur : lien direct « Créer mon accès » (choix du mot de passe en un clic, puis tableau de bord)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("  const lien = SITE + '/connexion.html?mode=premier';",
r"""  let lien = SITE + '/connexion.html?mode=premier';
  try {
    const rl = await admin.auth.admin.generateLink({ type: 'recovery', email: em, options: { redirectTo: SITE + '/connexion.html?nouveau=1&redirect=' + encodeURIComponent('/espace.html') } });
    if (rl.data && rl.data.properties && rl.data.properties.action_link) lien = rl.data.properties.action_link;
  } catch (e) { console.warn('lien accès', String(e && e.message || e).slice(0, 120)); }""")
rep(r"""\n\n1. Ouvrez ce lien : ' + lien + '\n2. Indiquez votre adresse e-mail : ' + em + '\n3. Choisissez votre mot de passe avec le lien reçu.\n\nTerrenUrbanisme';""",
    r"""\n\nCréez votre accès en choisissant votre mot de passe : ' + lien + '\n\nVous vous connecterez ensuite avec ' + em + ' et votre mot de passe sur ' + SITE + '/connexion.html\n\nTerrenUrbanisme';""")
rep(r"""Créer mon mot de passe</a></p><p style="color:#6E625A;font-size:13px">Indiquez l\'adresse ' + em + ', puis suivez le lien reçu pour choisir votre mot de passe.</p></div>';""",
    r"""Créer mon accès</a></p><p style="color:#6E625A;font-size:13px">Vous choisissez votre mot de passe et arrivez directement sur votre tableau de bord. Ensuite, connectez-vous avec ' + em + ' sur terrenurbanisme.com.</p></div>';""")
rep("subject: agence + ' vous a créé un accès TerrenUrbanisme'", "subject: 'Votre accès TerrenUrbanisme · ' + agence")
open(p, 'w', encoding='utf-8').write(s); print('patch membres2 appliqué')
