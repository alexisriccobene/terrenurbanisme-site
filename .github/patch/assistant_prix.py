# Assistant : nouvelle grille tarifaire (21/11/2026) et conseil de la formule la plus proche du besoin
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
L = s.split('\n')
i = next(k for k, l in enumerate(L) if l.startswith('- Particuliers : 19,90 €'))
assert L[i + 1].startswith('- Professionnels, crédits') and L[i + 2].startswith('- Abonnement mensuel'), 'ancre'
L[i:i + 3] = [
"- Particuliers : 29,90 € le rapport ; lot de 2 à 49,80 € (24,90 € le rapport) ; lot de 3 à 59,70 € (19,90 € le rapport). Rapports d'un lot sans limite de durée.",
"- Professionnels, crédits sans limite de durée : 10 rapports 149 € (14,90 €), 30 rapports 357 € (11,90 €), 100 rapports 790 € (7,90 €). Logo et coordonnées du professionnel sur chaque rapport, back-office pour les collaborateurs.",
"- Abonnement mensuel sans engagement, résiliable en un clic : 10 rapports par mois 129 € (12,90 €) ; 30 rapports par mois 297 € (9,90 €). Rapports non utilisés reportés une fois sur le mois suivant. Au-delà : offre personnalisée.",
"- Quand on te demande le prix pour un nombre de rapports qui ne correspond pas à une formule (par exemple 15), ne réponds jamais qu'il n'existe pas d'offre : conseille la formule la plus proche. Donne la combinaison la moins chère pour couvrir ce nombre (crédits et lots peuvent se cumuler ; les rapports en plus restent sur le compte sans limite de durée), la formule supérieure si son prix au rapport est nettement meilleur, et l'abonnement mensuel si le besoin est régulier. Exemple pour 15 : 10 crédits + lot de 3 + lot de 2 = 258,50 € ; ou 30 crédits à 357 € (11,90 € le rapport) ; ou, chaque mois, l'abonnement de 30 rapports à 297 €.",
]
s = '\n'.join(L)
open(p, 'w', encoding='utf-8').write(s); print('patch assistant_prix appliqué')
