# Rapport généré avec un crédit : enregistre l'agent (collaborateur de l'agence) qui l'a demandé
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "await admin.from('dossiers').insert({ user_id: u.user.id, stripe_session_id: sessionId, order_ref: orderRef, email: u.user.email, insee, commune, section, numero, amount_total: 0, status: 'pending', projet, origine:"
if s.count(old) != 1: sys.exit('ancre introuvable : insert credit')
s = s.replace(old, "await admin.from('dossiers').insert({ user_id: u.user.id, stripe_session_id: sessionId, order_ref: orderRef, email: u.user.email, insee, commune, section, numero, amount_total: 0, status: 'pending', projet, agent: String(b.agent || '').replace(/[<>]/g, '').trim().slice(0, 80) || null, origine:")
open(p, 'w', encoding='utf-8').write(s); print('patch agent appliqué')
