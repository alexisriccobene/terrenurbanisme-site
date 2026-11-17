# Agences et professionnels : packs de crédits sans abonnement (5 € le rapport au plus, dégressif) ; plus de nouvel abonnement
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
m = re.search(r'const OFFERS\b[^=]*=\s*\{', s)
if not m: print(s[:3000]); sys.exit('ancre OFFERS')
end = s.index('\n};', m.end()) + 3
s = s[:m.start()] + """const OFFERS: Record<string, { mode: string; amount: number; credits: number; name: string; interval?: string; pro?: boolean }> = {
  unit:   { mode: 'payment', amount: 1990,  credits: 1,   name: 'Rapport d\\'urbanisme complet' },
  pack2:  { mode: 'payment', amount: 2980,  credits: 2,   name: 'Lot de 2 rapports d\\'urbanisme' },
  pack3:  { mode: 'payment', amount: 3870,  credits: 3,   name: 'Lot de 3 rapports d\\'urbanisme' },
  // v16 : professionnels en crédits, sans abonnement ni engagement (crédits sans limite de durée, logo et back-office inclus)
  pro10:  { mode: 'payment', amount: 5000,  credits: 10,  name: 'Crédits professionnels · 10 rapports', pro: true },
  pro25:  { mode: 'payment', amount: 11000, credits: 25,  name: 'Crédits professionnels · 25 rapports', pro: true },
  pro50:  { mode: 'payment', amount: 20000, credits: 50,  name: 'Crédits professionnels · 50 rapports', pro: true },
  pro100: { mode: 'payment', amount: 35000, credits: 100, name: 'Crédits professionnels · 100 rapports', pro: true }
};""" + s[end:]
m2 = re.search(r'\n(\s*)const meta\b[^\n]*\n', s)
if not m2: sys.exit('ancre meta')
s = s[:m2.end()] + m2.group(1) + "if ((offer as any).pro) meta.pro = '1';\n" + s[m2.end():]
open(p, 'w', encoding='utf-8').write(s); print('patch credits_pro appliqué')
