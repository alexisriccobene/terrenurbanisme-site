"""Zone secondaire non constructible : présentation courte (caractère et usages admis), sans le tableau complet des règles ni les listes qui ne concernent pas un projet de construction ; vigilance dédoublonnée pour les autres zones secondaires."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', c, a[:90]); sys.exit(1)
    s = s.replace(a, b)
rep("      if (OA.caractere) { h4(OP('Caractère de la zone')); text(OA.caractere, { size: 9.5 }); }\n      const rg = (OA.regles || [])",
    "      if (OA.caractere) { h4(OP('Caractère de la zone')); text(OA.caractere, { size: 9.5 }); }\n      if (OZ && OZ.v === 'non' && (O.share || 0) < 0.5) { if (OA.autorise && OA.autorise.length) { h4(OP('Ce qui reste admis sur cette partie')); OA.autorise.slice(0, 6).forEach(t => bullet(t, { size: 9.5 })); } continue; }\n      const rg = (OA.regles || [])")
rep("      if (OA.points_vigilance && OA.points_vigilance.length) { h4(OP('Points de vigilance')); OA.points_vigilance.forEach(t => bullet(t, { size: 9.5, color: C.cond })); }",
    "      if (OA.points_vigilance && OA.points_vigilance.length) { const W = t => String(t || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').match(/[a-z0-9]{5,}/g) || []; const base = new Set(W(JSON.stringify({ ...OA, points_vigilance: null }))); const PV = OA.points_vigilance.filter(t => { const w = W(t).filter(x => !/^(verifier|parcelle|terrain|projet|possible|eventuel\\w*)$/.test(x)); return w.length && w.filter(x => base.has(x)).length / w.length < 0.75; }); if (PV.length) { h4(OP('Points de vigilance')); PV.forEach(t => bullet(t, { size: 9.5, color: C.cond })); } }")
open(p, 'w', encoding='utf-8').write(s); print('ok')
