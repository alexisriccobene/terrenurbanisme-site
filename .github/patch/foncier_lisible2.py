"""Foncier : libellés de procédure courts, avis de créances écartés, nom de société sur plusieurs lignes, arrondissements abrégés."""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(pat, rep, label):
    global s
    m = list(re.finditer(pat, s))
    if len(m) != 1: print('ANCRE', label, len(m)); sys.exit(1)
    s = s[:m[0].start()] + rep(m[0]) + s[m[0].end():]
# 1. kv : libellé replié sur plusieurs lignes
one(r"const ls = wrap\(String\(v\), F, 9\.5, CW \* 0\.66\);\s*ensure\(ls\.length \* 13\.5 \+ 8\);\s*page\.drawText\(clean\(k\), \{\s*x: M,\s*y,\s*size: 9,\s*font: B,\s*color: rgb\(C\.muet\)\s*\}\);",
    lambda m: """const ls = wrap(String(v), F, 9.5, CW * 0.66), kl = wrap(String(k), B, 9, CW * 0.31);
      ensure(Math.max(ls.length, kl.length) * 13.5 + 8);
      kl.forEach((l, i)=>page.drawText(l, { x: M, y: y - i * 13.5, size: 9, font: B, color: rgb(C.muet) }));""", 'kv')
one(r"y -= \(ls\.length - 1\) \* 13\.5 \+ 9;", lambda m: "y -= (Math.max(ls.length, kl.length) - 1) * 13.5 + 9;", 'kv-y')
# 2. Détail des sociétés : libellé court
one(r"s\.proc_nature \? s\.proc_nature \+ \(s\.proc_date \? ', publié le '", lambda m: "s.proc_nature ? natCourt(s.proc_nature) + (s.proc_date ? ', publié le '", 'detail')
# 3. Secteur : avis de créances écartés, libellé court, mandataire
one(r"/cl\[ôo\]ture\|r\[ée\]solution du plan\|homologation\|infirm\|rapport/i", lambda m: "/cl[ôo]ture|r[ée]solution du plan|homologation|infirm|rapport|cr[ée]ances|[ée]tat des|d[ée]p[ôo]t/i", 'excl')
one(r"nature: nat\.replace\(/\^Jugement .*?toUpperCase\(\)\),", lambda m: "nature: natCourt(nat),", 'nature')
one(r"mandataire: mm \? mm\[1\]\.trim\(\)\.replace\(/\\s\+/g, ' '\) : ''", lambda m: "mandataire: mm ? mm[1].trim().replace(/\\s+/g, ' ').replace(/^./, (c: string) => c.toUpperCase()) : ''", 'mand')
s = s.replace("(.{5,170}?)(?:\\.\\s|;|\\s+Les cr[ée]ances", "(.{5,230}?)(?:\\.\\s|;|\\s+Les cr[ée]ances", 1)
# 4. Arrondissements abrégés
one(r"\(s\.commune \|\| ''\) \+ ' · ' \+ \(s\.section", lambda m: "String(s.commune || '').replace(/ Arrondissement$/, '') + ' · ' + (s.section", 'arr')
open(p, 'w', encoding='utf-8').write(s); print('ok lisible2')
