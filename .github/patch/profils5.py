"""Services à proximité : sources officielles (Sirene, annuaire de l'Éducation nationale, gares SNCF) à la place d'OpenStreetMap, trop instable."""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
i = s.index("// Commerces, écoles, santé et transports les plus proches (OpenStreetMap"); j = s.index("// Plan du terrain au format DXF", i)
NEW = r'''// Commerces, écoles, santé et gares les plus proches : Sirene (INSEE, API Recherche d'entreprises), annuaire de l'Éducation nationale, gares SNCF
async function proximite(ctr, insee) {
  const [lon, lat] = ctr, here = turf.point([lon, lat]), dm = (la, lo) => turf.distance(here, turf.point([Number(lo), Number(la)]), { units: 'meters' });
  const out = [];
  // Sirene : établissements actifs par code d'activité, rayons croissants ; au-delà de 25 réponses, on indique le nombre sans désigner « le plus proche »
  const sirene = async (lab, naf) => {
    for (const r of [0.5, 1, 3, 10]) {
      let j = null;
      for (let k = 0; k < 3 && !j; k++) { try { const x = await fetch(`https://recherche-entreprises.api.gouv.fr/near_point?lat=${lat.toFixed(6)}&long=${lon.toFixed(6)}&radius=${r}&activite_principale=${naf}&etat_administratif=A&per_page=25`, { signal: AbortSignal.timeout(8000) }); if (x.ok) j = await x.json(); else await new Promise(z => setTimeout(z, 400 * (k + 1))); } catch (e) { await new Promise(z => setTimeout(z, 400)); } }
      if (!j) throw new Error('Sirene sans réponse');
      const tot = Number(j.total_results) || 0; if (!tot) continue;
      const E = [];
      for (const x of (j.results || [])) for (const m of (x.matching_etablissements || [])) if (m.etat_administratif === 'A' && m.latitude && m.longitude) E.push({ nom: m.enseigne_1 || m.nom_commercial || x.nom_complet || '', d: dm(m.latitude, m.longitude) });
      E.sort((a, b) => a.d - b.d);
      if (tot > 25) { out.push({ cat: lab, n: tot, r: r * 1000 }); return; }
      if (E.length && E[0].d <= r * 1000 * 1.05) { out.push({ cat: lab, nom: String(E[0].nom).replace(/\s+/g, ' ').trim(), d: Math.round(E[0].d) }); return; }
    }
    out.push({ cat: lab, aucun: true, r: 10000 });
  };
  const ecoles = async () => {
    const pt = `geom'POINT(${lon.toFixed(6)} ${lat.toFixed(6)})'`;
    for (const [lab, w] of [['École maternelle', 'ecole_maternelle=1'], ['École élémentaire', 'ecole_elementaire=1'], ['Collège', 'type_etablissement="Collège"'], ['Lycée', 'type_etablissement="Lycée"']]) {
      const u = `https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/records?where=${encodeURIComponent(w + ' and within_distance(position, ' + pt + ', 15km)')}&order_by=${encodeURIComponent('distance(position, ' + pt + ')')}&limit=1&select=nom_etablissement,position,statut_public_prive`;
      const j = await getJSON(u, 10000);
      const r = j && j.results && j.results[0];
      out.push(r && r.position ? { cat: lab, nom: r.nom_etablissement + (r.statut_public_prive ? ' (' + String(r.statut_public_prive).toLowerCase() + ')' : ''), d: Math.round(dm(r.position.lat, r.position.lon)) } : { cat: lab, aucun: true, r: 15000 });
    }
  };
  const gare = async () => {
    const pt = `geom'POINT(${lon.toFixed(6)} ${lat.toFixed(6)})'`;
    const j = await getJSON(`https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/gares-de-voyageurs/records?where=${encodeURIComponent('within_distance(position_geographique, ' + pt + ', 20km)')}&order_by=${encodeURIComponent('distance(position_geographique, ' + pt + ')')}&limit=1`, 10000);
    const r = j && j.results && j.results[0];
    out.push(r && r.position_geographique ? { cat: 'Gare SNCF', nom: r.nom, d: Math.round(dm(r.position_geographique.lat, r.position_geographique.lon)) } : { cat: 'Gare SNCF', aucun: true, r: 20000 });
  };
  const corse = /^2[AB]/.test(String(insee || ''));
  const tasks = [ecoles().catch(e => console.warn('écoles', String(e && e.message || e).slice(0, 80)))];
  if (!corse) tasks.push(gare().catch(e => console.warn('gares', String(e && e.message || e).slice(0, 80))));
  await Promise.all(tasks);
  // Sirene : appels successifs (limite de débit de l'API)
  for (const [lab, naf] of [['Boulangerie', '10.71C'], ['Supermarché ou hypermarché', '47.11D,47.11F'], ['Supérette', '47.11B,47.11C'], ['Pharmacie', '47.73Z'], ['Médecin généraliste', '86.21Z']]) {
    try { await sirene(lab, naf); } catch (e) { console.warn('Sirene', lab, String(e && e.message || e).slice(0, 80)); }
  }
  const ORD = ['École maternelle', 'École élémentaire', 'Collège', 'Lycée', 'Boulangerie', 'Supérette', 'Supermarché ou hypermarché', 'Pharmacie', 'Médecin généraliste', 'Gare SNCF'];
  out.sort((a, b) => ORD.indexOf(a.cat) - ORD.indexOf(b.cat));
  if (!out.length) throw new Error('aucune source de proximité');
  return out;
}
'''
s = s[:i] + NEW + s[j:]
rep("jobs.push(safe(proximite(d.ref.centroid), null).then(v => { out.proxi = v; }));", "jobs.push(safe(proximite(d.ref.centroid, insee), null).then(v => { out.proxi = v; }));")
# Affichage
old_start = s.index("        table([{ label: 'Service', w: 0.32, bold: true }")
old_end = s.index("      } else text(PR ?", old_start)
s = s[:old_start] + r'''        table([{ label: 'Service', w: 0.3, bold: true }, { label: 'Le plus proche', w: 0.48 }, { label: 'Distance', w: 0.22 }], PR.map(x => x.aucun ? [x.cat, 'Aucun à moins de ' + fmt(x.r / 1000) + ' km', '—'] : x.n ? [x.cat, fmt(x.n) + ' établissements à moins de ' + (x.r < 1000 ? fmt(x.r) + ' m' : fmt(x.r / 1000) + ' km'), 'moins de ' + (x.r < 1000 ? fmt(x.r) + ' m' : fmt(x.r / 1000) + ' km')] : [x.cat, x.nom || 'Nom non renseigné', dist(x.d)]));
        text('Distances à vol d\'oiseau depuis le centre de la parcelle. Sources : annuaire de l\'Éducation nationale' + (/^2[AB]/.test(R.insee) ? '' : ', gares de voyageurs SNCF') + ' et répertoire Sirene de l\'INSEE (établissements actifs : boulangerie 10.71C, supérette 47.11B-C, supermarché 47.11D-F, pharmacie 47.73Z, médecin généraliste 86.21Z).', { size: 8.5, color: C.muet });
''' + s[old_end:]
rep("'Source OpenStreetMap momentanément indisponible au moment du rapport.'", "'Sources momentanément indisponibles au moment du rapport.'")
rep("copropriété, commerces et services à proximité.',\n  notaire:", "copropriété, écoles, commerces, santé et gares à proximité.',\n  notaire:")
rep("'Sources publiques officielles : ventes (DVF), Carte des loyers, ADEME, registre des copropriétés, OpenStreetMap.'", "'Sources publiques officielles : ventes (DVF), Carte des loyers, ADEME, registre des copropriétés, Éducation nationale, Sirene.'")
rep("h3('Commerces, écoles, santé et transports');", "h3('Écoles, commerces, santé et gares');")
rep('await withTimeout(modulesPro(d.profil, c, d, PRO), 30000)', 'await withTimeout(modulesPro(d.profil, c, d, PRO), 40000)')
open(p, 'w', encoding='utf-8').write(s); print('ok profils5')
