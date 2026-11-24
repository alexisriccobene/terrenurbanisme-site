# Fiche du bien : nature du terrain (plat, pente, boisé...) pour les terrains
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("if (/^(neuf|tres_bon|bon|rafraichir|renover)$/.test(t(f.etat))) o.etat = t(f.etat);",
    "if (/^(neuf|tres_bon|bon|rafraichir|renover|plat|pente_douce|pente|boise|debroussailler|rocheux)$/.test(t(f.etat))) o.etat = t(f.etat);")
rep("renover: 'À rénover' };", "renover: 'À rénover', plat: 'Terrain plat', pente_douce: 'En pente douce', pente: 'En forte pente', boise: 'Boisé', debroussailler: 'À débroussailler', rocheux: 'Rocheux' };")
rep("['État général', ETAT[FI.etat] || '']", "[RC.type === 'terrain' ? 'Nature du terrain' : 'État général', ETAT[FI.etat] || '']")
open(p, 'w', encoding='utf-8').write(s); print('patch terrain appliqué')
