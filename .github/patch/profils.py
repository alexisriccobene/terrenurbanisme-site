"""Rapport adapté au profil choisi à la commande (particulier, agent immobilier, notaire, maître d'œuvre ou architecte).
Ajoute : profil transmis du paiement au rapport, chapitre « L'essentiel pour … », loyers (Carte des loyers), copropriété (RNIC),
commerces et services à proximité (OpenStreetMap), zone climatique RE2020, pièces du permis, plan DXF joint au PDF."""
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n:
        print('ANCRE', c, 'au lieu de', n, ':', old[:120]); sys.exit(1)
    s = s.replace(old, new)

HELP = r'''
// ---------- Profil du demandeur : la présentation du rapport s'adapte (le fond réglementaire reste complet pour tous) ----------
const PROFILS = { particulier: 'Particulier', agent: 'Agent immobilier', notaire: 'Notaire', moe: 'Maître d\'œuvre ou architecte' };
const PROFIL_TITRE = { agent: 'L\'essentiel pour l\'agent immobilier', notaire: 'L\'essentiel pour le notaire', moe: 'L\'essentiel pour le maître d\'œuvre' };
const PROFIL_ABOUT = {
  agent: 'Les éléments utiles à l\'estimation et à la vente : prix et loyers du secteur, diagnostic énergétique, copropriété, commerces et services à proximité.',
  notaire: 'Les points à contrôler avant l\'acte, avec leur résultat et le chapitre qui les détaille : urbanisme, servitudes, préemption, risques, copropriété.',
  moe: 'Le cadre technique du projet : règles clés de la zone, zone climatique RE2020, sol et risques, relief, pièces du permis et plan du terrain au format DXF.'
};
function profilCle(v) {
  const s = String(v || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  if (PROFILS[s]) return s;
  if (/agen|immobil/.test(s)) return 'agent'; if (/notai/.test(s)) return 'notaire';
  if (/archi|oeuvre|moe|geometre|construct|promot/.test(s)) return 'moe'; if (/particulier/.test(s)) return 'particulier';
  return null;
}
async function profilCompte(uid) {
  try {
    const { data } = await admin.from('marques').select('type').eq('user_id', uid).maybeSingle();
    const t = String(data && data.type || '');
    return /agence|conciergerie|courtier|banque/.test(t) ? 'agent' : /notaire/.test(t) ? 'notaire' : /architecte|geometre|constructeur|promoteur/.test(t) ? 'moe' : null;
  } catch (e) { return null; }
}
// Zones climatiques (annexe I de l'arrêté du 26 octobre 2010, reprises pour la RE2020 par l'arrêté du 4 août 2021)
const ZCLIM = {};
[['H1a', '02 14 27 28 59 60 61 62 75 76 77 78 80 91 92 93 94 95'], ['H1b', '08 10 45 51 52 54 55 57 58 67 68 70 88 89 90'],
 ['H1c', '01 03 05 15 19 21 23 25 38 39 42 43 63 69 71 73 74 87'], ['H2a', '22 29 35 50 56'], ['H2b', '16 17 18 36 37 41 44 49 53 72 79 85 86'],
 ['H2c', '09 12 24 31 32 33 40 46 47 64 65 81 82'], ['H2d', '04 07 26 48 84'], ['H3', '06 11 13 2A 2B 30 34 66 83']].forEach(([z, l]) => l.split(' ').forEach(dp => { ZCLIM[dp] = z; }));
function zoneClimatique(insee, alti) {
  const dp = depOf(insee);
  if (/^97/.test(dp)) return { dom: true };
  const z = ZCLIM[dp]; if (!z) return null;
  const a = alti && alti.min != null ? Math.round((alti.min + alti.max) / 2) : null;
  return { zone: z, alt: a, classe: a == null ? null : a <= 400 ? 'altitude inférieure ou égale à 400 m' : a <= 800 ? 'altitude de 401 à 800 m' : 'altitude supérieure à 800 m' };
}
// Carte des loyers 2025 (ministère chargé du logement) : loyer d'annonce prédit au m², appartements et maisons
async function loyersCommune(insee) {
  const R = { app: '55b34088-0964-415f-9df7-d87dd98a09be', mai: '129f764d-b613-44e4-952c-5ff50a8c9b73' }, out = { annee: 2025 };
  await Promise.all(Object.entries(R).map(async ([k, rid]) => {
    const j = await getJSON(`https://tabular-api.data.gouv.fr/api/resources/${rid}/data/?INSEE_C__exact=${encodeURIComponent(insee)}`, 15000);
    const r = j && j.data && j.data[0];
    if (r && Number(r.loypredm2) > 0) out[k] = { m2: Number(r.loypredm2), lo: Number(r['lwr.IPm2']) || null, hi: Number(r['upr.IPm2']) || null, commune: r.TYPPRED === 'commune', nb: Number(r.nbobs_com) || 0 };
  }));
  return out.app || out.mai ? out : null;
}
// Registre national d'immatriculation des copropriétés (ANAH) : copropriétés déclarées sur la parcelle
async function coproParcelle(idu) {
  if (!/^[0-9AB]{5}\d{3}[0-9A-Z]{2}\d{4}$/.test(String(idu || ''))) return null;
  const rid = 'cc062fa7-4a80-449c-ab73-d2856b455ec9', seen = new Set(), out = [];
  const rs = await Promise.all([1, 2, 3].map(i => getJSON(`https://tabular-api.data.gouv.fr/api/resources/${rid}/data/?reference_cadastrale_${i}__exact=${idu}`, 15000).catch(() => null)));
  for (const j of rs) for (const r of (j && j.data || [])) {
    if (seen.has(r.numero_d_immatriculation)) continue; seen.add(r.numero_d_immatriculation);
    const per = String(r.periode_de_construction || '').replace(/^AVANT_/, 'avant ').replace(/^A_COMPTER_DE_/, 'à partir de ').replace(/^DE_(\d+)_A_(\d+)$/, 'de $1 à $2').replace(/^NON_CONNUE$/, '');
    out.push({ nom: r.nom_d_usage_de_la_copropriete && !/non connu/i.test(r.nom_d_usage_de_la_copropriete) ? r.nom_d_usage_de_la_copropriete : '', immat: r.numero_d_immatriculation,
      lots: Number(r.nombre_total_de_lots) || null, hab: Number(r.nombre_de_lots_a_usage_d_habitation) || null, park: Number(r.nombre_de_lots_de_stationnement) || null,
      syndic: /non connu/i.test(r.type_de_syndic_benevole_professionnel_non_connu || '') ? '' : r.type_de_syndic_benevole_professionnel_non_connu,
      mandat: r.mandat_en_cours_dans_la_copropriete || '', reglement: r.date_du_reglement_de_copropriete ? frDate(String(r.date_du_reglement_de_copropriete).slice(0, 10)) : '', periode: per, maj: r.date_de_la_derniere_maj || '' });
  }
  return out;
}
// Commerces, écoles, santé et transports les plus proches (OpenStreetMap, distances à vol d'oiseau)
async function proximite(ctr) {
  const [lon, lat] = ctr, A = (r) => `(around:${r},${lat.toFixed(6)},${lon.toFixed(6)})`;
  const q = `[out:json][timeout:20];(nwr${A(3000)}["amenity"~"^(school|pharmacy|doctors|kindergarten)$"];nwr${A(3000)}["shop"~"^(supermarket|bakery|convenience)$"];nwr${A(8000)}["railway"="station"];nwr${A(1500)}["highway"="bus_stop"];);out center tags 400;`;
  const r = await fetch('https://overpass-api.de/api/interpreter', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'TerrenUrbanisme (contact@terrenurbanisme.com)' }, body: 'data=' + encodeURIComponent(q), signal: AbortSignal.timeout(22000) });
  if (!r.ok) throw new Error('overpass ' + r.status);
  const j = await r.json();
  const CAT = [['Crèche ou école maternelle', t => t.amenity === 'kindergarten'], ['École, collège ou lycée', t => t.amenity === 'school'], ['Boulangerie', t => t.shop === 'bakery'],
    ['Supermarché', t => t.shop === 'supermarket'], ['Commerce d\'alimentation', t => t.shop === 'convenience'], ['Pharmacie', t => t.amenity === 'pharmacy'], ['Médecin', t => t.amenity === 'doctors'],
    ['Arrêt de bus', t => t.highway === 'bus_stop'], ['Gare', t => t.railway === 'station']];
  const best = {};
  for (const e of (j.elements || [])) {
    const t = e.tags || {}, la = e.lat != null ? e.lat : e.center && e.center.lat, lo = e.lon != null ? e.lon : e.center && e.center.lon; if (la == null) continue;
    const dist = turf.distance(turf.point([lon, lat]), turf.point([lo, la]), { units: 'meters' });
    for (const [lab, f] of CAT) if (f(t) && (!best[lab] || dist < best[lab].d)) best[lab] = { d: dist, nom: t.name || '' };
  }
  return CAT.map(([lab]) => best[lab] ? { cat: lab, nom: best[lab].nom, d: Math.round(best[lab].d) } : null).filter(Boolean);
}
// Plan du terrain au format DXF (Lambert 93) : parcelle, parcelles voisines et leurs numéros, bâtiments, points d'altitude
async function planDxf(pf) {
  const b0 = turf.bbox(turf.buffer(pf, 60, { units: 'meters' })), box = turf.bboxPolygon(b0).geometry;
  const [pj, bj] = await Promise.all([
    getJSON(`${CARTO}/cadastre/parcelle?geom=${encodeURIComponent(JSON.stringify(box))}`, 20000).catch(() => null),
    getJSON(`https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=BDTOPO_V3:batiment&outputFormat=application/json&count=800&bbox=${b0[1]},${b0[0]},${b0[3]},${b0[2]},urn:ogc:def:crs:EPSG::4326&propertyName=geometrie,hauteur`, 20000).catch(() => null)
  ]);
  const N = 11, pts = [];
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) pts.push([b0[0] + (b0[2] - b0[0]) * i / (N - 1), b0[1] + (b0[3] - b0[1]) * j / (N - 1)]);
  const aj = await getJSON(`https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json?lon=${pts.map(p => p[0].toFixed(6)).join('|')}&lat=${pts.map(p => p[1].toFixed(6)).join('|')}&resource=ign_rge_alti_wld&zonly=true`, 20000).catch(() => null);
  const Z = (aj && aj.elevations || []).map(Number);
  const o = [], f2 = v => v.toFixed(2), L = (...a) => o.push(...a.map(String));
  const poly = (ring, layer, z = 0) => { L(0, 'POLYLINE', 8, layer, 66, 1, 10, 0, 20, 0, 30, f2(z), 70, 1); for (const q of ring) { const [x, y] = l93(q[0], q[1]); L(0, 'VERTEX', 8, layer, 10, f2(x), 20, f2(y), 30, f2(z)); } L(0, 'SEQEND', 8, layer); };
  const txt = (lonlat, t, h, layer) => { const [x, y] = l93(lonlat[0], lonlat[1]); L(0, 'TEXT', 8, layer, 10, f2(x), 20, f2(y), 30, '0.00', 40, h, 1, t, 72, 1, 11, f2(x), 21, f2(y), 31, '0.00'); };
  const rings = g => g.type === 'MultiPolygon' ? g.coordinates.map(p => p[0]) : g.type === 'Polygon' ? [g.coordinates[0]] : [];
  L(0, 'SECTION', 2, 'HEADER', 9, '$ACADVER', 1, 'AC1009', 0, 'ENDSEC', 0, 'SECTION', 2, 'TABLES', 0, 'TABLE', 2, 'LAYER', 70, 6);
  for (const [n, col] of [['PARCELLE', 1], ['CADASTRE', 8], ['NUMEROS', 7], ['BATI', 5], ['ALTI', 3]]) L(0, 'LAYER', 2, n, 70, 0, 62, col, 6, 'CONTINUOUS');
  L(0, 'ENDTAB', 0, 'ENDSEC', 0, 'SECTION', 2, 'ENTITIES');
  for (const r of rings(pf.geometry)) poly(r, 'PARCELLE');
  for (const f of (pj && pj.features || [])) {
    if (!f.geometry) continue; const p = f.properties || {};
    for (const r of rings(f.geometry)) poly(r, 'CADASTRE');
    try { const c = turf.pointOnFeature(f).geometry.coordinates; txt(c, String(p.section || '').replace(/^0/, '') + ' ' + Number(p.numero), 1.6, 'NUMEROS'); } catch (e) {}
  }
  for (const f of (bj && bj.features || [])) if (f.geometry) for (const r of rings(f.geometry)) poly(r, 'BATI');
  pts.forEach((q, i) => { const z = Z[i]; if (!(z > -100)) return; const [x, y] = l93(q[0], q[1]); L(0, 'POINT', 8, 'ALTI', 10, f2(x), 20, f2(y), 30, f2(z)); L(0, 'TEXT', 8, 'ALTI', 10, f2(x + 0.6), 20, f2(y + 0.6), 30, f2(z), 40, 1.2, 1, z.toFixed(1)); });
  L(0, 'ENDSEC', 0, 'EOF');
  return { bytes: new TextEncoder().encode(o.join('\r\n') + '\r\n'), nParc: (pj && pj.features || []).length, nBat: (bj && bj.features || []).length, nAlt: Z.filter(z => z > -100).length };
}
async function modulesPro(p, c, d) {
  const out = {}, jobs = [], pf = turf.feature(c.parcelGeom), insee = d.ref.insee;
  if (p === 'agent' || p === 'notaire') {
    jobs.push(safe(coproParcelle(d.ref.idu), null).then(v => { out.copro = v; }));
  }
  if (p === 'agent') {
    jobs.push(safe(loyersCommune(insee), null).then(v => { out.loyers = v; }));
    jobs.push(safe(communeStats(insee), null).then(v => { out.prix = v; }));
    jobs.push(safe(proximite(d.ref.centroid), null).then(v => { out.proxi = v; }));
  }
  if (p === 'moe') {
    out.zclim = zoneClimatique(insee, d.alti);
    if (!/^97/.test(depOf(insee))) jobs.push(safe(planDxf(pf), null).then(v => { out.dxf = v; }));
  }
  await Promise.all(jobs);
  return out;
}
'''
rep("  return null;\n}\n// ---------- Offre communale", "  return null;\n}\n" + HELP + "// ---------- Offre communale")

