# Rapport : espèces protégées observées autour du terrain, conséquences, démarches et coûts
# Observations naturalistes : GBIF (qui agrège les données de l'INPN / OpenObs et du SINP). Statuts de protection : TAXREF / INPN (data/especes-protegees.json).
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()

def rep(old, new, label):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable ou multiple : ' + label)
    s = s.replace(old, new)

FN = r"""// ---------- Espèces protégées observées autour du terrain (observations GBIF, dont INPN/OpenObs ; statuts de protection TAXREF/INPN) ----------
const ANC_REG = { '75': 11, '77': 11, '78': 11, '91': 11, '92': 11, '93': 11, '94': 11, '95': 11, '08': 21, '10': 21, '51': 21, '52': 21, '02': 22, '60': 22, '80': 22, '27': 23, '76': 23,
  '18': 24, '28': 24, '36': 24, '37': 24, '41': 24, '45': 24, '14': 25, '50': 25, '61': 25, '21': 26, '58': 26, '71': 26, '89': 26, '59': 31, '62': 31, '54': 41, '55': 41, '57': 41, '88': 41,
  '67': 42, '68': 42, '25': 43, '39': 43, '70': 43, '90': 43, '44': 52, '49': 52, '53': 52, '72': 52, '85': 52, '22': 53, '29': 53, '35': 53, '56': 53, '16': 54, '17': 54, '79': 54, '86': 54,
  '24': 72, '33': 72, '40': 72, '47': 72, '64': 72, '09': 73, '12': 73, '31': 73, '32': 73, '46': 73, '65': 73, '81': 73, '82': 73, '19': 74, '23': 74, '87': 74,
  '01': 82, '07': 82, '26': 82, '38': 82, '42': 82, '69': 82, '73': 82, '74': 82, '03': 83, '15': 83, '43': 83, '63': 83, '11': 91, '30': 91, '34': 91, '48': 91, '66': 91,
  '04': 93, '05': 93, '06': 93, '13': 93, '83': 93, '84': 93, '2A': 94, '2B': 94, '971': '01', '972': '02', '973': '03' };
let PROT_SP = null;
function groupeEsp(sp) {
  const k = sp.kingdom, c = sp.class || '', o = sp.order || '';
  if (k === 'Plantae') return 'Plante';
  if (k === 'Fungi') return 'Champignon';
  if (c === 'Aves') return 'Oiseau';
  if (c === 'Mammalia') return 'Mammifère';
  if (c === 'Amphibia') return 'Amphibien';
  if (c === 'Reptilia' || c === 'Squamata' || c === 'Testudines' || o === 'Testudines' || o === 'Squamata') return 'Reptile';
  if (c === 'Insecta') return 'Insecte';
  if (c === 'Arachnida') return 'Araignée';
  if (c === 'Gastropoda' || c === 'Bivalvia') return 'Mollusque';
  if (c === 'Actinopterygii' || c === 'Elasmobranchii') return 'Poisson';
  return 'Autre';
}
async function especesProtegees(pf, insee) {
  const c = turf.centroid(pf).geometry.coordinates, R = 1, t0 = Date.now();
  if (!PROT_SP) PROT_SP = getJSON((Deno.env.get('SITE_URL') || 'https://terrenurbanisme.com').replace(/\/$/, '') + '/data/especes-protegees.json', 20000).catch(() => null);
  const prot = await PROT_SP; if (!prot || !prot.especes) { PROT_SP = null; return null; }
  const dep = depOf(insee), reg = ANC_REG[dep];
  const applic = e => (e[0] === 'PN' && (e[1] === 'TERFXFR' || e[1] === 'ETATFRA' || e[1] === 'INSEED' + dep || e[1] === 'TER' + dep)) || (e[0] === 'PR' && reg != null && e[1] === 'INSEER' + reg) || (e[0] === 'PD' && e[1] === 'INSEED' + dep);
  const base = 'https://api.gbif.org/v1/occurrence/search?geoDistance=' + c[1].toFixed(5) + ',' + c[0].toFixed(5) + ',' + R + 'km&occurrenceStatus=PRESENT&hasGeospatialIssue=false&year=1990,2100&limit=0';
  const f = await getJSON(base + '&facet=speciesKey&facetLimit=600', 20000);
  const keys = ((f.facets || [])[0] || { counts: [] }).counts;
  const found = [];
  for (let i = 0; i < keys.length; i += 25) {
    if (Date.now() - t0 > 25000) break;
    const part = await Promise.all(keys.slice(i, i + 25).map(k => getJSON('https://api.gbif.org/v1/species/' + k.name, 10000).then(sp => ({ sp, n: k.count, key: k.name })).catch(() => null)));
    for (const x of part) {
      if (!x || !x.sp) continue;
      const nm = String(x.sp.canonicalName || x.sp.species || '').toLowerCase().split(/\s+/).slice(0, 2).join(' ');
      const st = (prot.especes[nm] || []).filter(applic);
      if (st.length) found.push({ ...x, st });
    }
  }
  found.sort((a, b) => b.n - a.n);
  const top = found.slice(0, 14);
  await Promise.all(top.map(async x => {
    const [vn, yr] = await Promise.all([
      getJSON('https://api.gbif.org/v1/species/' + x.key + '/vernacularNames?limit=200', 8000).catch(() => null),
      getJSON(base + '&speciesKey=' + x.key + '&facet=year&facetLimit=80', 8000).catch(() => null)]);
    const fr = vn && (vn.results || []).find(v => v.language === 'fra');
    x.fr = fr ? fr.vernacularName.charAt(0).toUpperCase() + fr.vernacularName.slice(1) : null;
    const ys = yr && ((yr.facets || [])[0] || { counts: [] }).counts.map(v => Number(v.name)).filter(Boolean);
    x.der = ys && ys.length ? Math.max(...ys) : null;
  }));
  const lab = t => t === 'PN' ? 'Nationale' : t === 'PR' ? 'Régionale' : 'Départementale';
  return {
    rayon: R, obs: f.count || 0, nb: found.length,
    liste: top.map(x => {
      const types = [...new Set(x.st.map(e => e[0]))].sort((a, b) => 'PN PR PD'.indexOf(a) - 'PN PR PD'.indexOf(b));
      const hab = x.st.some(e => /article 2|article 3/i.test(e[4] || '') && e[0] === 'PN');
      return { sci: x.sp.canonicalName, fr: x.fr, groupe: groupeEsp(x.sp), prot: types.map(lab).join(' + ') + (hab ? ' (espèce et habitat)' : ''), n: x.n, der: x.der };
    }),
    ms: Date.now() - t0
  };
}
async function extras(b) {"""
rep("async function extras(b) {", FN, 'extras')
rep("safe(eauService(INS), null)]);\n  const [opp, soleil]",
    "safe(eauService(INS), null), safe(withTimeoutC(especesProtegees(pf, INS), 40000), null)]);\n  const [opp, soleil]", 'promise')
