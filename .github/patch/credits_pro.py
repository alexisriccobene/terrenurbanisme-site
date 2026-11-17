# Agences et professionnels : packs de crédits sans abonnement (5 € le rapport au plus, dégressif) ; plus de nouvel abonnement
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index("const OFFERS: Record<string,"); b = s.index("};", a) + 2
s = s[:a] + """const OFFERS: Record<string, { mode: string; amount: number; credits: number; name: string; interval?: string; pro?: boolean }> = {
  unit:   { mode: 'payment', amount: 1990,  credits: 1,   name: 'Rapport d\\'urbanisme complet' },
  pack2:  { mode: 'payment', amount: 2980,  credits: 2,   name: 'Lot de 2 rapports d\\'urbanisme' },
  pack3:  { mode: 'payment', amount: 3870,  credits: 3,   name: 'Lot de 3 rapports d\\'urbanisme' },
  // v16 : professionnels en crédits, sans abonnement ni engagement (crédits sans limite de durée, logo et back-office inclus)
  pro10:  { mode: 'payment', amount: 5000,  credits: 10,  name: 'Crédits professionnels · 10 rapports', pro: true },
  pro25:  { mode: 'payment', amount: 11000, credits: 25,  name: 'Crédits professionnels · 25 rapports', pro: true },
  pro50:  { mode: 'payment', amount: 20000, credits: 50,  name: 'Crédits professionnels · 50 rapports', pro: true },
  pro100: { mode: 'payment', amount: 35000, credits: 100, name: 'Crédits professionnels · 100 rapports', pro: true }
};""" + s[b:]
old = "const meta: Record<string, string> = user ? { user_id: user.id, kind, credits: String(offer.credits) } : { guest: '1', kind, credits: String(offer.credits) };"
if s.count(old) != 1: sys.exit('ancre meta')
s = s.replace(old, old + "\n    if (offer.pro) meta.pro = '1';")
s = s.replace("// TerrenUrbanisme · fonction « create-checkout » (v15)", "// TerrenUrbanisme · fonction « create-checkout » (v16)")
open(p, 'w', encoding='utf-8').write(s); print('patch credits_pro appliqué')