# Données du profil, collectées après l'assemblage (délai borné : le rapport part même si une source ne répond pas)
rep("  d.projet = projetCle(m.projet);\n", """  d.projet = projetCle(m.projet);
  d.profil = profilCle(m.profil);
  if (d.profil && d.profil !== 'particulier') { try { d.pro = await withTimeout(modulesPro(d.profil, c, d), 30000); } catch (e) { console.warn('modules profil', String(e && e.message || e).slice(0, 160)); d.pro = {}; } }
""")

# Couverture : le profil figure sous le titre
rep("""  cover.drawText('RAPPORT D\\'URBANISME', { x: M, y: cy, size: 10, font: B, color: C.t });""",
    """  cover.drawText(clean('RAPPORT D\\'URBANISME' + (d.profil && d.profil !== 'particulier' ? ' · PRÉPARÉ POUR : ' + PROFILS[d.profil].toUpperCase() : '')), { x: M, y: cy, size: 10, font: B, color: C.t });""")

CH = r'''
  // =====================================================================
  // 0. L'ESSENTIEL POUR VOTRE MÉTIER (profil choisi à la commande)
  // =====================================================================
  if (d.profil && PROFIL_TITRE[d.profil]) {
    const PT = PROFIL_TITRE[d.profil], P = d.pro || {}, RKp = d.risques || {}, zc = (d.zones || []).map(z => z.code).filter(Boolean);
    const eur = v => fmt(Math.round(v)) + ' €', m2e = v => (Math.round(v * 10) / 10).toFixed(1).replace('.', ',') + ' €/m²', dist = v => v < 1000 ? fmt(Math.round(v / 10) * 10) + ' m' : (v / 1000).toFixed(1).replace('.', ',') + ' km';
    ABOUT[PT] = PROFIL_ABOUT[d.profil];
    chapter(++CHN, PT, 'Rapport préparé pour : ' + PROFILS[d.profil] + '. Les chapitres suivants détaillent chaque point ; aucune information réglementaire n\'est retirée.');
    if (d.profil === 'agent') {
      h3('Prix et loyers du secteur');
      const PX = P.prix, LY = P.loyers, rows = [];
      if (PX && PX.maison && PX.maison.median) rows.push(['Maison', fmt(Math.round(PX.maison.median)) + ' €/m²', fmt(PX.maison.count) + ' ventes', LY && LY.mai ? m2e(LY.mai.m2) + ' (' + m2e(LY.mai.lo) + ' à ' + m2e(LY.mai.hi) + ')' : 'Non publié']);
      if (PX && PX.appartement && PX.appartement.median) rows.push(['Appartement', fmt(Math.round(PX.appartement.median)) + ' €/m²', fmt(PX.appartement.count) + ' ventes', LY && LY.app ? m2e(LY.app.m2) + ' (' + m2e(LY.app.lo) + ' à ' + m2e(LY.app.hi) + ')' : 'Non publié']);
      if (!rows.length && LY) { if (LY.mai) rows.push(['Maison', 'Non publié', '', m2e(LY.mai.m2)]); if (LY.app) rows.push(['Appartement', 'Non publié', '', m2e(LY.app.m2)]); }
      if (rows.length) {
        table([{ label: 'Type de bien', w: 0.2, bold: true }, { label: 'Prix médian de vente', w: 0.24 }, { label: 'Ventes', w: 0.16 }, { label: 'Loyer mensuel au m²', w: 0.4 }], rows);
        const yl = [];
        if (PX && PX.maison && PX.maison.median && LY && LY.mai) yl.push('maison ' + (LY.mai.m2 * 12 / PX.maison.median * 100).toFixed(1).replace('.', ',') + ' %');
        if (PX && PX.appartement && PX.appartement.median && LY && LY.app) yl.push('appartement ' + (LY.app.m2 * 12 / PX.appartement.median * 100).toFixed(1).replace('.', ',') + ' %');
        if (yl.length) text('Rendement locatif brut indicatif (loyer annuel rapporté au prix médian) : ' + yl.join(', ') + '. Ce repère moyen ne remplace pas l\'estimation du bien.', { size: 9.5 });
        text('Sources : prix médians des ventes de la commune (DVF, DGFiP et Etalab) ; loyers d\'annonce prédits au m² par la Carte des loyers ' + (LY ? LY.annee : 2025) + ' du ministère chargé du logement, avec leur fourchette de prédiction' + (LY && ((LY.mai && !LY.mai.commune) || (LY.app && !LY.app.commune)) ? ' (estimation établie sur un groupe de communes voisines, faute d\'annonces suffisantes dans la commune)' : '') + '.', { size: 8.5, color: C.muet });
      } else note('Prix et loyers non publiés pour cette commune par les sources officielles. Les ventes réelles du secteur figurent au chapitre « Valeur de marché » ou « Environnement et marché immobilier ».');
      h3('Diagnostic de performance énergétique');
      const DP = (d.dpe || [])[0];
      if (DP) {
        kvn([['Dernier DPE enregistré', [DP.dpe ? 'Étiquette énergie ' + DP.dpe : '', DP.ges ? 'climat ' + DP.ges : ''].filter(Boolean).join(', ')], ['Date', DP.date], ['Logement', [DP.type, DP.surf ? fmt(DP.surf) + ' m²' : '', DP.annee ? 'construit ' + String(DP.annee).toLowerCase() : ''].filter(Boolean).join(' · ')], ['Adresse', DP.adresse], ['Numéro ADEME', DP.num]]);
        if ((d.dpe || []).length > 1) text((d.dpe.length - 1) + ' autre(s) DPE enregistré(s) à cette adresse : voir le chapitre « Opportunités autour du terrain » ou la base de l\'ADEME.', { size: 9 });
        if (/^[FG]$/.test(DP.dpe)) note('Logement classé ' + DP.dpe + ' : un audit énergétique est obligatoire pour la vente d\'une maison individuelle ou d\'un immeuble en monopropriété classé F ou G (code de la construction et de l\'habitation, art. L. 126-28-1). Location : les logements G sont interdits à la location depuis le 1er janvier 2025 (décence énergétique), les F le seront en 2028.', 'cond');
      } else text('Aucun DPE enregistré sur cette parcelle dans la base de l\'ADEME.', { size: 9.5 });
    }
    if (d.profil === 'agent' || d.profil === 'notaire') {
      h3('Copropriété');
      const CP = P.copro;
      if (CP && CP.length) CP.slice(0, 3).forEach(x => kvn([['Copropriété', (x.nom || 'Sans nom d\'usage') + ' · immatriculation ' + x.immat], ['Lots', [x.lots ? fmt(x.lots) + ' lots' : '', x.hab ? fmt(x.hab) + ' à usage d\'habitation' : '', x.park ? fmt(x.park) + ' de stationnement' : ''].filter(Boolean).join(', ')], ['Construction', x.periode], ['Règlement de copropriété', x.reglement], ['Syndic', [x.syndic, x.mandat].filter(Boolean).join(' · ')]]));
      else text(CP ? 'Aucune copropriété immatriculée sur cette parcelle au registre national (ANAH).' : 'Registre national des copropriétés momentanément indisponible : à vérifier sur registre-coproprietes.gouv.fr.', { size: 9.5 });
      text('Source : registre national d\'immatriculation des copropriétés (ANAH), données déclarées par les syndics.', { size: 8.5, color: C.muet });
    }
    if (d.profil === 'agent') {
      h3('Commerces, écoles, santé et transports');
      const PR = P.proxi;
      if (PR && PR.length) {
        table([{ label: 'Service', w: 0.32, bold: true }, { label: 'Le plus proche', w: 0.46 }, { label: 'Distance', w: 0.22 }], PR.map(x => [x.cat, x.nom || 'Nom non renseigné', dist(x.d)]));
        text('Distances à vol d\'oiseau depuis le centre de la parcelle, dans un rayon de 1,5 km (arrêts de bus), 3 km (commerces, écoles, santé) et 8 km (gares). Source : © les contributeurs d\'OpenStreetMap.', { size: 8.5, color: C.muet });
      } else text('Aucun service recensé dans le rayon étudié, ou source momentanément indisponible.', { size: 9.5 });
    }
    if (d.profil === 'notaire') {
      h3('Points à contrôler avant l\'acte');
      const inf = (d.infos || []).filter(x => /pr[ée]emption/i.test(x.label + ' ' + x.typeLabel)).map(x => x.label);
      const sup = d.sups || [], agri = (d.zones || []).some(z => /^(A|N)/i.test(String(z.code || '')));
      const rows = [
        ['Document d\'urbanisme et zone', d.doc ? d.doc.typeLabel + (d.doc.date ? ', approuvé le ' + d.doc.date : '') + (zc.length ? ' · zone ' + zc.join(', ') : '') : (zc.length ? 'Zone ' + zc.join(', ') : 'Voir le chapitre'), 'Règles d\'urbanisme applicables'],
        ['Servitudes d\'utilité publique', sup.length ? sup.length + ' servitude(s) : ' + sup.slice(0, 3).map(x => x.typeLabel).join(' ; ') + (sup.length > 3 ? '…' : '') : 'Aucune publiée au Géoportail de l\'Urbanisme', 'Règles d\'urbanisme applicables'],
        ['Droit de préemption urbain', inf.length ? 'Périmètre publié : ' + inf.slice(0, 2).join(' ; ') : 'Aucun périmètre publié au Géoportail ; le DPU n\'est pas toujours numérisé : à confirmer auprès de la mairie (déclaration d\'intention d\'aliéner)', 'Règles d\'urbanisme applicables'],
        ['Préemption SAFER', agri ? 'Terrain en zone agricole ou naturelle : préemption SAFER à examiner' : 'Sans objet a priori (zone urbaine ou à urbaniser)', agri ? 'Conditions de vente du terrain' : ''],
        ['Architecte des Bâtiments de France', d.verdict && d.verdict.abf === 'sur' ? 'Accord obligatoire (abords de monument ou site protégé)' : d.verdict && d.verdict.abf === 'probable' ? 'Avis probable' : 'Non concerné d\'après les servitudes publiées', 'Règles d\'urbanisme applicables'],
        ['État des risques (ERP)', (RKp.ppr && RKp.ppr.length ? RKp.ppr.length + ' plan(s) ou atlas de risques · ' : '') + (RKp.sismique || 'sismicité non renseignée') + ' · formulaire pré-rempli en annexe', 'État des risques (ERP) pré-rempli'],
        ['Catastrophes naturelles', (RKp.catnat || []).length ? (RKp.catnat || []).length + ' arrêté(s) de reconnaissance dans la commune' : 'Aucun arrêté recensé dans la commune', 'Risques naturels et technologiques'],
        ['Sites et sols pollués', RKp.sis && RKp.sis.length ? 'Secteur d\'information sur les sols : ' + RKp.sis.join(', ') : 'Aucun secteur d\'information sur les sols publié sur la parcelle', 'Risques naturels et technologiques'],
        ['Copropriété', P.copro && P.copro.length ? P.copro.length + ' copropriété(s) immatriculée(s) sur la parcelle' : P.copro ? 'Aucune immatriculée' : 'Registre indisponible', 'Ce chapitre']
      ];
      table([{ label: 'Point', w: 0.28, bold: true }, { label: 'Résultat', w: 0.47 }, { label: 'Chapitre', w: 0.25 }], rows, { size: 8.5 });
      text('Ces résultats proviennent des bases officielles publiées en ligne ; ils ne remplacent ni le certificat d\'urbanisme, ni les pièces obtenues auprès des administrations.', { size: 8.5, color: C.muet });
    }
    if (d.profil === 'moe') {
      const K = d.calc || {}, an = d.reglement && d.reglement.analysis;
      h3('Cadre technique du terrain');
      const ZC = P.zclim;
      kvn([
        ['Zone du document d\'urbanisme', zc.length ? zc.join(', ') + (d.doc ? ' · ' + d.doc.typeLabel : '') : null],
        ['Surface du terrain', R.contenance ? fmt(R.contenance) + ' m² (cadastre)' : null],
        ['Emprise au sol maximale', K.empMax ? fmt(Math.round(K.empMax)) + ' m²' + (K.empPct != null ? ' (' + K.empPct + ' %)' : '') : null],
        ['Hauteur', (() => { try { return typeof hauteurTexte === 'function' ? hauteurTexte(d) : null; } catch (e) { return null; } })()],
        ['Recul des limites séparatives', K.rl ? String(K.rl).replace('.', ',') + ' m' : null],
        ['Zone climatique RE2020', ZC ? (ZC.dom ? 'Outre-mer : la RE2020 ne s\'applique pas (réglementation thermique, acoustique et aération propre aux DOM)' : ZC.zone + (ZC.classe ? ', ' + ZC.classe + (ZC.alt != null ? ' (environ ' + fmt(ZC.alt) + ' m)' : '') : '')) : null],
        ['Zone de sismicité', RKp.sismique || null],
        ['Retrait-gonflement des argiles', RKp.rga || null],
        ['Potentiel radon', RKp.radon || null],
        ['Altitude et pente', d.alti ? fmt(d.alti.min) + ' à ' + fmt(d.alti.max) + ' m · pente estimée ' + d.alti.slope + ' %' : null],
        ['Assainissement', d.eau && (d.eau.ac || d.eau.anc) ? [d.eau.ac ? 'collectif dans la commune' : '', d.eau.anc ? 'non collectif (SPANC)' : ''].filter(Boolean).join(' · ') : null]
      ]);
      if (ZC && !ZC.dom) text('Zones climatiques : annexe I de l\'arrêté du 26 octobre 2010, reprise par l\'arrêté du 4 août 2021 (RE2020). L\'altitude module les exigences de la RE2020.', { size: 8.5, color: C.muet });
      if (/moyen|fort/i.test(String(RKp.rga || ''))) note('Exposition ' + String(RKp.rga).toLowerCase() + ' au retrait-gonflement des argiles : étude géotechnique préalable à la vente du terrain et étude de conception avant la construction, obligatoires (code de la construction et de l\'habitation, art. L. 132-4 à L. 132-9).', 'cond');
      h3('Pièces du permis de construire d\'une maison individuelle');
      ['PCMI1 Plan de situation du terrain', 'PCMI2 Plan de masse des constructions', 'PCMI3 Plan en coupe du terrain et de la construction', 'PCMI4 Notice décrivant le terrain et le projet',
       'PCMI5 Plan des façades et des toitures', 'PCMI6 Document graphique d\'insertion du projet', 'PCMI7 Photographie de l\'environnement proche', 'PCMI8 Photographie du paysage lointain'].forEach(t2 => bullet(t2, { size: 9.5 }));
      const extra = ['Attestation de prise en compte de la réglementation environnementale (RE2020), à joindre pour une construction neuve (code de l\'urbanisme, art. R. 431-16).'];
      if (d.eau && d.eau.anc && !d.eau.ac) extra.push('Commune en assainissement non collectif : attestation de conformité du projet d\'installation délivrée par le SPANC (art. R. 431-16).');
      if (RKp.ppr && RKp.ppr.length) extra.push('Plan de prévention des risques : si son règlement impose une étude préalable, attestation de l\'architecte ou de l\'expert certifiant sa réalisation (art. R. 431-16).');
      if (d.verdict && (d.verdict.abf === 'sur' || d.verdict.abf === 'probable')) extra.push('Abords de monument ou site protégé : dossier soumis à l\'architecte des Bâtiments de France ; soigner la notice et l\'insertion paysagère.');
      extra.push('Recours à un architecte obligatoire au-delà de 150 m² de surface de plancher (personne physique construisant pour elle-même).');
      h4('Selon le projet et le terrain');
      extra.forEach(t2 => bullet(t2, { size: 9.5 }));
      h3('Plan du terrain au format DXF');
      if (P.dxf && P.dxf.bytes) {
        try { await pdf.attach(P.dxf.bytes, ('Plan-' + R.insee + '-' + R.section + '-' + R.numero + '.dxf'), { mimeType: 'application/dxf', description: 'Plan du terrain en Lambert 93 (RGF93) : parcelle, cadastre voisin, bâtiments, points d\'altitude', creationDate: new Date(), modificationDate: new Date() }); } catch (e) { console.warn('dxf', e); }
        text('Le fichier « Plan-' + R.insee + '-' + R.section + '-' + R.numero + '.dxf » est joint à ce PDF. Pour l\'ouvrir : dans Adobe Acrobat Reader, cliquez sur l\'icône trombone (pièces jointes), puis enregistrez le fichier et ouvrez-le dans votre logiciel de dessin (AutoCAD, ArchiCAD, Revit, SketchUp, DraftSight…).', { size: 9.5 });
        kvn([['Système de coordonnées', 'Lambert 93 (RGF93, EPSG:2154), en mètres'], ['Calques', 'PARCELLE (le terrain), CADASTRE et NUMEROS (parcelles voisines), BATI (bâtiments), ALTI (points d\'altitude cotés)'], ['Contenu', fmt(P.dxf.nParc) + ' parcelles, ' + fmt(P.dxf.nBat) + ' bâtiments, ' + fmt(P.dxf.nAlt) + ' points d\'altitude sur une grille de 11 × 11']]);
        text('Sources : plan cadastral (DGFiP, via l\'IGN), BD TOPO et RGE ALTI de l\'IGN. Le plan cadastral n\'a pas la précision d\'un relevé de géomètre : il ne remplace pas le bornage ni le relevé topographique.', { size: 8.5, color: C.muet });
      } else text(/^97/.test(depOf(R.insee)) ? 'Plan DXF non proposé en outre-mer (projection différente du Lambert 93).' : 'Plan DXF momentanément indisponible (source de l\'IGN sans réponse) : il peut être régénéré sur demande à contact@terrenurbanisme.com.', { size: 9.5 });
    }
  }
'''
rep("  // =====================================================================\n  // 1. IDENTIFICATION\n", CH + "  // =====================================================================\n  // 1. IDENTIFICATION\n")

