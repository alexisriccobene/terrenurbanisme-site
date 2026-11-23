# Mesure du temps de fabrication du PDF par chapitre (journal), pour réduire le calcul des gros rapports
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = """  function chapter(num, title, sub) {
    CURT = title;"""
if s.count(old) != 1: sys.exit('ancre chapter')
s = s.replace(old, """  function chapter(num, title, sub) {
    try { console.log('pdf chrono', CURT || 'début', Date.now() - T0PDF, 'ms'); } catch (e) {}
    CURT = title;""")
old2 = "let page, y, CHN = 0, CUR = '', CURT = ''; let pages = []; let toc = [];"
if s.count(old2) != 1: sys.exit('ancre T0')
s = s.replace(old2, old2 + "\n  const T0PDF = Date.now();")
old3 = "  // Rubriques retirées par l'agence : pages supprimées, sommaire recalculé"
if s.count(old3) != 1: sys.exit('ancre fin')
s = s.replace(old3, "  try { console.log('pdf chrono', CURT, Date.now() - T0PDF, 'ms (fin des chapitres)'); } catch (e) {}\n" + old3)
open(p, 'w', encoding='utf-8').write(s); print('patch chrono appliqué')