rep("const [pm, dpe, ta, elec, mairie, eau] = await Promise.all([", "const [pm, dpe, ta, elec, mairie, eau, especes] = await Promise.all([", 'destructure')
rep("return { pm, dpe, ta, elec, mairie, eau, opp, soleil };", "return { pm, dpe, ta, elec, mairie, eau, opp, soleil, especes };", 'retour')
rep(".then(x => x ? [x.pm, x.dpe, x.ta, x.elec, x.mairie, x.eau, x.opp, x.soleil] : [null, null, null, null, null, null, null, null]);",
    ".then(x => x ? [x.pm, x.dpe, x.ta, x.elec, x.mairie, x.eau, x.opp, x.soleil, x.especes] : [null, null, null, null, null, null, null, null, null]);", 'map')
rep("const [pmData, dpeData, taData, elecData, mairieData, eauData, oppData, soleilData] = await extraP;",
    "const [pmData, dpeData, taData, elecData, mairieData, eauData, oppData, soleilData, especesData] = await extraP;", 'await')
rep("eau: eauData, opp: oppData, soleil: soleilData,", "eau: eauData, opp: oppData, soleil: soleilData, especes: especesData,", 'collecte')
rep("eau: c.eau, opp: c.opp, soleil: c.soleil,", "eau: c.eau, opp: c.opp, soleil: c.soleil, especes: c.especes,", 'donnees')

