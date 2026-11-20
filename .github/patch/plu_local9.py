# Zonages communaux : règlement de la zone reproduit en annexe (preuve de lecture du PLU), mention de la source communale
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + old[:70])
    s = s.replace(old, new)
rep("      try { res = await analyseReglement(zone, u, commune, main && !p.copie); }", "      try { res = await analyseReglement(zone, u, commune, main); }")
rep("du document approuvé), tel que publié sur le Géoportail de l\\'Urbanisme. Il s\\'agit",
    "du document approuvé), tel que publié ' + (d.doc && d.doc.local ? 'par la commune' : 'sur le Géoportail de l\\'Urbanisme') + '. Il s\\'agit")
open(p, 'w', encoding='utf-8').write(s); print('patch plu_local9 appliqué')
