# Zonage relevé sur un plan communal : les prescriptions graphiques ne sont pas numérisées, on ne peut pas écrire « aucune »
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "} else text('Aucune prescription graphique du PLU (emplacement réservé, espace boisé classé, élément de paysage protégé, etc.) n\\'est recensée sur la parcelle.', { size: 9.5 });"
assert s.count(a) == 1, s.count(a)
b = "} else text(d.doc && d.doc.local ? 'Les prescriptions graphiques du PLU de cette commune (emplacements réservés, espaces boisés classés, éléments de paysage protégés, etc.) ne sont pas publiées sous forme numérique : elles figurent uniquement sur le plan de zonage officiel' + (d.doc.source ? ' (' + d.doc.source + ')' : '') + ', à consulter pour la parcelle.' : 'Aucune prescription graphique du PLU (emplacement réservé, espace boisé classé, élément de paysage protégé, etc.) n\\'est recensée sur la parcelle.', { size: 9.5 });"
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('patch presc_local appliqué')
