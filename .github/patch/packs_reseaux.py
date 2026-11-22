# create-checkout : packs réseaux 250 et 500 rapports en paiement en ligne
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "  pro100: { mode: 'payment', amount: 35000, credits: 100, name: 'Crédits professionnels · 100 rapports', pro: true }\n"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, "  pro100: { mode: 'payment', amount: 35000, credits: 100, name: 'Crédits professionnels · 100 rapports', pro: true },\n  pro250: { mode: 'payment', amount: 75000, credits: 250, name: 'Crédits professionnels · 250 rapports', pro: true },\n  pro500: { mode: 'payment', amount: 125000, credits: 500, name: 'Crédits professionnels · 500 rapports', pro: true }\n")
s = s.replace('// TerrenUrbanisme · fonction « create-checkout » (v17)', '// TerrenUrbanisme · fonction « create-checkout » (v18)\n// v18 : packs réseaux de 250 et 500 rapports (3 € et 2,50 € le rapport) achetables en ligne.')
open(p, 'w', encoding='utf-8').write(s); print('patch packs_reseaux appliqué')
