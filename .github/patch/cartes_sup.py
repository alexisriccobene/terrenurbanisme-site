"""Rapport : trois cartes en plus — courbes de niveau, risques présents sur la carte, bruit des aéroports (PEB DGAC)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(a, b, label, after=True):
    global s
    n = s.count(a)
    if n != 1: print('ANCRE', label, n); sys.exit(1)
    s = s.replace(a, a + b if after else b + a)

HELP = r"""
  // ---------- Cartes complémentaires : relief, risques, bruit des aéroports ----------
  const CEN = (d.ref && d.ref.centroid) || null;
  const frameC = (ratio, dLat) => { if (!CEN) return null; const kk = Math.cos(CEN[1] * Math.PI / 180), dLon = dLat * ratio / kk; return [CEN[0] - dLon / 2, CEN[1] - dLat / 2, CEN[0] + dLon / 2, CEN[1] + dLat / 2]; };
  const IGNR = 'https://data.geopf.fr/wms-r/wms?', IGNV = 'https://data.geopf.fr/wms-v/ows?', GRW = 'https://www.georisques.gouv.fr/services?';
  const wmsU = (base, layer, b, w, h, fmt) => base + 'SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=' + layer + '&STYLES=&CRS=EPSG:4326&BBOX=' + b[1] + ',' + b[0] + ',' + b[3] + ',' + b[2] + '&WIDTH=' + w + '&HEIGHT=' + h + '&FORMAT=' + fmt + '&TRANSPARENT=' + (fmt === 'image/png' ? 'TRUE' : 'FALSE');
  const legU = l => GRW + 'SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER=' + l + '&FORMAT=image/png&SLD_VERSION=1.1.0';
  const legends = async (L) => {
    const out = [];
    for (const b of L) { const im = b && b.length > 300 ? await img(b, true) : null; if (im) out.push(im); }
    if (!out.length) return;
    const sc = 0.6; let row = [], rw = 0; const rows = [];
    for (const im of out) { const w = Math.min(im.width * sc, CW); if (rw + w > CW && row.length) { rows.push(row); row = []; rw = 0; } row.push(im); rw += w + 14; }
    if (row.length) rows.push(row);
    for (const r of rows) {
      const hh = Math.max(...r.map(im => im.height * sc)); ensure(hh + 8); let lx = M;
      for (const im of r) { const w = Math.min(im.width * sc, CW), h = im.height * sc * (w / (im.width * sc)); page.drawImage(im, { x: lx, y: y - h, width: w, height: h }); lx += w + 14; }
      y -= hh + 8;
    }
    y -= 4;
  };
