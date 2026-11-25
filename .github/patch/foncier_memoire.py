"""Foncier entreprises : lecture des tuiles par petits lots (zones denses comme Lyon ou Paris sans dépasser la mémoire)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
i = s.find('async function chargerSites(')
j = s.find('// ---------- Secteur', i)
if i < 0 or j < 0 or s.count('async function chargerSites(') != 1: print('ANCRE', i, j); sys.exit(1)
new = r"""async function chargerSites(q: any) {
  const T = 0.25, dLat = q.rayon_km / 111, dLon = q.rayon_km / (111 * Math.cos(q.lat * Math.PI / 180));
  const { data: deps } = await admin.from('fon_grille').select('dep').gte('clat', q.lat - dLat - 0.02).lte('clat', q.lat + dLat + 0.02).gte('clon', q.lon - dLon - 0.02).lte('clon', q.lon + dLon + 0.02).limit(5000);
  const depList = [...new Set((deps || []).map((x: any) => x.dep))] as string[];
  const paths: string[] = [];
  for (const dep of depList) for (let ty = Math.floor((q.lat - dLat) / T); ty <= Math.floor((q.lat + dLat) / T); ty++) for (let tx = Math.floor((q.lon - dLon) / T); tx <= Math.floor((q.lon + dLon) / T); tx++) paths.push(`t/${dep}/${ty}_${tx}.json.gz`);
  const out: any[] = [];
  const keep = (s: any) => {
    const d = hav(q.lat, q.lon, s.lat, s.lon); if (d > q.rayon_km) return;
    if (q.besoin === 'terrain' && !(s.kind === 'friche' || (s.kind === 'terrain' && !s.bati))) return;
    if (q.besoin === 'batiment' && !s.bati) return;
    if (q.surface && !((s.surface || 0) >= q.surface)) return;
    if (q.bati && !((s.bati || 0) >= q.bati)) return;
    s.dist = d; out.push(s);
  };
  // Lecture par lots de 3 tuiles : chaque tuile est filtrée puis libérée avant la suivante
  for (let i = 0; i < paths.length; i += 3) {
    await Promise.all(paths.slice(i, i + 3).map(async (p) => {
      const { data } = await admin.storage.from('foncier').download(p);
      if (!data) return;
      let l: any[] | null = await gunzipJSON(data);
      for (const s of l || []) keep(s);
      l = null;
    }));
  }
  for (const s of out) {
    const dif = !!(s.proc_nature || s.etat === 'C');
    s.dif = dif;
    s.score = (s.activite ? 30 : 0) + (dif ? 25 : 0) + (s.kind === 'friche' ? 12 : 0) + (s.armee ? 8 : 0) + (s.siren ? 5 : 0) + (s.poste_km != null ? (s.poste_km < 2 ? 10 : s.poste_km < 5 ? 5 : 0) : 0) - s.dist * 0.6 + (q.besoin !== 'terrain' && s.bati ? 6 : 0);
  }
  out.sort((a, b) => b.score - a.score);
  return { sites: out, depList };
}

"""
s = s[:i] + new + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok memoire')
