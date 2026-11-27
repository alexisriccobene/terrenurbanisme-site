# Assistant et e-mails : plus d'abonnement proposé (27/11/2026), crédits uniquement.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
R = [("\n- Abonnement mensuel sans engagement, résiliable en un clic : 10 rapports par mois 129 € (12,90 €) ; 30 rapports par mois 297 € (9,90 €). Rapports non utilisés reportés une fois sur le mois suivant. Au-delà : offre personnalisée.", ""),
     (", la formule supérieure si son prix au rapport est nettement meilleur, et l'abonnement mensuel si le besoin est régulier.", ", ou la formule supérieure si son prix au rapport est nettement meilleur."),
     ("Exemple pour 15 : 10 crédits + lot de 3 + lot de 2 = 258,50 € ; ou 30 crédits à 357 € (11,90 € le rapport) ; ou, chaque mois, l'abonnement de 30 rapports à 297 €.", "Exemple pour 15 : 10 crédits + lot de 3 + lot de 2 = 217,50 € ; ou 30 crédits à 357 € (11,90 € le rapport). Il n'existe pas d'abonnement : uniquement des crédits payés une fois."),
     ("les crédits et l'abonnement pour les professionnels (logo sur le rapport)", "les crédits pour les professionnels (logo sur le rapport)"),
     ("Crédits sans limite de durée, ou abonnement mensuel sans engagement.", "Crédits sans limite de durée, payés une fois, sans abonnement.")]
for a, b in R:
    if s.count(a) != 1: print('ANCRE', s.count(a), a[:60]); sys.exit(1)
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('assistant sans abonnement')
