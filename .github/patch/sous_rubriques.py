# Version client : sous-rubriques retirées une par une (le contenu est dessiné hors du document, la suite reprend à la même place)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("const PERSO = d.perso || null, EXC = (PERSO && PERSO.exclure) || [], SANS = (PERSO && PERSO.sans) || [];",
    "const PERSO = d.perso || null, EXC = (PERSO && PERSO.exclure) || [], SANS = (PERSO && PERSO.sans) || [], SOUS = (PERSO && PERSO.sous) || [];\n  let SKIP = null;\n  function endSkip() { if (SKIP) { page = SKIP.page; y = SKIP.y; SKIP = null; } }")
rep("  function newPage() { page = pdf.addPage([W, H]);", "  function newPage() { if (SKIP) { page = PDFLib.PDFPage.create(pdf); page.setSize(W, H); y = H - 92; return page; } page = pdf.addPage([W, H]);")
rep("  function h3(t, need) {\n    ensure(need || 150); y -= 8;",
    "  function h3(t, need) {\n    endSkip();\n    if (SOUS.length && SOUS.includes(CURT + '|' + clean(t))) { SKIP = { page, y }; page = PDFLib.PDFPage.create(pdf); page.setSize(W, H); y = H - 92; return; }\n    ensure(need || 150); y -= 8;")
rep("    CURT = title;\n    if (EXC.includes(title)) CHN--;", "    endSkip();\n    CURT = title;\n    if (EXC.includes(title)) CHN--;")
rep("  // Rubriques retirées par l'agence : pages supprimées, sommaire recalculé\n  if (EXC.length) {", "  endSkip();\n  // Rubriques retirées par l'agence : pages supprimées, sommaire recalculé\n  if (EXC.length) {")
rep("  d.perso = { exclure, sans, photos,", "  const sous = (Array.isArray(b.sous) ? b.sous : []).map(x => String(x).replace(/[<>]/g, '').slice(0, 260)).filter(x => /^[^|]{2,120}\\|.{1,140}$/.test(x)).slice(0, 120);\n  d.perso = { exclure, sans, sous, photos,")
rep("const req = { exclure, sans, reco:", "const req = { exclure, sans, sous, reco:")
rep("d.perso = { exclure: P.exclure || [], sans: P.sans || [], reco:", "d.perso = { exclure: P.exclure || [], sans: P.sans || [], sous: P.sous || [], reco:")
open(p, 'w', encoding='utf-8').write(s); print('patch sous-rubriques appliqué')