SEC = r"""  } else text('La parcelle n\'est concernée par aucun site Natura 2000, ZNIEFF, parc ou réserve naturelle.', { size: 9.5 });
  // Espèces protégées observées autour du terrain
  {
    const SP = d.especes;
    h3('Espèces protégées observées près du terrain');
    if (!SP) text('Les bases d\'observations naturalistes n\'ont pas pu être consultées lors de l\'édition de ce rapport. Avant d\'engager des travaux, faites vérifier la présence d\'espèces protégées par un écologue.', { size: 9 });
    else if (!SP.liste.length) {
      note('Aucune espèce protégée n\'a été signalée dans un rayon de ' + SP.rayon + ' km autour du terrain depuis 1990 (' + fmt(SP.obs) + ' observations naturalistes recensées dans ce rayon). Cela ne garantit pas leur absence : un secteur peu prospecté peut abriter des espèces non signalées.', 'ok');
    } else {
      text(fmt(SP.nb) + ' espèce' + (SP.nb > 1 ? 's protégées ont' : ' protégée a') + ' été observée' + (SP.nb > 1 ? 's' : '') + ' dans un rayon de ' + SP.rayon + ' km autour du terrain depuis 1990' + (SP.nb > SP.liste.length ? ' ; les ' + SP.liste.length + ' plus fréquemment signalées figurent ci-dessous' : '') + '.', { size: 9.5 });
      table([{ label: 'ESPÈCE', w: 0.40, bold: true }, { label: 'GROUPE', w: 0.14 }, { label: 'PROTECTION', w: 0.26 }, { label: 'OBSERVATIONS', w: 0.20 }],
        SP.liste.map(s => [s.fr ? s.fr + ' (' + s.sci + ')' : s.sci, s.groupe, s.prot, fmt(s.n) + (s.der ? ' · dernière en ' + s.der : '')]));
      note('Une observation à proximité ne signifie pas que l\'espèce vit sur le terrain. Mais si elle y est présente, il est interdit de détruire, capturer ou déranger les individus et, pour la plupart de ces espèces, de détruire leurs lieux de reproduction et de repos (articles L. 411-1 et suivants du Code de l\'environnement). L\'infraction est punie de 3 ans d\'emprisonnement et 150 000 € d\'amende.', 'cond');
    }
    h4('Que faire avant de construire ?');
    bullet('Faire réaliser un pré-diagnostic écologique : un écologue visite le terrain et confirme ou écarte la présence d\'espèces protégées et de leurs habitats (haies, vieux arbres, murets, zones humides, maquis).', { size: 9 });
    bullet('Si un enjeu est confirmé : inventaire faune-flore aux saisons utiles (printemps et été en général), puis mesures pour éviter et réduire l\'impact : implantation de la maison sur la partie la moins sensible, travaux hors période de reproduction, clôture de chantier adaptée, déplacement d\'individus par un spécialiste habilité.', { size: 9 });
    bullet('Si la destruction d\'individus ou d\'habitats ne peut pas être évitée : demande de dérogation « espèces protégées » auprès de la préfecture (DREAL), avec avis du conseil scientifique. Comptez 4 à 12 mois d\'instruction, à anticiper avant le dépôt du permis.', { size: 9 });
    h4('Combien prévoir ?');
    kvn([
      ['Pré-diagnostic écologique', '800 à 2 000 € (une visite et une note de synthèse)'],
      ['Inventaire faune-flore', '3 000 à 10 000 € selon la surface et le nombre de passages'],
      ['Mesures d\'évitement et de réduction', '500 à 5 000 € (balisage, calendrier, suivi de chantier)'],
      ['Dossier de dérogation', '8 000 à 25 000 €, hors mesures de compensation éventuelles']
    ], { lw: 0.36 });
    text('Ordres de prix indicatifs, honoraires de bureaux d\'études en environnement. Pour une maison sur un terrain déjà entouré de constructions, le pré-diagnostic suffit le plus souvent.', { size: 8, color: C.muet });
    text('Sources : statuts de protection TAXREF et base de connaissance des statuts (INPN, Muséum national d\'Histoire naturelle) ; observations naturalistes GBIF, qui rassemble notamment les données de l\'INPN et du SINP.', { size: 8, color: C.muet });
  }"""
rep("  } else text('La parcelle n\\'est concernée par aucun site Natura 2000, ZNIEFF, parc ou réserve naturelle.', { size: 9.5 });", SEC, 'section')
open(p, 'w', encoding='utf-8').write(s)
print('patch especes appliqué')
