"""Commerces : requête OpenStreetMap lancée en parallèle, délai borné."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
i = s.find("  let OSM = null;\n  try {\n    const q = `[out:json]")
j = s.find("  const telFR_ = t =>", i)
if i < 0 or j < 0: print('ANCRE osm', i, j); sys.exit(1)
blk = s[i:j]
blk = blk.replace("  let OSM = null;\n  try {", "  const osmP = (async () => {\n  let OSM = null;\n  try {", 1)
blk = blk.replace("AbortSignal.timeout(25000)", "AbortSignal.timeout(12000)").replace("'https://overpass.private.coffee/api/interpreter', 'https://overpass.kumi.systems/api/interpreter'", "'https://overpass.private.coffee/api/interpreter'")
blk = blk.rstrip('\n') + "\n  return OSM;\n  })();\n"
s = s[:i] + blk + s[j:]
a = "      if (E.length && E[0].d <= r * 1000 * 1.05) { const os = OSM && OSMK[lab]"
if s.count(a) != 1: print('ANCRE use'); sys.exit(1)
s = s.replace(a, "      if (E.length && E[0].d <= r * 1000 * 1.05) { const OSM = await Promise.race([osmP, new Promise(z => setTimeout(() => z(null), 8000))]); const os = OSM && OSMK[lab]")
open(p, 'w', encoding='utf-8').write(s); print('ok F')
