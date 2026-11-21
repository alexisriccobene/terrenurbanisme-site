# Marché immobilier resserré : commune de la parcelle uniquement, 500 m (1 km au plus), ventes atypiques écartées
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:70]))
    s = s.replace(old, new)

# 1. Collecte : seule la commune de la parcelle, cinq années, rayon maximal 1 km
a = s.index("  // 1. Communes dont le centre est à moins de rayon + 6 km")
b = s.index("comms.sort((a, b) => distM(center, ...a.centre.coordinates) - distM(center, ...b.centre.coordinates)).slice(0, maxCom).forEach(c => years.forEach(y => jobs.push({ c, y })));")
b = s.index('\n', b) + 1
s = s[:a] + """  // 1. Commune de la parcelle uniquement : les ventes des communes voisines ne reflètent pas le marché du terrain
  if (!insee) return null;
  const comms = [{ code: insee }];
  radius = Math.min(radius || 1000, 1000);
  const y0 = new Date().getFullYear(), years = [y0 - 1, y0 - 2, y0 - 3, y0 - 4, y0 - 5];
  const jobs = years.map(y => ({ c: comms[0], y }));
""" + s[b:]

# 2. Rayon 500 m si assez de ventes, sinon 1 km ; ventes atypiques écartées
rep("  const sum = (arr) => {\n", """  const nb500 = [...cat.maison, ...cat.appartement, ...cat.terrain].filter(x => x.dist <= 500).length;
  radius = nb500 >= 8 ? 500 : 1000;
  for (const k of Object.keys(cat)) cat[k] = cat[k].filter(x => x.dist <= radius);
  let ecartees = 0;
  const filt = (arr, lo, hi) => {
    if (arr.length < 4) return arr;
    const v = arr.map(x => x.pm2).sort((p, q) => p - q), med = pct(v, 0.5);
    const keep = arr.filter(x => x.pm2 >= med * lo && x.pm2 <= med * hi);
    ecartees += arr.length - keep.length; return keep;
  };
  cat.maison = filt(cat.maison, 0.5, 2); cat.appartement = filt(cat.appartement, 0.5, 2);
  cat.terrain = [...filt(cat.terrain.filter(x => x.ab), 0.33, 3), ...filt(cat.terrain.filter(x => !x.ab), 0.33, 3)];
  const nomC = ([...cat.maison, ...cat.appartement, ...cat.terrain][0] || {}).commune || '';
  const sum = (arr) => {
""")
rep("const res = { radius, communes: comms.length, period:", "const res = { radius, ecartees, commune: nomC, communes: comms.length, period:")
rep("async function market(center, radius = 10000, insee = '') {",
    "const rTxt = r => r >= 1000 ? (r / 1000).toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' km' : r + ' m';\nasync function market(center, radius = 1000, insee = '') {")
rep("await market(b.center, 10000, b.insee)", "await market(b.center, 1000, b.insee)")

# 3. Textes
rep("'Demandes de valeurs foncières géolocalisées (DVF), DGFiP et Etalab, rayon de ' + Math.round(((c.marche && c.marche.radius) || 10000) / 1000) + ' km'",
    "'Demandes de valeurs foncières géolocalisées (DVF), DGFiP et Etalab : ventes de la commune à moins de ' + rTxt((c.marche && c.marche.radius) || 10000) + ' de la parcelle'")
rep("(MK2.stats ? 'sur la commune' : 'dans un rayon de ' + Math.round((MK2.radius || 10000) / 1000) + ' km')",
    "(MK2.stats ? 'sur la commune' : 'sur la commune, à moins de ' + rTxt(MK2.radius || 10000) + ' du terrain')")

a = s.index("  } else if (MK) {\n    const km = Math.round(MK.radius / 1000);")
b = s.index("  const DV = d.dvf;", a)
blk = s[a:b]
def brep(old, new, n=1):
    global blk
    if blk.count(old) != n: sys.exit('ancre bloc introuvable (%d) : %s' % (blk.count(old), old[:70]))
    blk = blk.replace(old, new)
brep("    const km = Math.round(MK.radius / 1000);\n    h3('Marché immobilier dans un rayon de ' + km + ' km');\n",
     "    const km = rTxt(MK.radius), oneC = MK.radius <= 1000;\n    const dropC = (cols, rows) => { if (!oneC) return [cols, rows]; const c = cols.filter((_, i) => i !== 1), t = c.reduce((p, x) => p + x.w, 0); return [c.map(x => ({ ...x, w: x.w / t })), rows.map(r => r.filter((_, i) => i !== 1))]; };\n    h3(oneC ? 'Prix de vente autour du terrain, à moins de ' + km : 'Marché immobilier dans un rayon de ' + km);\n")
brep("    text('Ventes enregistrées ' + (MK.period ? 'de ' + MK.period : 'sur les dernières années publiées') + ' dans un rayon de ' + km + ' km autour de la parcelle (' + MK.communes + ' communes examinées). Seules les ventes portant sur un bien unique et identifiable sont retenues.', { size: 9 });",
     "    if (oneC) text('Ventes enregistrées ' + (MK.period ? 'de ' + MK.period : 'sur les dernières années publiées') + ' sur la commune de ' + (MK.commune || R.commune) + ', à moins de ' + km + ' de la parcelle. Seul le voisinage immédiat est retenu : les communes voisines et les quartiers éloignés ont d\\'autres prix et fausseraient la lecture. Seules les ventes d\\'un bien unique et identifiable sont comptées' + (MK.ecartees ? ' ; ' + MK.ecartees + ' vente' + (MK.ecartees > 1 ? 's' : '') + ' à un prix anormalement bas ou élevé (vente familiale, bien à rénover, erreur de saisie) ' + (MK.ecartees > 1 ? 'ont été écartées' : 'a été écartée') : '') + '.', { size: 9 });\n    else text('Ventes enregistrées ' + (MK.period ? 'de ' + MK.period : 'sur les dernières années publiées') + ' dans un rayon de ' + km + ' autour de la parcelle (' + MK.communes + ' communes examinées). Seules les ventes portant sur un bien unique et identifiable sont retenues.', { size: 9 });")
brep("table([{ label: 'DATE', w: 0.13 }, { label: 'COMMUNE'", "table(...dropC([{ label: 'DATE', w: 0.13 }, { label: 'COMMUNE'")
brep("table([{ label: 'DATE', w: 0.14 }, { label: 'COMMUNE'", "table(...dropC([{ label: 'DATE', w: 0.14 }, { label: 'COMMUNE'", 2)
brep("fmt(x.pm2)]), { size: 8 }); }", "fmt(x.pm2)])), { size: 8 }); }", 3)
s = s[:a] + blk + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('patch marche_local appliqué')
