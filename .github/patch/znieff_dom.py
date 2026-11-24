"""ZNIEFF partout : l'API Carto ne couvre pas les ZNIEFF d'outre-mer ; pour les communes 97x, lecture complémentaire du WFS de la Géoplateforme (patrinat_znieff1 / patrinat_znieff2)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "    Promise.all(natureKeys.map(k => safe(gq('/nature/' + k, g), E))),"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
b = """    Promise.all(natureKeys.map(k => safe(gq('/nature/' + k, g), E).then(async r => {
      if ((r.features || []).length || !/^(znieff1|znieff2)$/.test(k) || !/^97/.test(String(INS || m.insee || ''))) return r;
      const lo = pt.coordinates[0], la = pt.coordinates[1], d = 0.0003;
      const w = await safe(getJSON(`https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=patrinat_${k}:${k}&OUTPUTFORMAT=application/json&COUNT=5&BBOX=${la - d},${lo - d},${la + d},${lo + d},urn:ogc:def:crs:EPSG::4326`, 15000), E);
      return (w && (w.features || []).length) ? w : r;
    }))),"""
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok')
