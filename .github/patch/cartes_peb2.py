"""PEB : interrogation au centre ET sur le contour de la parcelle (un terrain partiellement en zone est détecté)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = """      const fb = [CEN[1] - 0.0005, CEN[0] - 0.0005, CEN[1] + 0.0005, CEN[0] + 0.0005];
      const r = await fetch(IGNV + 'SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&LAYERS=dgac_peb_plan_wmsv&QUERY_LAYERS=dgac_peb_plan_wmsv&STYLES=&CRS=EPSG:4326&BBOX=' + fb.join(',') + '&WIDTH=101&HEIGHT=101&I=50&J=50&INFO_FORMAT=application/json&FEATURE_COUNT=10', { signal: AbortSignal.timeout(15000) });
      if (r.ok) { const j = await r.json(); okq = true; const zs = (j.features || []).map(f => f.properties || {}).filter(p => /^[ABCD]$/.test(String(p.zone || '').trim().toUpperCase())); zs.sort((a, b) => String(a.zone).trim().toUpperCase().localeCompare(String(b.zone).trim().toUpperCase())); pz = zs[0] || null; }"""
b = """      const ring = Array.isArray(d.parcelCoords) ? d.parcelCoords : [], step = Math.max(1, Math.ceil(ring.length / 8));
      const PTS = [CEN, ...ring.filter((_, i) => i % step === 0).slice(0, 8)];
      const q1 = async (pt) => { const fb = [pt[1] - 0.0005, pt[0] - 0.0005, pt[1] + 0.0005, pt[0] + 0.0005]; const r = await fetch(IGNV + 'SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&LAYERS=dgac_peb_plan_wmsv&QUERY_LAYERS=dgac_peb_plan_wmsv&STYLES=&CRS=EPSG:4326&BBOX=' + fb.join(',') + '&WIDTH=101&HEIGHT=101&I=50&J=50&INFO_FORMAT=application/json&FEATURE_COUNT=10', { signal: AbortSignal.timeout(15000) }); if (!r.ok) return null; const j = await r.json(); return (j.features || []).map(f => f.properties || {}).filter(p => /^[ABCD]$/.test(String(p.zone || '').trim().toUpperCase())); };
      const RES = await Promise.all(PTS.map(pt => q1(pt).catch(() => null)));
      okq = RES[0] !== null || RES.some(x => x !== null);
      const zs = RES.filter(Boolean).flat(); zs.sort((a, b) => String(a.zone).trim().toUpperCase().localeCompare(String(b.zone).trim().toUpperCase()));
      pz = zs[0] || null; if (pz) pz._partiel = !(RES[0] || []).some(x => String(x.zone).trim().toUpperCase() === String(pz.zone).trim().toUpperCase());"""
if s.count(a) != 1: print('ANCRE fi', s.count(a)); sys.exit(1)
s = s.replace(a, b)
a2 = "date: String(pz.date_arret || '').slice(0, 10).split('-').reverse().join('/') } : null;"
if s.count(a2) != 1: print('ANCRE z', s.count(a2)); sys.exit(1)
s = s.replace(a2, "date: String(pz.date_arret || '').slice(0, 10).split('-').reverse().join('/'), partiel: !!pz._partiel } : null;")
a3 = "note('Le terrain est en zone ' + PZ.zone"
if s.count(a3) != 1: print('ANCRE n', s.count(a3)); sys.exit(1)
s = s.replace(a3, "note('Le terrain est ' + (PZ.partiel ? 'en partie ' : '') + 'en zone ' + PZ.zone")
open(p, 'w', encoding='utf-8').write(s); print('ok peb2')
