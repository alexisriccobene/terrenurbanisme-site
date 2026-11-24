# Verdict : le titre suit toujours le zonage du PLU. Si le PLU classe la parcelle en zone constructible,
# le titre dit « Constructible » et les contraintes supérieures (PADDUC) sont présentées comme un point de vigilance.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable : ' + old[:70])
    s = s.replace(old, new)
rep("""    if (key === 'ok') key = 'cond';
    if (erc && key !== 'non') key = 'non';
    else if (esa && !zoneConstr && key !== 'non') key = 'non';""", """    if (!zoneConstr) { if (key === 'ok') key = 'cond'; if ((erc || esa) && key !== 'non') key = 'non'; }
    else if (erc) { if (key === 'ok') key = 'cond'; vigil = 'ERC'; }
    else vigil = 'ESA';""")
rep("""    if (esa && zoneConstr && !erc) {""", """    if (erc && zoneConstr) {
      why += ' Attention : selon la cartographie du PADDUC, la parcelle est aussi située dans un espace remarquable et caractéristique du littoral, où seuls des aménagements légers sont en principe admis. Ce point est à faire confirmer par la mairie (certificat d\\'urbanisme opérationnel) avant tout engagement.';
    } else if (esa && zoneConstr) {""")
rep("""      why += ' La parcelle est toutefois située, selon la cartographie du PADDUC, dans un espace stratégique agricole,""", """      why += ' Point de vigilance : la parcelle est aussi située, selon la cartographie du PADDUC, dans un espace stratégique agricole,""")
# déclaration de vigil avant le bloc PADDUC
rep("""  if (majorHits.length) {
    const erc = majorHits.some(""", """  let vigil = '';
  if (majorHits.length) {
    const erc = majorHits.some(""")
rep("""    ref: R, verdict: { key, word: WORD[key], title: TITLE[key], why },""", """    ref: R, verdict: { key, word: WORD[key], title: vigil && key === 'ok' ? 'Le PLU autorise la construction, avec un point de vigilance' : vigil && key === 'cond' ? 'Constructible au PLU, avec une contrainte forte à vérifier' : TITLE[key], why, vigil },""")
open(p, 'w', encoding='utf-8').write(s); print('patch verdict_plu appliqué')
