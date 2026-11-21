# Abonnements corrélés aux crédits : 10/50/100/250/500 rapports par mois (39/175/299/690/1190 €), annuel = 10 mois pour 12.
# Rapports non utilisés reportés sur le mois suivant uniquement.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("const PLAN_CREDITS = { essentiel: 15, pro: 50, cabinet: 150, essentiel_an: 180, pro_an: 600, cabinet_an: 1800 };",
    "const PLAN_CREDITS = { essentiel: 15, pro: 50, cabinet: 150, essentiel_an: 180, pro_an: 600, cabinet_an: 1800, ab10: 10, ab50: 50, ab100: 100, ab250: 250, ab500: 500, ab10_an: 120, ab50_an: 600, ab100_an: 1200, ab250_an: 3000, ab500_an: 6000 };")
rep("const PLAN_LABEL = { essentiel: 'Solo', pro: 'Agence', cabinet: 'Réseau', essentiel_an: 'Solo annuel', pro_an: 'Agence annuel', cabinet_an: 'Réseau annuel' };",
    "const PLAN_LABEL = { essentiel: 'Solo', pro: 'Agence', cabinet: 'Réseau', essentiel_an: 'Solo annuel', pro_an: 'Agence annuel', cabinet_an: 'Réseau annuel', ab10: '10 rapports par mois', ab50: '50 rapports par mois', ab100: '100 rapports par mois', ab250: '250 rapports par mois', ab500: '500 rapports par mois', ab10_an: '10 rapports par mois (annuel)', ab50_an: '50 rapports par mois (annuel)', ab100_an: '100 rapports par mois (annuel)', ab250_an: '250 rapports par mois (annuel)', ab500_an: '500 rapports par mois (annuel)' };")
rep("const PLAN_PRIX_AN = { essentiel_an: 290, pro_an: 550, cabinet_an: 1390 };",
    "const PLAN_PRIX_AN = { essentiel_an: 290, pro_an: 550, cabinet_an: 1390, ab10_an: 390, ab50_an: 1750, ab100_an: 2990, ab250_an: 6900, ab500_an: 11900 };")
rep(".in('formule', ['essentiel_an', 'pro_an', 'cabinet_an'])", ".in('formule', ['essentiel_an', 'pro_an', 'cabinet_an', 'ab10_an', 'ab50_an', 'ab100_an', 'ab250_an', 'ab500_an'])")
rep("""  // Les rapports de l'abonnement sont remis au nombre prévu par la formule à chaque période (sans report)
  await crediter(userId, 'abonnement', PLAN_CREDITS[formule], (inv.billing_reason === 'subscription_create' ? 'Souscription ' : 'Renouvellement ') + PLAN_LABEL[formule], inv.id, true);""",
"""  // Rapports de la période ; formules mensuelles : les rapports non utilisés du mois précédent sont reportés une seule fois
  let dotation = PLAN_CREDITS[formule];
  if (/^ab\\d+$/.test(formule) && inv.billing_reason !== 'subscription_create') {
    const { data: cpt } = await admin.from('comptes').select('credits_abonnement').eq('user_id', userId).maybeSingle();
    dotation += Math.min(Math.max(0, Number(cpt && cpt.credits_abonnement) || 0), PLAN_CREDITS[formule]);
  }
  await crediter(userId, 'abonnement', dotation, (inv.billing_reason === 'subscription_create' ? 'Souscription ' : 'Renouvellement ') + PLAN_LABEL[formule], inv.id, true);""")
rep("    await upsertCompte(m.user_id, { stripe_subscription: s.subscription, formule: m.kind, statut_abonnement: 'active', resiliation_prevue: false });",
    "    await upsertCompte(m.user_id, { stripe_subscription: s.subscription, formule: m.kind, statut_abonnement: 'active', resiliation_prevue: false, ...(m.pro === '1' ? { pro: true } : {}) });")
open(p, 'w', encoding='utf-8').write(s); print('patch abonnements appliqué')
