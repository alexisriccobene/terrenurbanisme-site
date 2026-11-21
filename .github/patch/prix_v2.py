# Nouvelle grille (21/11/2026) : 29,90 / 49,80 / 59,70 ; pros 10 = 149, 30 = 357, 100 = 790 ; abonnements 10/mois = 129, 30/mois = 297. Autres formules retirées.
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index('const OFFERS = {'); b = s.index('\n};', a) + 3
NEW = '''const OFFERS = {
  synth: { mode: 'payment', amount: 990, credits: 1, name: 'Rapport d\\'urbanisme synthétique (2 pages)', synth: true },
  upgrade: { mode: 'payment', amount: 1000, credits: 0, name: 'Passage au rapport d\\'urbanisme complet', upgrade: true },
  unit: { mode: 'payment', amount: 2990, credits: 1, name: 'Rapport d\\'urbanisme complet' },
  pack2: { mode: 'payment', amount: 4980, credits: 2, name: 'Lot de 2 rapports d\\'urbanisme' },
  pack3: { mode: 'payment', amount: 5970, credits: 3, name: 'Lot de 3 rapports d\\'urbanisme' },
  pro10: { mode: 'payment', amount: 14900, credits: 10, name: 'Crédits professionnels · 10 rapports', pro: true },
  pro30: { mode: 'payment', amount: 35700, credits: 30, name: 'Crédits professionnels · 30 rapports', pro: true },
  pro100: { mode: 'payment', amount: 79000, credits: 100, name: 'Crédits professionnels · 100 rapports', pro: true },
  ab10: { mode: 'subscription', interval: 'month', amount: 12900, credits: 10, mois: 10, name: 'Abonnement TerrenUrbanisme · 10 rapports par mois', pro: true },
  ab30: { mode: 'subscription', interval: 'month', amount: 29700, credits: 30, mois: 30, name: 'Abonnement TerrenUrbanisme · 30 rapports par mois', pro: true }
};'''
s = s[:a] + NEW + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('nouvelle grille appliquée')
