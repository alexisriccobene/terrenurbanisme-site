# Version client : retrait fiable des rubriques (suppression en ordre décroissant, renumérotation des pages et du sommaire)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:80]))
    s = s.replace(old, new)
rep("function newPage() { page = pdf.addPage([W, H]); page.__ch = CURT; pages.push(page); header(page); y = H - 92; return page; }",
    "function newPage() { page = pdf.addPage([W, H]); page.__ch = CURT; page.__i = pdf.getPageCount() - 1; pages.push(page); header(page); y = H - 92; return page; }")
rep("""    const rm = pages.filter(pg => EXC.includes(pg.__ch));
    for (const pg of rm) { const i = pdf.getPages().indexOf(pg); if (i >= 0) pdf.removePage(i); }
    pages = pages.filter(pg => !rm.includes(pg));
    toc = toc.filter(t => !EXC.includes(t.title));
    toc.forEach(t => { if (t._p) t.page = pdf.getPages().indexOf(t._p) + 1; else t.page -= rm.length; });""",
"""    const rm = pages.filter(pg => EXC.includes(pg.__ch) && pg.__i != null);
    const idx = rm.map(pg => pg.__i).sort((a, b) => b - a);
    for (const i of idx) pdf.removePage(i);
    RMIDX = idx;
    pages = pages.filter(pg => !rm.includes(pg));
    toc = toc.filter(t => !EXC.includes(t.title));
    toc.forEach(t => { if (t._p && t._p.__i != null) t.page = NEWI(t._p.__i) + 1; else t.page -= rm.length; });""")
rep("  const PERSO = d.perso || null, EXC = (PERSO && PERSO.exclure) || [], SANS = (PERSO && PERSO.sans) || [];",
    "  const PERSO = d.perso || null, EXC = (PERSO && PERSO.exclure) || [], SANS = (PERSO && PERSO.sans) || [];\n  let RMIDX = []; const NEWI = i => i - RMIDX.filter(r => r < i).length;")
rep("""    const pg = (ALLP.indexOf(p) + 1) + ' / ' + pdf.getPageCount();""",
    """    const pg = ((p.__i != null ? NEWI(p.__i) : ALLP.indexOf(p)) + 1) + ' / ' + pdf.getPageCount();""")
open(p, 'w', encoding='utf-8').write(s); print('patch perso3 appliqué')
