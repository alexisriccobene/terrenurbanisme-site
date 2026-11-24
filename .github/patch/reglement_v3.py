# Règlements : (1) document du Géoportail périmé (404) -> version en vigueur retrouvée automatiquement ;
# (2) sources de règlements renseignées à la main (table reglement_sources) lues en priorité.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:90], s.count(a)); s = s.replace(a, b)
FN = r'''
// Document du Géoportail de l'Urbanisme réellement en vigueur pour une partition (le zonage pointe parfois vers une version supprimée)
const GPU_ACTIF = new Map();
async function gpuDocActif(partition) {
  if (!partition) return null;
  if (GPU_ACTIF.has(partition)) return GPU_ACTIF.get(partition);
  let id = null;
  try {
    const L = await getJSON(`https://www.geoportail-urbanisme.gouv.fr/api/document?partition=${encodeURIComponent(partition)}`, 15000);
    const prod = (Array.isArray(L) ? L : []).filter(d => d && d.status === 'document.production');
    if (prod.length) id = prod[prod.length - 1].id;
  } catch (e) { console.warn('document en vigueur', partition, String(e && e.message || e).slice(0, 120)); }
  GPU_ACTIF.set(partition, id); return id;
}
async function urlExiste(u) {
  try { const r = await fetch(u, { method: 'HEAD', signal: AbortSignal.timeout(15000) }); return r.ok; } catch (_) { return false; }
}
async function gpuReglementActif(p, nomfic) {
  const id = await gpuDocActif(p.partition); if (!id || id === p.gpu_doc_id) return '';
  let nom = nomfic;
  try {
    const fl = await getJSON(`https://www.geoportail-urbanisme.gouv.fr/api/document/${id}/files`, 15000);
    const names = (Array.isArray(fl) ? fl : (fl && fl.files) || []).map(x => typeof x === 'string' ? x : (x && (x.name || x.path)) || '').filter(Boolean).map(n => n.split('/').pop());
    if (!nom || !names.includes(nom)) nom = names.find(n => /r[eè]glement/i.test(n) && !/graphique|plan|annexe|zonage/i.test(n) && /\.pdf$/i.test(n)) || '';
  } catch (e) { console.warn('pièces du document en vigueur', String(e && e.message || e).slice(0, 120)); }
  return nom ? `https://data.geopf.fr/annexes/gpu/documents/${p.partition}/${id}/${nom}` : '';
}
// Sources de règlement vérifiées à la main (métropoles qui ne déposent qu'un renvoi vers leur site)
async function sourcesManuelles(partition, code) {
  if (!partition) return [];
  try {
    const { data } = await admin.from('reglement_sources').select('zone,url').eq('partition', partition).eq('actif', true);
    const c = String(code || '').toUpperCase();
    const hit = (data || []).filter(r => r.zone && new RegExp('^(' + r.zone + ')$', 'i').test(c));
    return (hit.length ? hit : (data || []).filter(r => !r.zone)).map(r => r.url);
  } catch (e) { console.warn('reglement_sources', e); return []; }
}
async function reglementFor(m) {'''
rep("async function reglementFor(m) {", FN)
a = "    const gpuUrl = p.gpu_doc_id && nomfic && p.partition ? `https://data.geopf.fr/annexes/gpu/documents/${p.partition}/${p.gpu_doc_id}/${nomfic}` : '';"
rep(a, a.replace('const gpuUrl', 'let gpuUrl') + "\n    if (gpuUrl && !(await urlExiste(gpuUrl))) { const g2 = await gpuReglementActif(p, nomfic); if (g2) { console.log('règlement : version en vigueur', g2.slice(-60)); gpuUrl = g2; } }\n    const manu = await sourcesManuelles(p.partition, zlib(p));")
rep("const urls = [p.copie || '', gpuUrl", "const urls = [...manu, p.copie || '', gpuUrl")
open(p, 'w', encoding='utf-8').write(s); print('patch reglement_v3 appliqué')
