"""Foncier : ne retenir que les sites disponibles (terrain libre, bâtiment sans entreprise en activité, société en procédure ou radiée, friche)."""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(pat, rep, label, rx=False):
    global s
    m = list(re.finditer(pat if rx else re.escape(pat), s))
    if len(m) != 1: print('ANCRE', label, len(m)); sys.exit(1)
    s = s[:m[0].start()] + (rep(m[0]) if callable(rep) else rep) + s[m[0].end():]
one("const d = hav(q.lat, q.lon, s.lat, s.lon); if (d > q.rayon_km) return;", "const d = hav(q.lat, q.lon, s.lat, s.lon); if (d > q.rayon_km) return;\n    if (s.v >= 2 && !s.dispo) return;", 'keep')
one("const sit = (s)=>s.kind === 'friche'", "const sit = (s)=>s.dispo === 'vacant' ? 'Aucune entreprise en activité à cette adresse' : s.dispo === 'libre' ? 'Terrain libre' : s.kind === 'friche'", 'sit')
one(r"terr: sites\.filter\(\(s\)=>s\.kind === 'terrain' && !s\.bati\)\.length,\s*bat: sites\.filter\(\(s\)=>s\.bati\)\.length,", "terr: sites.filter((s)=>s.kind === 'terrain' && !s.bati && (!s.v || s.dispo === 'libre')).length,\n    bat: sites.filter((s)=>s.bati && (!s.v || s.dispo === 'vacant')).length,", 'cnt', rx=True)
one(r"soc: sites\.filter\(\(s\)=>s\.siren\)\.length,", "soc: 0,", 'soc', rx=True)
one("'sites avec bâtiment d\\'activité'", "'bâtiments sans entreprise en activité'", 'tile')
one("Ils sont classés par pertinence : zone d'activité du PLU, société en difficulté, friche, proximité d'un poste électrique et distance.`", "Seuls les sites disponibles sont retenus : terrains libres, bâtiments sans entreprise en activité, biens de sociétés en liquidation ou fermées, friches. Les sites occupés par une entreprise en activité sont écartés. Ils sont classés par pertinence : zone d'activité du PLU, société en difficulté, friche, proximité d'un poste électrique et distance.`", 'intro')
one("    ...(q._verif ? [[", """    [
      'Disponibilité',
      'Un site est retenu s\\'il est libre : terrain sans construction, bâtiment où aucune entreprise en activité n\\'est déclarée (répertoire Sirene de l\\'INSEE, établissements géolocalisés), bien d\\'une société en procédure collective ou radiée (BODACC), ou friche (Cartofriches). Les sites occupés par une entreprise en activité, y compris par leur propriétaire, sont écartés. Un bâtiment sans activité déclarée reste à vérifier sur place.'
    ],
    ...(q._verif ? [[""", 'methode')
open(p, 'w', encoding='utf-8').write(s); print('ok dispo')
