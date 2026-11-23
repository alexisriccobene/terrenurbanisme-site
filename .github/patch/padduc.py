# PADDUC : la plateforme Data Corsica a changé ; les cartes du PADDUC sont lues sur le serveur cartographique de la DREAL Corse
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + label)
    s = s.replace(old, new)
rep("['padduc-esa-donnees-vecteur', ", "['espaces_strategiques_agricoles', ", 'esa')
rep("['padduc-erc-donnees-vecteur', ", "['espaces_remarquables_caracteristiques', ", 'erc')
rep("['padduc-ese-donnees-vecteur', ", "['ressource_pastoralisme_arboriculture_traditionnelle', ", 'ese')
a = s.index("  await Promise.all(PADDUC_LAYERS.map(async ([id, label, explain, major]) => {")
b = s.index("  // Atlas loi Littoral de l'État (espaces remarquables, espaces proches du rivage)", a)
NEW = r"""  // Cartes du PADDUC publiées par la DREAL Corse (WFS) : test d'intersection côté serveur, sans télécharger les géométries
  const WFS = 'https://georchestra.dreal-corse.din.developpement-durable.gouv.fr/geoserver/dreal/ows?service=WFS&version=2.0.0&request=GetFeature&resultType=hits&typeNames=dreal:';
  const bb0 = turf.bbox(pf), ct = turf.centroid(pf).geometry.coordinates, e = 0.00003;
  const hitsOf = async (id, b) => {
    const t = await (await fetch(WFS + id + '&bbox=' + b[1] + ',' + b[0] + ',' + b[3] + ',' + b[2] + ',urn:ogc:def:crs:EPSG::4326', { signal: AbortSignal.timeout(15000) })).text();
    const m = t.match(/numberMatched="(\d+)"/); if (!m) throw new Error('wfs'); return Number(m[1]);
  };
  await Promise.all(PADDUC_LAYERS.map(async ([id, label, explain, major]) => {
    try {
      const n = await hitsOf(id, bb0);
      if (major) checked = true; sources.push(id);
      if (n > 0) {
        let share = null;
        try { share = (await hitsOf(id, [ct[0] - e, ct[1] - e, ct[0] + e, ct[1] + e])) > 0 ? 0.6 : 0.2; } catch (e2) { share = null; }
        hits.push({ label, explain: share === 0.2 ? explain + ' Seule une bordure de la parcelle semble concernée : faites préciser la limite exacte en mairie.' : explain, share, major: major && share !== 0.2, approx: true });
      }
    } catch (e1) { /* serveur indisponible : le rapport invite à vérifier en mairie */ }
  }));
"""
s = s[:a] + NEW + s[b:]
rep("table([{ label: 'ESPACE DU PADDUC', w: 0.6 }, { label: 'PART DE LA PARCELLE', w: 0.4 }], P.hits.map(h => [h.label, h.share != null ? Math.round(h.share * 100) + ' %' : 'Concernée']));",
    "table([{ label: 'ESPACE DU PADDUC', w: 0.6 }, { label: 'PARCELLE CONCERNÉE', w: 0.4 }], P.hits.map(h => [h.label, h.approx ? (h.share >= 0.5 ? 'Oui, au moins en majeure partie' : 'Oui, en bordure ou en partie') : h.share != null ? Math.round(h.share * 100) + ' %' : 'Oui']));", 'table')
open(p, 'w', encoding='utf-8').write(s); print('patch padduc appliqué')
