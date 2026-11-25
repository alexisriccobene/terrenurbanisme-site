"""Foncier entreprises : procédures limitées aux sociétés, coordonnées complètes du mandataire, synthèse limitée aux chiffres utiles, explication des pistes."""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)
# Procédures : sociétés seulement (pas les entrepreneurs individuels), mandataire avec son adresse
rep("    const lp = pj(r.listepersonnes); const pers = lp && (Array.isArray(lp.personne) ? lp.personne[0] : lp.personne) || {};",
    "    const lp = pj(r.listepersonnes); const pers = lp && (Array.isArray(lp.personne) ? lp.personne[0] : lp.personne) || {};\n    if (pers.typePersonne && pers.typePersonne !== 'pm') continue;", 'pm')
rep(r"""    const mm = comp.match(/(?:d[ée]sign(?:ant|e)|nomm(?:ant|e))\s+(?:en qualit[ée] de\s+)?(?:mandataire judiciaire|liquidateur(?: judiciaire)?|administrateur judiciaire)\s*:?\s*([^,;.]+(?:,\s*repr[ée]sent[ée]e? par [^,;.]+)?)/i);""",
    r"""    const mm = comp.match(/(?:d[ée]sign(?:ant|e)|nomm(?:ant|e))\s+(?:en qualit[ée] de\s+)?(?:mandataire judiciaire|liquidateur(?: judiciaire)?|administrateur judiciaire)\s*:?\s*(.{5,170}?)(?:\.\s|;|\s+Les cr[ée]ances|\s+et\s+d[ée]sign|$)/i);""", 'mand')
# Synthèse : seulement les chiffres utiles à la recherche
m = re.findall(r"tiles\.forEach\(", s)
if len(m) != 1: print('ANCRE tiles', len(m)); sys.exit(1)
s = s.replace("tiles.forEach(", "for (let i0 = tiles.length - 1; i0 >= 0; i0--) { const lab0 = String(tiles[i0][1]); if (!tiles[i0][0] || (q.besoin === 'batiment' && /sans bâtiment/.test(lab0)) || (q.besoin === 'terrain' && /avec bâtiment/.test(lab0))) tiles.splice(i0, 1); }\n  tiles.forEach(", 1)
# Explication des pistes
m = re.findall(r"newPage\(['\"]Les sites les plus pertinents['\"]\);?", s)
if len(m) != 1: print('ANCRE pertinents', len(m)); sys.exit(1)
s = s.replace(m[0], m[0] + "\n  note('Comment utiliser cette liste : ces terrains et bâtiments correspondent à vos critères, mais la plupart ne sont pas annoncés à la vente. Ce sont des pistes à approcher. Quand le propriétaire est une société, son nom est indiqué : retrouvez son siège et ses dirigeants sur annuaire-entreprises.data.gouv.fr. Les particuliers ne sont jamais nommés : passez par la mairie ou un agent immobilier. Pour une société en procédure (colonne Situation en rouge), contactez le mandataire judiciaire.');", 1)
open(p, 'w', encoding='utf-8').write(s); print('ok lisible')
