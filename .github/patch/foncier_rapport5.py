"""Foncier : bandes étroites écartées au contrôle, dirigeants sans commissaires aux comptes, activité complète, sites non contrôlés expliqués."""
import sys, os
d = os.path.dirname(__file__)
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index('// ---------- Secteur'); b = s.index('// ---------- PDF ----------'); c = s.index('// ---------- E-mail ----------')
s = s[:a] + open(os.path.join(d, 'foncier_rapport5_secteur.ts'), encoding='utf-8').read() + open(os.path.join(d, 'foncier_rapport5.ts'), encoding='utf-8').read() + '\n' + s[c:]
R = [
 ("        if (a >= 50) { drop.add(x); bati++; x.bati_autre = Math.round(a); } else { ok++; x.verifie = true; }",
  """        // Forme : une bande étroite (talus, bord de route, délaissé) ne sert pas à une entreprise
        let A = 0, P = 0; for (const p of ps) { A += ringM2(p[0], p[0][0][1]); const r = p[0]; for (let k2 = 1; k2 < r.length; k2++) P += hav(r[k2 - 1][1], r[k2 - 1][0], r[k2][1], r[k2][0]) * 1000; }
        const pp = P > 0 ? 4 * Math.PI * A / (P * P) : 1;
        if (a >= 50) { drop.add(x); bati++; x.bati_autre = Math.round(a); } else if (pp < 0.22) { drop.add(x); etroit++; } else { ok++; x.verifie = true; }"""),
 ("  let ok = 0, bati = 0, i = 0;", "  let ok = 0, bati = 0, etroit = 0, i = 0;"),
 ("  console.log('verif', { ok, bati, nonControles, ms: Date.now() - t0 });\n  return { ok, bati, nonControles };", "  console.log('verif', { ok, bati, etroit, nonControles, ms: Date.now() - t0 });\n  return { ok, bati, etroit, nonControles };"),
]
for o, n in R:
    if s.count(o) != 1: print('ANCRE', o[:60]); sys.exit(1)
    s = s.replace(o, n)
open(p, 'w', encoding='utf-8').write(s); print('ok rapport5')
