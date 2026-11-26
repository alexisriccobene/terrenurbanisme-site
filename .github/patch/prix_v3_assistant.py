# Assistant et e-mails : grille particuliers rétablie à 19,90 / 29,80 / 38,70 (26/11/2026).
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
R = [("Particuliers : 29,90 € le rapport ; lot de 2 à 49,80 € (24,90 € le rapport) ; lot de 3 à 59,70 € (19,90 € le rapport)",
      "Particuliers : 19,90 € le rapport ; lot de 2 à 29,80 € (14,90 € le rapport) ; lot de 3 à 38,70 € (12,90 € le rapport)"),
     ("return '1 rapport : 29,90 €.';", "return '1 rapport : 19,90 €.';"),
     ("return '2 rapports : lot de 2 à 49,80 €, soit 24,90 € le rapport.';", "return '2 rapports : lot de 2 à 29,80 €, soit 14,90 € le rapport.';"),
     ("return '3 rapports : lot de 3 à 59,70 €, soit 19,90 € le rapport.';", "return '3 rapports : lot de 3 à 38,70 €, soit 12,90 € le rapport.';"),
     ("['unit', 1, 29.9, 'rapport à l\\'unité'], ['pack2', 2, 49.8, 'lot de 2'], ['pack3', 3, 59.7, 'lot de 3']",
      "['unit', 1, 19.9, 'rapport à l\\'unité'], ['pack2', 2, 29.8, 'lot de 2'], ['pack3', 3, 38.7, 'lot de 3']")]
for a, b in R:
    if s.count(a) != 1: print('ANCRE', s.count(a), a[:60]); sys.exit(1)
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('assistant : grille 19,90')