"""
one("const ortho = await img(I.ortho), cadastre = await img(I.cadastre, true), plan = await img(I.plan), orthoWide = await img(I.orthoWide);", HELP, 'helpers')

TOPO = r"""
      if (CEN) {
        const tb = frameC(487 / 220, Math.max(0.0045, I.bbox ? (I.bbox[3] - I.bbox[1]) * 1.3 : 0));
        const [tbase, tcont] = await Promise.all([getBytes(wmsU(IGNR, 'ORTHOIMAGERY.ORTHOPHOTOS', tb, 1100, 497, 'image/jpeg')), getBytes(wmsU(IGNV, 'ELEVATION.CONTOUR.LINE', tb, 1100, 497, 'image/png'))]);
        const ci = tcont && tcont.length > 400 ? await img(tcont, true) : null;
        if (ci) mapBox([{ img: await img(tbase), opacity: 0.4 }, { img: ci }], tb, { h: 220, title: 'Courbes de niveau', parcel: d.parcelCoords, caption: 'Chaque ligne relie des points de même altitude (en mètres) : plus les lignes sont serrées, plus la pente est forte · terrain entouré en jaune · © IGN' });
      }"""
one("['Appréciation', RF.cls[0]]]);", TOPO, 'topo')

RISK = r"""
      if (CEN) {
        const RMAP = {
          retraitGonflementArgile: ['ALEARG_REALISE', ['ALEARG_REALISE'], 'Retrait-gonflement des argiles', ''],
          remonteeNappe: ['REMNAPPE_FR', [], 'Remontées de nappes', 'Rose : débordement de nappe possible · orange clair : inondation de cave possible · plus la teinte est foncée, plus la donnée est fiable · '],
          inondation: ['SUP_INOND,ALEA_SYNT_01_04FAI_FXX,ALEA_SYNT_01_02MOY_FXX,ALEA_SYNT_01_01FOR_FXX', ['SUP_INOND', 'ALEA_SYNT_01_01FOR_FXX', 'ALEA_SYNT_01_02MOY_FXX', 'ALEA_SYNT_01_04FAI_FXX'], 'Zones inondables', ''],
          risqueCotier: ['SUP_INOND,ALEA_SYNT_03_04FAI_FXX,ALEA_SYNT_03_02MOY_FXX,ALEA_SYNT_03_01FOR_FXX', ['SUP_INOND', 'ALEA_SYNT_03_01FOR_FXX', 'ALEA_SYNT_03_02MOY_FXX', 'ALEA_SYNT_03_04FAI_FXX'], 'Submersion marine', ''],
          mouvementTerrain: ['SUP_MVT_TERRAIN,MVT_LOCALISE,CAVITE_LOCALISEE', ['SUP_MVT_TERRAIN', 'MVT_LOCALISE', 'CAVITE_LOCALISEE'], 'Mouvements de terrain', ''],
          feuForet: ['SUP_FEU', ['SUP_FEU'], 'Feux de forêt', ''],
          canalisationsMatieresDangereuses: ['CANALISATIONS', ['C_GAZ', 'C_HYDROCARBURES', 'C_PRODUITS_CHIM'], 'Canalisations de matières dangereuses', ''],
          pollutionSols: ['SSP_CLASSIFICATION_SIS,SSP_ETS_GE_POLYGON,SSP_ETS_GE_POINT', ['SSP_CLASSIFICATION_SIS', 'SSP_ETS_GE_POINT'], 'Sols pollués', ''],
          icpe: ['INSTALLATIONS_CLASSEES_SIMPLIFIE', ['INSTALLATIONS_CLASSEES_SIMPLIFIE'], 'Installations classées', '']
        };
        const want = PRES.filter(r => RMAP[r.key] && (r.key !== 'retraitGonflementArgile' || /moyen|fort|important|élevé/i.test(String(r.adresse || r.commune || '')))).slice(0, 4);
        if (want.length) {
          const rb = frameC(487 / 190, 0.011);
          const [base, ...got] = await Promise.all([getBytes(wmsU(IGNR, 'GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2', rb, 1100, 429, 'image/jpeg')), ...want.map(async r => { const m = RMAP[r.key]; const [ov, ...lg] = await Promise.all([getBytes(wmsU(GRW, m[0], rb, 1100, 429, 'image/png'), 25000), ...m[1].map(l => getBytes(legU(l), 15000))]); return { m, ov, lg }; })]);
          const baseI = await img(base), okm = got.filter(g => g.ov && g.ov.length > 400);
          if (okm.length) { h3('Les risques sur la carte'); text('Chaque carte montre l\'étendue du risque autour du terrain (environ 1 km de côté).', { size: 9 }); }
          for (const g of okm) { mapBox([{ img: baseI, opacity: 0.75 }, { img: await img(g.ov, true), opacity: 0.85 }], rb, { h: 190, title: g.m[2], parcel: d.parcelCoords, pin: CEN, thin: true, caption: g.m[3] + 'Point rouge : le terrain · source : Géorisques · fond © IGN' }); await legends(g.lg); }
        }
      }"""
one("PRES.map(r => [r.label, r.key === 'seisme' && RK.sismique ? RK.sismique.replace(/^Zone\\s*/i, 'Zone ') : rkLvl(r), rkExpl(r)]), { size: 8.5 });", RISK, 'risques')

PEB = r"""  if (CEN) {
    h3('Bruit des aéroports (plan d\'exposition au bruit)');
    let pz = null, okq = false;
    try {
      const fb = [CEN[1] - 0.0005, CEN[0] - 0.0005, CEN[1] + 0.0005, CEN[0] + 0.0005];
      const r = await fetch(IGNV + 'SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&LAYERS=dgac_peb_plan_wmsv&QUERY_LAYERS=dgac_peb_plan_wmsv&STYLES=&CRS=EPSG:4326&BBOX=' + fb.join(',') + '&WIDTH=101&HEIGHT=101&I=50&J=50&INFO_FORMAT=application/json&FEATURE_COUNT=10', { signal: AbortSignal.timeout(15000) });
      if (r.ok) { const j = await r.json(); okq = true; const zs = (j.features || []).map(f => f.properties || {}).filter(p => /^[ABCD]$/.test(String(p.zone || '').trim().toUpperCase())); zs.sort((a, b) => String(a.zone).trim().toUpperCase().localeCompare(String(b.zone).trim().toUpperCase())); pz = zs[0] || null; }
    } catch (_) {}
    d.pebChecked = okq; d.pebZone = pz ? { zone: String(pz.zone).trim().toUpperCase(), nom: String(pz.nom || '').toLowerCase().replace(/(^|[\s'-])\S/g, c => c.toUpperCase()), date: String(pz.date_arret || '').slice(0, 10).split('-').reverse().join('/') } : null;
    if (d.pebZone) {
      const PZ = d.pebZone, ZT = { A: 'bruit très fort', B: 'bruit fort', C: 'bruit modéré', D: 'bruit faible' }[PZ.zone];
      const ZR = { A: 'Les logements y sont interdits, sauf ceux nécessaires à l\'activité de l\'aéroport ou à une exploitation agricole.', B: 'Les logements y sont interdits, sauf ceux nécessaires à l\'activité de l\'aéroport ou à une exploitation agricole.', C: 'Une maison individuelle isolée y est admise dans un secteur déjà urbanisé et équipé, si elle n\'augmente que faiblement le nombre d\'habitants exposés ; les immeubles collectifs sont interdits. Une isolation acoustique renforcée est obligatoire.', D: 'Les constructions y sont autorisées, avec une isolation acoustique renforcée obligatoire.' }[PZ.zone];
      note('Le terrain est en zone ' + PZ.zone + ' (' + ZT + ') du plan d\'exposition au bruit de l\'aérodrome ' + PZ.nom + (PZ.date ? ', approuvé le ' + PZ.date : '') + '. ' + ZR, PZ.zone === 'D' ? 'info' : 'cond');
      text('À savoir : la zone de bruit doit figurer dans la promesse et l\'acte de vente, ainsi que dans le bail (article L.112-11 du code de l\'urbanisme).', { size: 9 });
      const pb = frameC(487 / 200, 0.05);
      const [pbase, pov] = await Promise.all([getBytes(wmsU(IGNR, 'GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2', pb, 1100, 452, 'image/jpeg')), getBytes(wmsU(IGNV, 'dgac_peb_plan_wmsv', pb, 1100, 452, 'image/png'))]);
      const povI = pov && pov.length > 400 ? await img(pov, true) : null;
      if (povI) mapBox([{ img: await img(pbase), opacity: 0.8 }, { img: povI, opacity: 0.7 }], pb, { h: 200, title: 'Plan d\'exposition au bruit', pin: CEN, caption: 'Rouge : zone A · orange : zone B · vert : zone C · bleu : zone D · point rouge : le terrain · source : DGAC · fond © IGN' });
    } else if (okq) text('Le terrain n\'est dans aucune zone de bruit d\'un aérodrome : aucune contrainte de bruit aérien ne s\'applique (plans d\'exposition au bruit publiés par la DGAC).', { size: 9.5 });
    else text('Le service de la DGAC n\'a pas répondu au moment du rapport : la situation vis-à-vis du plan d\'exposition au bruit est à vérifier sur geoportail.gouv.fr.', { size: 9.5 });
  }
"""
one("  h3('Rapport officiel Géorisques');", PEB, 'peb', after=False)

old = "peb.length ? 'Oui' : 'À vérifier', peb.length ? peb.map(p => p.label).slice(0, 2).join(' ; ') : 'Aucun PEB annexé au document d\\'urbanisme ; vérifier auprès de la mairie'"
new = "(d.pebZone || peb.length) ? 'Oui' : d.pebChecked ? 'Non' : 'À vérifier', d.pebZone ? 'Zone ' + d.pebZone.zone + ' du plan d\\'exposition au bruit de l\\'aérodrome ' + d.pebZone.nom : peb.length ? peb.map(p => p.label).slice(0, 2).join(' ; ') : d.pebChecked ? 'Hors des plans d\\'exposition au bruit publiés par la DGAC' : 'Aucun PEB annexé au document d\\'urbanisme ; vérifier auprès de la mairie'"
n = s.count(old)
if n < 1: print('ANCRE erp', n); sys.exit(1)
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s); print('ok cartes', n)
