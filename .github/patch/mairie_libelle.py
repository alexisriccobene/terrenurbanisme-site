# Rapports des communes : « La mairie de X » au lieu de « Offert par la Ville de X » (couverture, interlocuteur, dernière page)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("nom: 'Offert par ' + villeLib(V),", "nom: 'La mairie de ' + V.nom,")
rep("const th = clean('vous remercie également de votre confiance');", "const th = clean('vous remercie également pour votre confiance');")
open(p, 'w', encoding='utf-8').write(s); print('patch libellé mairie appliqué')
