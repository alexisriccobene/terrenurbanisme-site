"""Foncier : zones d'activité plus strictes, contrôle des constructions sur chaque terrain, situations lisibles."""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(pat, rep, flags=0, label=''):
    global s
    m = list(re.finditer(pat, s, flags))
    if len(m) != 1: print('ANCRE', label, len(m)); sys.exit(1)
    s = s[:m[0].start()] + rep(m[0]) + s[m[0].end():]

HELP = r"""// ---------- Zones d'activité et contrôle des constructions ----------
const actZone = (s: any) => {
  const lib = String(s.zone || '').toUpperCase(), ll = String(s.zone_long || '');
  if (/^\d*\s*(AU|U)\s*[-_]?\s*[XEIYZ]/.test(lib)) return true;
  if (/habitat|r[ée]siden|logement|centralit|mixit|mixte|centre[- ]?(ville|bourg|ancien)|urbaine? (dense|centrale)/i.test(ll)) return false;
  return /activit|industri|artisan|[ée]conomi|logisti/i.test(ll);
};
const natCourt = (n: string) => /liquidation/i.test(n) ? 'Liquidation judiciaire' : /redressement/i.test(n) ? 'Redressement judiciaire' : /cl[ôo]ture/i.test(n) ? 'Procédure clôturée' : /modifiant le plan/i.test(n) ? 'Plan de sauvegarde modifié' : /sauvegarde/i.test(n) ? 'Procédure de sauvegarde' : /plan de (continuation|cession)/i.test(n) ? 'Plan de continuation ou de cession' : 'Procédure collective';
const WFS_IGN = 'https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json&srsName=EPSG:4326';
const polysOf = (g: any) => !g ? [] : g.type === 'Polygon' ? [g.coordinates] : g.type === 'MultiPolygon' ? g.coordinates : [];
const inRing = (x: number, y: number, r: any[]) => { let c = false; for (let i = 0, j = r.length - 1; i < r.length; j = i++) { const xi = r[i][0], yi = r[i][1], xj = r[j][0], yj = r[j][1]; if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) c = !c; } return c; };
const inPolys = (x: number, y: number, ps: any[]) => ps.some((p: any) => inRing(x, y, p[0]) && !p.slice(1).some((h: any) => inRing(x, y, h)));
const ringM2 = (r: any[], lat: number) => { const kx = 111320 * Math.cos(lat * Math.PI / 180), ky = 110540; let a = 0; for (let i = 0, j = r.length - 1; i < r.length; j = i++) a += r[j][0] * kx * r[i][1] * ky - r[i][0] * kx * r[j][1] * ky; return Math.abs(a / 2); };
// Chaque terrain « sans bâtiment » est contrôlé sur le plan cadastral et la BD TOPO (toutes constructions) ; les parcelles déjà bâties sont écartées.
async function verifBati(q: any, sites: any[]) {
  const t0 = Date.now(), budget = Deno.env.get('TU_LOCAL') ? 420000 : 45000, cible = 420;
  const cand = sites.filter((s: any) => s.kind === 'terrain' && !s.bati && s.id);
  if (!cand.length) return null;
  let ok = 0, bati = 0, i = 0;
  const drop = new Set();
  const jget = async (u: string, ms: number) => { for (let t = 0; t < 2; t++) { try { const r = await fetch(u, { signal: AbortSignal.timeout(ms) }); if (r.ok) return await r.json(); } catch (_) {} } return null; };
  while (i < cand.length && ok < cible && Date.now() - t0 < budget) {
    const lot = cand.slice(i, i + 40); i += 40;
    const pu = WFS_IGN + '&typeNames=CADASTRALPARCELS.PARCELLAIRE_EXPRESS:parcelle&count=60&CQL_FILTER=' + encodeURIComponent('idu IN (' + lot.map((x: any) => "'" + String(x.id).replace(/[^0-9A-Z]/g, '') + "'").join(',') + ')');
    const pj0 = await jget(pu, 30000);
    const geo = new Map();
    for (const f of pj0?.features || []) geo.set(f.properties?.idu, polysOf(f.geometry));
    for (let k = 0; k < lot.length; k += 10) {
      await Promise.all(lot.slice(k, k + 10).map(async (x: any) => {
        const ps = geo.get(x.id); if (!ps || !ps.length) return;
        let x0 = 180, y0 = 90, x1 = -180, y1 = -90;
        for (const p of ps) for (const c of p[0]) { x0 = Math.min(x0, c[0]); x1 = Math.max(x1, c[0]); y0 = Math.min(y0, c[1]); y1 = Math.max(y1, c[1]); }
        const bj = await jget(WFS_IGN + '&typeNames=BDTOPO_V3:batiment&propertyName=geometrie&count=1000&bbox=' + [y0, x0, y1, x1].map((v) => v.toFixed(6)).join(',') + ',urn:ogc:def:crs:EPSG::4326', 20000);
        if (!bj) return;
        let a = 0;
        for (const f of bj.features || []) for (const p of polysOf(f.geometry)) { const r = p[0]; let cx = 0, cy = 0; for (const c of r) { cx += c[0]; cy += c[1]; } cx /= r.length; cy /= r.length; if (inPolys(cx, cy, ps)) a += ringM2(r, cy); }
        if (a >= 50) { drop.add(x); bati++; x.bati_autre = Math.round(a); } else { ok++; x.verifie = true; }
      }));
    }
  }
  if (ok + bati < 10) { console.error('verif: service indisponible', ok, bati); return null; }
  let nonControles = 0;
  for (let j = sites.length - 1; j >= 0; j--) {
    const x = sites[j];
    if (x.kind === 'terrain' && !x.bati && !x.verifie) { if (!drop.has(x)) nonControles++; sites.splice(j, 1); }
  }
  console.log('verif', { ok, bati, nonControles, ms: Date.now() - t0 });
  return { ok, bati, nonControles };
}
"""
one(r"async function chargerSites\(q(: any)?\)", lambda m: HELP + m.group(0), label='chargerSites')
one(r"for \(const s of out\) \{\s*const dif = ", lambda m: m.group(0).replace('{', '{\n    s.activite = actZone(s);', 1), label='activite')
one(r"const \{ sites, depList \} = await chargerSites\(row\);", lambda m: m.group(0) + "\n    row._verif = await verifBati(row, sites).catch((e: any) => { console.error('verif', e); return null; });", label='generer')
one(r"s\.proc_nature \? s\.proc_nature \+ \(s\.proc_date \? ' \(' \+", lambda m: m.group(0).replace('s.proc_nature ? s.proc_nature +', 's.proc_nature ? natCourt(s.proc_nature) +'), label='sit')
one(r"\[\s*'Bâtiments',\s*'Bâtiments industriels[^\]]*\],", lambda m: m.group(0) + """
    ...(q._verif ? [[
      'Contrôle des terrains',
      'Chaque terrain proposé a été vérifié un par un sur le plan cadastral et la BD TOPO (IGN) : aucune construction de plus de 50 m² sur la parcelle. ' + (q._verif.bati ? nb(q._verif.bati) + ' parcelle' + (q._verif.bati > 1 ? 's' : '') + ' déjà bâtie' + (q._verif.bati > 1 ? 's ont été écartées.' : ' a été écartée.') : '')
    ]] : []),""", label='methode')
open(p, 'w', encoding='utf-8').write(s); print('ok verif')
