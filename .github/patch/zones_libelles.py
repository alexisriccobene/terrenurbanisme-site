# Zones : libellés de remplacement publiés sur le Géoportail (AAAAAAA, UEXXXXXX) remplacés par le vrai code ;
# règlement écrit retrouvé dans la liste des pièces du document quand la zone ne le désigne pas (ou désigne le plan de zonage)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("async function reglementFor(m) {", """function zlib(p) {
  const bad = x => !x || /^(.)\\1{3,}$/.test(x) || /X{3,}/.test(x);
  const l = String((p && p.libelle) || '').trim(); if (!bad(l)) return l;
  const m = String((p && p.libelong) || '').match(/^\\s*([A-Za-z0-9][A-Za-z0-9.\\-]{0,9})\\s*:/);
  if (m && !bad(m[1])) return m[1];
  return (p && p.typezone) || l || '';
}
function zlong(p) { return String((p && p.libelong) || '').replace(/^\\s*[A-Za-z0-9.\\-]*(?:([A-Za-z0-9])\\1{3,}|X{3,})[A-Za-z0-9.\\-]*\\s*:\\s*/, '').trim(); }
async function reglementFor(m) {""")
rep("for (const z of zs) { const code = z.p.libelle || z.p.typezone;", "for (const z of zs) { const code = zlib(z.p);")
rep("""    const nomfic = String(p.nomfic || '').split('#')[0];
    const gpuUrl""", """    let nomfic = String(p.nomfic || '').split('#')[0];
    if ((!nomfic || /graphique|plan_?de_?zonage|_zonage/i.test(nomfic)) && p.gpu_doc_id && p.partition) {
      try {
        const fl = await getJSON(`https://www.geoportail-urbanisme.gouv.fr/api/document/${p.gpu_doc_id}/files`, 15000);
        const names = (Array.isArray(fl) ? fl : (fl && fl.files) || []).map(x => typeof x === 'string' ? x : (x && (x.name || x.path)) || '').filter(Boolean);
        const rg = names.find(n => /r[eè]glement/i.test(n) && !/graphique|plan|annexe|zonage/i.test(n) && /\\.pdf$/i.test(n));
        if (rg) nomfic = rg.split('/').pop();
      } catch (e) { console.warn('pièces du document', String(e && e.message || e).slice(0, 120)); }
    }
    const gpuUrl""")
rep("const zone = { code: p.libelle || p.typezone, typeLabel: classify(p.typezone)[0] + (p.libelong ? ' · ' + p.libelong : '') };", "const zone = { code: zlib(p), typeLabel: classify(p.typezone)[0] + (zlong(p) ? ' · ' + zlong(p) : '') };")
rep("return { code: p.libelle || p.typezone || '?', longLabel: p.libelong && p.libelong !== p.libelle ? p.libelong : '',", "return { code: zlib(p) || '?', longLabel: zlong(p) && zlong(p) !== zlib(p) ? zlong(p) : '',")
rep("return { code: p.libelle || p.typezone || ('Secteur ' + (p.typesect || '')),", "return { code: zlib(p) || ('Secteur ' + (p.typesect || '')),")
open(p, 'w', encoding='utf-8').write(s); print('patch libellés appliqué')
