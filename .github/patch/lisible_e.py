"""Lisibilité E : OSM fiable, téléphones lisibles, coupures typographiques, ajustements risques et réseaux."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag, n=1):
    global s
    c = s.count(a)
    if c != n: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)

# Coupures : ne jamais commencer une ligne par %, €, :, ?, », une unité, ni couper un nombre à milliers
rep("    const words = clean(text).split(' '); const lines = []; let cur = '';",
    "    const words = []; for (const w of clean(text).split(' ')) { const pv = words.length ? words[words.length - 1] : null; if (pv != null && (/^(%|€|€\\/m²|m²|m|km|h|:|;|\\?|!|»)$/.test(w) || pv === '«' || (/^\\d{3}(?!\\d)/.test(w) && /^\\d{1,3}$/.test(pv)))) words[words.length - 1] = pv + ' ' + w; else words.push(w); } const lines = []; let cur = '';", 'wrap')

# OpenStreetMap : requête GET, délai plus long, serveur de secours
rep("    const x = await fetch('https://overpass-api.de/api/interpreter', { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'TerrenUrbanisme/1.0' }, signal: AbortSignal.timeout(14000) });\n    if (x.ok) OSM =",
    "    let x = null;\n    for (const host of ['https://overpass-api.de/api/interpreter', 'https://overpass.private.coffee/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']) { try { x = await fetch(host + '?data=' + encodeURIComponent(q), { headers: { 'User-Agent': 'TerrenUrbanisme/1.0' }, signal: AbortSignal.timeout(25000) }); if (x.ok) break; } catch (e) { x = null; } }\n    if (x && x.ok) OSM =", 'osm')
# Téléphones au format français
rep("  const OSMK = {", "  const telFR = t => { let v = String(t || '').split(/[;,]/)[0].replace(/[^\\d+]/g, ''); if (v.startsWith('+33')) v = '0' + v.slice(3); if (v.startsWith('0033')) v = '0' + v.slice(4); return /^0\\d{9}$/.test(v) ? v.replace(/(\\d{2})(?=\\d)/g, '$1 ') : String(t || ''); };\n  const OSMK = {", 'telfn')
rep("out.push({ cat: lab, nom: os.nom, d: Math.round(os.d), tel: os.tel, mail: os.mail });", "out.push({ cat: lab, nom: os.nom, d: Math.round(os.d), tel: telFR(os.tel), mail: os.mail });", 'telosm')
rep("d: Math.round(dm(r.position.lat, r.position.lon)), tel: r.telephone || '', mail: r.mail || '' }", "d: Math.round(dm(r.position.lat, r.position.lon)), tel: telFR(r.telephone), mail: r.mail || '' }", 'telecole')
# telFR doit exister avant les écoles : on le déclare en tête de proximite
s = s.replace("  const telFR = t => {", "  const telFR_ = t => {", 1)
rep("async function proximite(ctr, insee) {\n", "async function proximite(ctr, insee) {\n  const telFR = t => { let v = String(t || '').split(/[;,]/)[0].replace(/[^\\d+]/g, ''); if (v.startsWith('+33')) v = '0' + v.slice(3); if (v.startsWith('0033')) v = '0' + v.slice(4); return /^0\\d{9}$/.test(v) ? v.replace(/(\\d{2})(?=\\d)/g, '$1 ') : String(t || ''); };\n", 'telhead')

# Risques : sismicité 1 non affichée comme risque ; plan de prévention sans répétition ; ICPE ; pas de doublon ERP en fin de 5.4
rep("    const PRES = RK.addressLevel ? ALLR.filter(r => r.present) : ALLR.filter(r => /existant|concern/i.test(String(r.commune || '')) || r.present);",
    "    const z1 = Number((String(RK.sismique || '').match(/\\d/) || [])[0]) === 1;\n    const PRES = (RK.addressLevel ? ALLR.filter(r => r.present) : ALLR.filter(r => /existant|concern/i.test(String(r.commune || '')) || r.present)).filter(r => !(r.key === 'seisme' && z1));", 'z1')
rep("    if (PM1.length) note('Plan de prévention : ' + PM1.map(x => x.label || 'plan des risques naturels').join(', ') + '. ' + supExpl('pm1', PM1[0].label), 'cond');",
    "    if (PM1.length) note('Plan de prévention : ' + PM1.map(x => x.label || 'plan des risques naturels').join(', ') + ' (voir les servitudes, chapitre 2). Demandez en mairie dans quelle zone du plan se trouve le terrain : c\\'est elle qui dit si l\\'on peut construire et à quelles conditions.', 'cond');", 'pm1')
rep("    if (ABS.length) text('Recherchés et non relevés à l\\'adresse : ' + ABS.map(r => r.label.charAt(0).toLowerCase() + r.label.slice(1)).join(', ') + '.', { size: 8.5, color: C.muet });",
    "    const ABS2 = ABS.concat(z1 ? ALLR.filter(r => r.key === 'seisme') : []);\n    if (ABS2.length) text('Recherchés et non relevés à l\\'adresse : ' + ABS2.map(r => r.key === 'seisme' ? 'séisme (zone 1, très faible : aucune règle pour une maison)' : r.label.charAt(0).toLowerCase() + r.label.slice(1)).join(', ') + '.', { size: 8.5, color: C.muet });", 'abs')
rep("    RK.icpe.forEach(i => bullet(i.replace(/ · Autres régimes/i, ' · activité suivie hors régime d\\'autorisation').replace(/ · Enregistrement/i, ' · régime d\\'enregistrement').replace(/ · Autorisation/i, ' · régime d\\'autorisation (le plus surveillé)'), { size: 9 }));",
    "    RK.icpe.forEach(i => bullet(i.replace(/ · Autres régimes/i, '').replace(/ · Enregistrement/i, ' · régime d\\'enregistrement').replace(/ · Autorisation/i, ' · régime d\\'autorisation (le plus surveillé)').replace(/ · Déclaration/i, ' · régime de déclaration'), { size: 9 }));", 'icpe')
rep("  text('Lors d\\'une vente ou d\\'une location, le vendeur ou le bailleur doit remettre un état des risques de moins de six mois, complété et signé, et l\\'information sur les sinistres indemnisés au titre des catastrophes naturelles.', { size: 8.5, color: C.muet });\n", "", 'erpdbl')

# Réseaux : renvoi corrigé, noms en casse normale, colonne fibre plus large
rep("Interroger le service des eaux (coordonnées ci-dessous)", "Interroger le service des eaux (coordonnées au point « Qui contacter pour les réseaux »)", 'renvoi')
rep("      const tc = t => t && t === t.toUpperCase() ? t.toLowerCase().replace(/(^|[\\s'’-])(\\p{L})/gu, (x, a, b) => a + b.toUpperCase()).replace(/\\b(De|Du|Des|La|Le|Les|Et|D'|L')\\b/g, w => w.toLowerCase()) : t;",
    "      const tc = t => String(t || '').replace(/\\b[A-ZÀ-Ý][A-ZÀ-Ý'’-]{2,}\\b/g, w => w.charAt(0) + w.slice(1).toLowerCase());", 'tc')
rep("table([{ label: 'DISTANCE', w: 0.14 }, { label: 'ADRESSE', w: 0.5 }, { label: 'ACCÈS DISPONIBLES', w: 0.36 }],", "table([{ label: 'DISTANCE', w: 0.12 }, { label: 'ADRESSE', w: 0.4 }, { label: 'ACCÈS DISPONIBLES', w: 0.48 }],", 'fibcol')
# Recul « 3m » : toujours « 3 m »
rep("        ['Recul des limites séparatives', K.rl ? String(K.rl).replace('.', ',') + ' m' : null],", "        ['Recul des limites séparatives', K.rl ? (isFinite(parseFloat(String(K.rl).replace(',', '.'))) ? String(parseFloat(String(K.rl).replace(',', '.'))).replace('.', ',') + ' m' : String(K.rl)) : null],", 'rl')
# Étapes : « Coût : sans frais »
s = s.replace("'Sans frais · réponse sous 2 mois'", "'sans frais · réponse sous 2 mois'").replace("], 'Sans frais', 'Mairie : ' + mair]", "], 'sans frais', 'Mairie : ' + mair]")
open(p, 'w', encoding='utf-8').write(s); print('ok E')

# --- suite E : informations du PLU expliquées, syndic identifié, argiles « important »
p2 = p; s = open(p2, encoding='utf-8').read()
def rep2(a, b, tag):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)
rep2("function supExpl(code, label) {", r"""const INF_ALL = { '02': 'Zone d\'aménagement concerté (ZAC)', '03': 'Préemption des espaces naturels sensibles', '04': 'Droit de préemption urbain', '05': 'Zone d\'aménagement différé', '07': 'Réseau de chaleur (développement prioritaire)', '08': 'Périmètre forestier', '09': 'Périmètre minier', '10': 'Zone de carrières', '11': 'Divisions soumises à déclaration', '12': 'Périmètre de sursis à statuer', '13': 'Programme d\'aménagement d\'ensemble', '14': 'Voie bruyante', '16': 'Site archéologique', '17': 'Zone à risque d\'exposition au plomb', '19': 'Zonage d\'assainissement', '20': 'Règlement local de publicité', '21': 'Projet de plan de prévention des risques', '22': 'Rives des plans d\'eau en montagne', '25': 'Espaces agricoles et naturels périurbains protégés', '27': 'Plan d\'exposition au bruit d\'un aérodrome', '30': 'Projet urbain partenarial', '31': 'Restriction de certains matériaux et énergies renouvelables', '32': 'Secteur de taxe d\'aménagement', '33': 'Droit de préemption commercial', '34': 'Opération d\'intérêt national', '35': 'Densité minimale', '36': 'Schéma d\'aménagement de plage', '37': 'Bois ou forêt relevant du régime forestier', '38': 'Secteur d\'information sur les sols', '39': 'Association foncière urbaine de projet', '99': 'Information particulière' };
const INF_EXPL = { '02': 'L\'aménageur de la zone fixe les surfaces et usages ; une participation aux équipements peut être demandée.', '03': 'Le Département peut acheter le terrain en priorité en cas de vente.', '04': 'La commune peut acheter en priorité en cas de vente : le notaire lui adresse une déclaration d\'intention d\'aliéner (DIA).', '05': 'Une collectivité peut acheter en priorité en cas de vente.', '07': 'Les constructions neuves doivent en principe se raccorder au réseau de chaleur.', '08': 'Les plantations d\'arbres y sont réglementées.', '09': 'Ancienne ou actuelle exploitation minière : sous-sol à faire vérifier.', '10': 'Exploitation de carrières possible ou passée à proximité.', '11': 'Toute division du terrain doit être déclarée en mairie avant la vente.', '12': 'La mairie peut suspendre sa réponse à un permis (jusqu\'à 2 ans) en raison d\'un projet d\'aménagement.', '13': 'Une participation au financement des équipements publics peut être demandée.', '14': 'Proximité d\'une voie bruyante : isolation acoustique renforcée obligatoire pour un logement.', '16': 'Des fouilles archéologiques préventives peuvent être prescrites avant les travaux.', '17': 'Pour vendre ou louer un logement construit avant 1949, un constat de risque d\'exposition au plomb est exigé.', '19': 'Indique si le terrain doit se raccorder aux égouts ou avoir une installation individuelle, et comment gérer les eaux de pluie.', '20': 'Enseignes et panneaux publicitaires encadrés.', '21': 'Un plan de prévention des risques est en préparation : ses règles pourraient bientôt s\'appliquer.', '22': 'Constructions limitées au bord des plans d\'eau.', '25': 'Espaces agricoles et naturels protégés : constructions très limitées.', '27': 'Bruit d\'avions : logements nouveaux limités et isolation renforcée.', '30': 'Une participation financière aux équipements publics peut être demandée.', '31': 'Certains matériaux ou équipements (panneaux solaires...) peuvent être interdits pour protéger le patrimoine.', '32': 'Un taux particulier de taxe d\'aménagement s\'applique.', '33': 'La commune peut acheter en priorité un fonds de commerce.', '34': 'Grand projet d\'aménagement conduit par l\'État.', '35': 'Une densité minimale de construction est imposée.', '36': 'Aménagements de plage encadrés.', '37': 'Forêt gérée par l\'Office national des forêts : défrichement très encadré.', '38': 'Sol potentiellement pollué : étude de sol obligatoire pour construire.', '39': 'Les propriétaires peuvent se regrouper pour un projet d\'aménagement.', '99': 'Information particulière : voir le règlement du PLU.' };
function supExpl(code, label) {""", 'inf')
rep2(".map(p => ({ label: p.libelle || p.txt || 'Information', typeLabel: 'Information du PLU' + (p.typeinf ? ' (type ' + p.typeinf + ')' : '') })), x => x.label);",
     ".map(p => { const cd = String(p.typeinf || '').padStart(2, '0').slice(0, 2); return { code: cd, label: p.libelle || p.txt || 'Information', typeLabel: INF_ALL[cd] || 'Information du PLU' }; }), x => x.label);", 'infmap')
rep2("    table([{ label: 'INFORMATION', w: 0.62 }, { label: 'TYPE', w: 0.38 }], d.infos.map(p => [p.label, p.typeLabel]));",
     "    table([{ label: 'INFORMATION', w: 0.4, bold: true }, { label: 'CE QUE CELA VEUT DIRE', w: 0.6 }], d.infos.map(p => [p.typeLabel + (p.label && p.label !== p.typeLabel && p.label !== 'Information' ? ' : ' + p.label : ''), INF_EXPL[p.code] || 'Information à prendre en compte : voir le règlement du PLU.']), { size: 8.5 });", 'inftab')
rep2("      mandat: r.mandat_en_cours_dans_la_copropriete || '',", "      mandat: r.mandat_en_cours_dans_la_copropriete || '', synNom: r.raison_sociale_du_representant_legal || '', synSiret: String(r.siret_representant_legal || '').replace(/\\D/g, ''),", 'syn')
rep2("['Syndic (contact)', [x.syndic, x.mandat].filter(Boolean).join(' · ')], ['Fiche officielle', 'https://www.registre-coproprietes.gouv.fr/']]));",
     "['Syndic', x.synNom ? x.synNom + (x.syndic ? ' (' + String(x.syndic).toLowerCase() + ')' : '') : [x.syndic, x.mandat].filter(Boolean).join(' · ')], ['Coordonnées du syndic', /^\\d{14}$/.test(x.synSiret || '') ? 'https://annuaire-entreprises.data.gouv.fr/etablissement/' + x.synSiret : null], ['Registre officiel', 'https://www.registre-coproprietes.gouv.fr/']]));", 'synrow')
rep2("return /moyen|fort/i.test(t) ? 'Le sol argileux", "return /moyen|fort|important|élevé/i.test(t) ? 'Le sol argileux", 'rga')
open(p2, 'w', encoding='utf-8').write(s); print('ok E2')

# --- suite E3 : l'implantation évite les bâtiments existants
s = open(p, encoding='utf-8').read()
def rep3(a, b, tag):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)
rep3("function implantation(K, geom, acces) {", "function implantation(K, geom, acces, bats) {", 'sig')
rep3("  const ringArea = r => {", "  const BAT = (bats || []).map(g => { try { const rr = g.type === 'MultiPolygon' ? g.coordinates.map(p => p[0]) : [g.coordinates[0]]; return rr.map(r => r.map(toL)); } catch (e) { return []; } }).flat().filter(r => r.length > 3);\n  const hitBat = Rr => BAT.some(b => b.some(q => inPoly(q, Rr)) || Rr.some(q => inPoly(q, b)) || inPoly([(Rr[0][0] + Rr[2][0]) / 2, (Rr[0][1] + Rr[2][1]) / 2], b));\n  const ringArea = r => {", 'bat')
rep3("          const R = rect(cx, cy, G.w, G.l, a); if (!fits(R, z)) continue;", "          const R = rect(cx, cy, G.w, G.l, a); if (!fits(R, z)) continue; if (BAT.length && hitBat(rect(cx, cy, G.w + 4, G.l + 4, a))) continue;", 'essai')
rep3("        if (fits(P, hz) && !P.some(q => inPoly(q, best.R))) cands.push(", "        if (fits(P, hz) && !P.some(q => inPoly(q, best.R)) && !(BAT.length && hitBat(rect(cx, cy, pw + 2, pl + 2, best.a)))) cands.push(", 'pool')
rep3("  if (!best) return { ok: false, maxFoot: Math.round(maxFoot) };", "  if (!best) return { ok: false, maxFoot: Math.round(maxFoot), bati: BAT.length > 0 };", 'nobest')
rep3("    if (!IP.ok) { note('La zone constructible est trop étroite", "    if (!IP.ok && IP.bati) { note('Le terrain est déjà bâti : l\\'espace libre restant dans la zone constructible ne permet pas d\\'implanter une maison courante à côté des bâtiments existants. Une extension ou une surélévation reste à étudier avec un architecte, dans la limite de l\\'emprise au sol autorisée.', 'cond'); return; }\n    if (!IP.ok) { note('La zone constructible est trop étroite", 'msg')
rep3("Esquisse automatique : la maison est placée dans la zone constructible, au plus près de la voie, en dégageant le jardin vers le sud, sans tenir compte des constructions existantes ni de la végétation.", "Esquisse automatique : la maison est placée dans la zone constructible, au plus près de la voie, en dégageant le jardin vers le sud et en évitant les bâtiments existants (IGN), sans tenir compte de la végétation.", 'txt')
i = s.find("  try { if (d.calc && d.calc.neuf !== false && d.calc.rings && d.calc.rings.length) d.implant = implantation(d.calc, c.parcelGeom, c.acces);")
if i < 0: print('ANCRE appel'); sys.exit(1)
s = s[:i] + """  let batsP = [];
  try { if (c.parcelGeom) { const b0 = turf.bbox(c.parcelGeom), pfB = turf.feature(c.parcelGeom); const jb = await getJSON(`https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=BDTOPO_V3:batiment&outputFormat=application/json&count=200&bbox=${b0[1]},${b0[0]},${b0[3]},${b0[2]},urn:ogc:def:crs:EPSG::4326&propertyName=geometrie`, 12000).catch(() => null); batsP = (jb && jb.features || []).filter(f => { try { return f.geometry && turf.booleanIntersects(f, pfB); } catch (e) { return false; } }).map(f => f.geometry); } } catch (e) { batsP = []; }
""" + s[i:].replace("d.implant = implantation(d.calc, c.parcelGeom, c.acces);", "d.implant = implantation(d.calc, c.parcelGeom, c.acces, batsP);", 1)
open(p, 'w', encoding='utf-8').write(s); print('ok E3')
