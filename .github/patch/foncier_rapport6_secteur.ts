// ---------- Secteur : procédures collectives du jour et liens d'annonces ----------
const getJ = async (u: string, ms = 15000) => { try { const r = await fetch(u, { signal: AbortSignal.timeout(ms) }); return r.ok ? await r.json() : null; } catch { return null; } };
const pj = (v: any) => { if (!v || v === 'None') return null; if (typeof v === 'object') return v; try { return JSON.parse(v); } catch { return null; } };
// Fiche publique d'une société (Annuaire des entreprises, data.gouv) : siège, dirigeants, activité, état
const NAF_LOCAUX = /^(0[1-3]|1\d|2\d|3[0-3]|3[6-9]|4[1-3]|45|46|49|5[0-2]|77|81\.2|95)/;
async function ficheSociete(siren: string) {
  const j = await getJ('https://recherche-entreprises.api.gouv.fr/search?q=' + siren + '&page=1&per_page=1', 12000);
  const r = j && j.results && j.results[0];
  if (!r || r.siren !== siren) return null;
  const sg = r.siege || {};
  const dir = (r.dirigeants || []).filter((d: any) => !/commissaire|suppl[ée]ant|^autre$/i.test(String(d.qualite || ''))).slice(0, 2).map((d: any) => d.type_dirigeant === 'personne morale' ? (d.denomination || '') + (d.qualite ? ' (' + d.qualite + ')' : '') : [d.prenoms ? String(d.prenoms).split(/[ ,]/)[0] : '', d.nom || ''].filter(Boolean).join(' ') + (d.qualite ? ' (' + d.qualite + ')' : '')).filter(Boolean);
  return { nom: r.nom_complet || r.nom_raison_sociale || '', adresse: sg.adresse || '', lat: sg.latitude ? Number(sg.latitude) : null, lon: sg.longitude ? Number(sg.longitude) : null, naf: r.activite_principale || sg.activite_principale || '', dirigeants: dir, creation: r.date_creation || '', etat: r.etat_administratif || '' };
}
async function fiches(sirens: string[]) {
  const out = new Map<string, any>(), L = [...new Set(sirens.filter((x) => /^\d{9}$/.test(x)))].slice(0, 90);
  for (let i = 0; i < L.length; i += 5) {
    const lot = await Promise.all(L.slice(i, i + 5).map((x) => ficheSociete(x).catch(() => null)));
    lot.forEach((f, k) => { if (f) out.set(L[i + k], f); });
    await new Promise((r) => setTimeout(r, 900));
  }
  return out;
}
async function secteur(q: any, depList: string[], sites: any[]) {
  const g = await getJ(`https://geo.api.gouv.fr/communes/${encodeURIComponent(q.insee || '')}?fields=nom,codesPostaux,codeDepartement`);
  const nomC = (g && g.nom) || q.commune, cp0 = g && g.codesPostaux && g.codesPostaux[0] ? g.codesPostaux[0] : '';
  const deps = depList.length ? depList : (g && g.codeDepartement ? [g.codeDepartement] : []);
  const cps = new Set<string>();
  for (const d of deps) {
    const l = await getJ(`https://geo.api.gouv.fr/departements/${d}/communes?fields=centre,codesPostaux`, 20000) || [];
    for (const c of l) { const ce = c.centre && c.centre.coordinates; if (ce && hav(q.lat, q.lon, ce[1], ce[0]) <= q.rayon_km + 2) (c.codesPostaux || []).forEach((x: string) => cps.add(x)); }
  }
  const since = new Date(Date.now() - 365 * 864e5).toISOString().slice(0, 10), L = [...cps], raw: any[] = [];
  for (let i = 0; i < L.length && raw.length < 600; i += 30) {
    const ch = L.slice(i, i + 30);
    const where = `familleavis="collective" and dateparution>="${since}" and (${ch.map(x => 'cp="' + x + '"').join(' or ')})`;
    const j = await getJ('https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records?where=' + encodeURIComponent(where) + '&select=commercant,ville,cp,dateparution,jugement,registre,url_complete,listepersonnes&order_by=dateparution%20desc&limit=100');
    for (const r of (j && j.results) || []) raw.push(r);
  }
  const bySiren = new Map<string, any>();
  for (const r of raw) {
    const ju = pj(r.jugement) || {}; const nat = String(ju.nature || ''), fam = String(ju.famille || '');
    if (!/liquidation|cession/i.test(nat) || /cl[ôo]ture|r[ée]solution du plan|homologation|infirm|rapport|cr[ée]ances|[ée]tat des|d[ée]p[ôo]t/i.test(nat)) continue;
    const reg = Array.isArray(r.registre) ? r.registre : String(r.registre || '').match(/\d{9}/g) || [];
    const siren = String(reg.find((x: string) => /^\d{9}$/.test(String(x).replace(/\s/g, ''))) || '').replace(/\s/g, '');
    const comp = String(ju.complementJugement || '');
    const mm = comp.match(/(?:d[ée]sign(?:ant|e)|nomm(?:ant|e))\s+(?:en qualit[ée] de\s+)?(?:mandataire judiciaire|liquidateur(?: judiciaire)?|administrateur judiciaire)\s*:?\s*(.{5,230}?)(?:\.\s|;|\s+Les cr[ée]ances|\s+et\s+d[ée]sign|$)/i);
    const lp = pj(r.listepersonnes); const pers = lp && (Array.isArray(lp.personne) ? lp.personne[0] : lp.personne) || {};
    if (pers.typePersonne && pers.typePersonne !== 'pm') continue;
    const it = { nom: r.commercant || pers.denomination || '', activite: (() => { const t = String(pers.activite || '').replace(/\s+/g, ' ').trim(); return t.length <= 220 ? t : t.slice(0, 220).replace(/\s+\S*$/, '') + '…'; })(), ville: r.ville || '', cp: r.cp || '', date: ju.date || r.dateparution || '', nature: natCourt(nat), mandataire: mm ? mm[1].trim().replace(/\s+/g, ' ').replace(/^./, (c: string) => c.toUpperCase()) : '', url: r.url_complete || '', siren, liq: /liquidation/i.test(nat) };
    const k = siren || (it.nom + it.cp);
    if (!bySiren.has(k)) bySiren.set(k, it);
  }
  let procs = [...bySiren.values()].sort((a, b) => (Number(b.liq) - Number(a.liq)) || String(b.date).localeCompare(String(a.date)));
  // Fiches des sociétés : en procédure dans le secteur et propriétaires des sites retenus
  const F = await fiches([...procs.map((p: any) => p.siren), ...sites.slice(0, 60).map((s0: any) => String(s0.siren || ''))]).catch(() => new Map());
  for (const p of procs) { const f = F.get(p.siren); if (f) p.fiche = f; }
  // Seules les entreprises qui occupaient des locaux d'activité (industrie, BTP, garage, transport, commerce de gros, agriculture…)
  const ACT_LOCAUX = /b[âa]timent|ma[çc]onn|travaux|construction|menuis|charpent|plomb|couverture|garage|m[ée]canique|carrosserie|transport|logisti|entrep[ôo]t|stockage|n[ée]goce|de gros|industri|fabrication|atelier|agricol|[ée]levage|scierie|m[ée]tallerie|serrurerie|imprimerie|recyclage|d[ée]chets|location de (mat|v[ée]hic|engins)/i;
  const SANS = /production d.?[ée]lectricit|photovolta|conseil|logiciel|informatique|holding|vtc|chauffeur|restaura|snack|pizz|caf[ée]|\bbar\b|coiffure|esth[ée]ti|formation|enseignement|cours /i;
  procs = procs.filter((p: any) => { const naf = p.fiche && p.fiche.naf; if (naf) return NAF_LOCAUX.test(naf) && !/^35/.test(naf); return ACT_LOCAUX.test(p.activite) && !SANS.test(p.activite); });
  for (const s0 of sites) { if (s0.siren && F.get(String(s0.siren))) s0.fiche = F.get(String(s0.siren)); }
  let maj = 0;
  for (const s0 of sites) { if (!s0.siren) continue; const p0 = bySiren.get(String(s0.siren)); if (p0) { s0.proc_nature = p0.nature; s0.proc_date = p0.date; s0.proc_url = p0.url; s0.mandataire = p0.mandataire; if (!s0.dif) { s0.dif = true; s0.score += 25; } maj++; } }
  if (maj) sites.sort((a, b) => b.score - a.score);
  const slug = String(nomC).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const sc = cp0 ? slug + '-' + cp0 : '';
  const links: [string, string, string][] = [];
  if (sc) {
    if (q.besoin !== 'terrain') {
      links.push(['BureauxLocaux : entrepôts et locaux d\'activité à vendre', 'Annonces d\'agences spécialisées en immobilier d\'entreprise, autour de ' + nomC + '.', `https://www.bureauxlocaux.com/immobilier-d-entreprise/annonces/${sc}/vente-entrepots`]);
      links.push(['BureauxLocaux : entrepôts et locaux d\'activité à louer', 'Les mêmes biens en location, souvent plus rapides à occuper.', `https://www.bureauxlocaux.com/immobilier-d-entreprise/annonces/${sc}/location-entrepots`]);
      links.push(['Geolocaux : entrepôts à louer', 'Autre portail d\'immobilier d\'entreprise, avec la carte des annonces.', `https://geolocaux.com/location/entrepot/${sc}`]);
      links.push(['Zimo : locaux d\'activité à vendre', 'Agrégateur qui rassemble les annonces de nombreuses agences.', `https://www.zimo.fr/annonces/immobilier-professionnel/vente/local-d-activite/${sc}`]);
    }
    if (q.besoin !== 'batiment') {
      links.push(['BureauxLocaux : terrains d\'activité à vendre', 'Terrains industriels et commerciaux proposés par les agences.', `https://www.bureauxlocaux.com/immobilier-d-entreprise/annonces/${sc}/vente-terrains`]);
      links.push(['Geolocaux : terrains à vendre', 'Terrains proposés aux entreprises, avec la carte des annonces.', `https://geolocaux.com/vente/terrain/${sc}`]);
      links.push(['Zimo : terrains à vendre', 'Terrains constructibles ou non, toutes agences confondues.', `https://www.zimo.fr/annonces/immobilier-professionnel/vente/terrain/${sc}`]);
    }
  }
  const ench: [string, string, string][] = [
    ['Licitor : prochaines ventes aux enchères immobilières', 'Biens saisis ou vendus sur décision de justice, avec la date de l\'audience et la mise à prix.', 'https://www.licitor.com/ventes-aux-encheres-immobilieres/france.html'],
    ['Avoventes : site des avocats pour les ventes judiciaires', 'Plateforme du Conseil national des barreaux : ventes aux enchères devant les tribunaux.', 'https://avoventes.fr/recherche/toutes']
  ];
  let mj: any[] = [];
  try { const { data } = await admin.from('fon_mandataires').select('nom,cles,tel,email,site,implantations').limit(3000); mj = data || []; } catch (_) {}
  return { nomC, procs, maj, links, ench, mj };
}

