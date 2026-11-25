"""Foncier : textes alignés — plus de bâtiments « sans entreprise » (non prouvables), annonces pour les locaux vides."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(a, b, label):
    global s
    n = s.count(a)
    if n != 1: print('ANCRE', label, n); sys.exit(1)
    s = s.replace(a, b)
one("Seuls les sites disponibles sont retenus : terrains libres, bâtiments sans entreprise en activité, biens de sociétés en liquidation ou fermées, friches. Les sites occupés par une entreprise en activité sont écartés.",
    "Seuls les sites disponibles sont retenus : terrains libres et sans construction, terrains et bâtiments de sociétés en liquidation ou fermées, friches. Les sites occupés par une entreprise en activité sont écartés. Pour les hangars et locaux vides, voir aussi les annonces en cours à la fin du rapport.", 'intro')
one("'Un site est retenu s\\'il est libre : terrain sans construction, bâtiment où aucune entreprise en activité n\\'est déclarée (répertoire Sirene de l\\'INSEE, établissements géolocalisés), bien d\\'une société en procédure collective ou radiée (BODACC), ou friche (Cartofriches). Les sites occupés par une entreprise en activité, y compris par leur propriétaire, sont écartés. Un bâtiment sans activité déclarée reste à vérifier sur place.'",
    "'Un site est retenu s\\'il est disponible : terrain sans construction et sans entreprise en activité déclarée (répertoire Sirene de l\\'INSEE), bien d\\'une société en procédure collective ou radiée (BODACC), ou friche (Cartofriches). Les sites occupés par une entreprise en activité, y compris par leur propriétaire, sont écartés.'", 'methode')
open(p, 'w', encoding='utf-8').write(s); print('ok dispo2')
