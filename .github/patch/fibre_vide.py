# Fibre : commune préparée sans adresse à moins de 400 m -> on renvoie les adresses les plus proches (jusqu'à 3 km), sans repasser par la lecture du département
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:80], s.count(a))
    s = s.replace(a, b)
rep("""    if (cache && Array.isArray(cache.rows)) {
      const list = [];""", """    if (cache && Array.isArray(cache.rows)) {
      const list = [], far = [];""")
rep("""        const d = Math.hypot((ll[0] - lon) * 111320 * k, (ll[1] - lat) * 110574); if (d > R) continue;
        const techs = (Array.isArray(r0[7]) ? r0[7] : []).map(String).filter(Boolean);
        list.push(""", """        const d = Math.hypot((ll[0] - lon) * 111320 * k, (ll[1] - lat) * 110574); if (d > 3000) continue;
        const techs = (Array.isArray(r0[7]) ? r0[7] : []).map(String).filter(Boolean);
        (d > R ? far : list).push(""")
rep("""      if (list.length) {
        list.sort((a1, b1) => a1.d - b1.d);""", """      if (!list.length && far.length) { far.sort((a1, b1) => a1.d - b1.d); list.push(...far.slice(0, 5)); }
      if (true) {
        list.sort((a1, b1) => a1.d - b1.d);
        const inR = list.filter(x => x.d <= R);""")
rep("""        const cnt = { n100: list.filter(x => x.d <= 100).length, f100: list.filter(x => x.d <= 100 && x.fibre).length, n400: list.length, f400: list.filter(x => x.fibre).length };""",
    """        const cnt = { n100: inR.filter(x => x.d <= 100).length, f100: inR.filter(x => x.d <= 100 && x.fibre).length, n400: inR.length, f400: inR.filter(x => x.fibre).length };""")
open(p, 'w', encoding='utf-8').write(s); print('patch fibre vide appliqué')