# Commande payée : le profil est enregistré avec le dossier
rep("projet: projetCle(m.projet), formule: m.formule === 'synthese' ? 'synthese' : 'complet'\n  }, { onConflict",
    "projet: projetCle(m.projet), profil: profilCle(m.profil), formule: m.formule === 'synthese' ? 'synthese' : 'complet'\n  }, { onConflict")
# Rapport sur crédit (professionnels) : profil choisi, sinon métier du compte
rep("  const projet = projetCle(b.projet);\n  const m = { user_id: u.user.id, insee, section, numero, commune, projet };",
    "  const projet = projetCle(b.projet);\n  const profil = profilCle(b.profil) || await profilCompte(u.user.id);\n  const m = { user_id: u.user.id, insee, section, numero, commune, projet, profil };")
rep("amount_total: 0, status: 'pending', projet, agent:", "amount_total: 0, status: 'pending', projet, profil, agent:")
# Régénération : même profil
rep("commune: row.commune, projet: row.projet }, row.order_ref, row.email, row.origine);", "commune: row.commune, projet: row.projet, profil: row.profil }, row.order_ref, row.email, row.origine);")
# Aperçu de test : profil en paramètre
rep("const m = { insee, section, numero, commune: url.searchParams.get('commune') || '', projet: url.searchParams.get('projet') || null };",
    "const m = { insee, section, numero, commune: url.searchParams.get('commune') || '', projet: url.searchParams.get('projet') || null, profil: url.searchParams.get('profil') || null };")

open(p, 'w', encoding='utf-8').write(s)
print('ok profils')
