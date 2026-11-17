# Crédits professionnels : l'achat d'un pack pro active les avantages pro (logo, back-office) sans abonnement
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + old[:60])
    s = s.replace(old, new)
rep("""  if (!m.insee) { // lot de rapports ou rapport à l'unité acheté depuis la page Tarifs""", """  if (m.pro === '1') { try { await upsertCompte(m.user_id, { pro: true }); } catch (e) { console.error('compte pro', e); } }
  if (!m.insee) { // lot de rapports ou rapport à l'unité acheté depuis la page Tarifs""")
rep("""  const { data: cp } = await admin.from('comptes').select('statut_abonnement, formule').eq('user_id', uid).maybeSingle();""", """  const { data: cp } = await admin.from('comptes').select('statut_abonnement, formule, pro').eq('user_id', uid).maybeSingle();""")
rep("""  if (!OWNER && (!cp || !['active', 'trialing', 'past_due'].includes(cp.statut_abonnement || '') || /^essentiel/.test(cp.formule || ''))) return null;""", """  if (!OWNER && !(cp && cp.pro) && (!cp || !['active', 'trialing', 'past_due'].includes(cp.statut_abonnement || '') || /^essentiel/.test(cp.formule || ''))) return null;""")
open(p, 'w', encoding='utf-8').write(s); print('patch credits_pro_wh appliqué')
