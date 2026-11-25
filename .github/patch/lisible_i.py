"""Commerces : nom commercial et téléphone depuis la table commerces (BANCO, OpenStreetMap), sans appel Overpass."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
i = s.find("  const osmP = (async () => {")
j = s.find("  })();\n", i)
if i < 0 or j < 0: print('ANCRE', i, j); sys.exit(1)
j += len("  })();\n")
s = s[:i] + """  const osmP = (async () => {
    try {
      const { data } = await admin.from('commerces').select('k, nom, marque, tel, mail, lon, lat').gte('lat', lat - 0.03).lte('lat', lat + 0.03).gte('lon', lon - 0.04).lte('lon', lon + 0.04).limit(1500);
      return (data || []).map(e => ({ k: e.k, nom: e.nom || e.marque, tel: e.tel || '', mail: e.mail || '', d: dm(e.lat, e.lon) })).filter(e => e.nom);
    } catch (e) { console.warn('commerces', String(e && e.message || e).slice(0, 80)); return null; }
  })();
""" + s[j:]
a = "const OSM = await Promise.race([osmP, new Promise(z => setTimeout(() => z(null), 22000))]);"
if s.count(a) != 1: print('ANCRE race'); sys.exit(1)
s = s.replace(a, "const OSM = await Promise.race([osmP, new Promise(z => setTimeout(() => z(null), 6000))]);")
open(p, 'w', encoding='utf-8').write(s); print('ok I')
