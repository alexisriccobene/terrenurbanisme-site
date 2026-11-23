# Rapport : alléger le calcul (enregistrement du PDF sans flux d'objets, calque cadastre plus léger)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + label)
    s = s.replace(old, new)
rep("  return await pdf.save();", "  return await pdf.save({ useObjectStreams: false });", 'save')
rep("getBytes(wms('CADASTRALPARCELS.PARCELLAIRE_EXPRESS', bbox, 975, 501, 'image/png'))", "getBytes(wms('CADASTRALPARCELS.PARCELLAIRE_EXPRESS', bbox, 760, 390, 'image/png'))", 'cadastre')
open(p, 'w', encoding='utf-8').write(s); print('patch cpu appliqué')
