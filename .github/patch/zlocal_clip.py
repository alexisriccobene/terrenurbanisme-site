# Zonage relevé localement : géométries découpées autour de la parcelle (800 m) pour alléger les calculs et les cartes du rapport
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "      const hit = (zl || []).filter(r => !(r.bbox[0] > pb[2] || r.bbox[2] < pb[0] || r.bbox[1] > pb[3] || r.bbox[3] < pb[1]))"
assert s.count(a) == 1
b = """      const cb = turf.bbox(turf.buffer(pf, 800, { units: 'meters' }));
      for (const r of (zl || [])) {
        if (r.bbox[0] > cb[2] || r.bbox[2] < cb[0] || r.bbox[1] > cb[3] || r.bbox[3] < cb[1]) continue;
        if (r.bbox[0] >= cb[0] && r.bbox[2] <= cb[2] && r.bbox[1] >= cb[1] && r.bbox[3] <= cb[3]) continue;
        try { const c = turf.bboxClip(turf.feature(r.geom), cb); if (c && c.geometry && c.geometry.coordinates && c.geometry.coordinates.length) { r.geom = c.geometry; r.bbox = turf.bbox(c); } } catch (e) {}
      }
""" + a
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('patch zlocal_clip appliqué')
