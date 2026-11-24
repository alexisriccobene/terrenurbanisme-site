# Zonage : une même zone servie deux fois par le Géoportail (ancienne et nouvelle version du document) n'apparaît qu'une fois,
# avec sa part réelle du terrain (« zone Nf (100 %) et pour le reste en zone Nf (100 %) » ne doit plus se produire)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "  }).filter(r => r.share > 0.005 || zf.length === 1).sort((a, b) => b.share - a.share);\n"
assert s.count(a) == 1, s.count(a)
b = a + """  {
    const byCode = new Map();
    for (const z of zones) {
      const k = String(z.code || '?').toUpperCase(), o = byCode.get(k);
      if (!o) { byCode.set(k, { ...z, _s: [z.share] }); continue; }
      o._s.push(z.share); if (!o.url && z.url) o.url = z.url; if (!o.longLabel && z.longLabel) o.longLabel = z.longLabel;
    }
    const fus = [...byCode.values()].map(o => { const sum = o._s.reduce((x, y) => x + y, 0); o.share = sum > 1.001 ? Math.max(...o._s) : sum; delete o._s; return o; }).sort((a, b) => b.share - a.share);
    if (fus.length !== zones.length) { console.log('zones en double fusionnées', zones.length, '->', fus.length); zones.splice(0, zones.length, ...fus); }
  }
"""
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('patch zones_doublons appliqué')
