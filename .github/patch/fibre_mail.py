"""Fibre : numéro « 0 » retiré, adresses en capitales remises en forme, pas de tableau « plus proches » si le terrain a ses propres adresses. E-mails multiples séparés lisiblement."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(a, b, label):
    global s
    n = s.count(a)
    if n != 1: print('ANCRE', label, n); sys.exit(1)
    s = s.replace(a, b)
one("if (v === v.toUpperCase() || v === v.toLowerCase()) v =", "const up = (v.match(/[A-ZÀ-Ý]/g) || []).length, lo = (v.match(/[a-zà-ÿ]/g) || []).length;\n      if (up >= lo || !up) v =", 'casse')
one("const n = /^0+$/.test(String(o.num || '').trim()) ? '' : String(o.num || '').trim();", "const n = String(o.num || '').trim().replace(/^0+(\\s+|$)/, '').toUpperCase();", 'num')
one("{ const FL = ok && FB.list ? FB.list.filter(o => o.fibre).slice(0, 3) : [];", "{ const FL = ok && !opF.length && FB.list ? FB.list.filter(o => o.fibre).slice(0, 3) : [];", 'table')
one("['Courriel', ct && ct.email]", "['Courriel', ct && ct.email ? String(ct.email).split(/\\s*[;,]\\s*/).filter(Boolean).join(', ') : null]", 'mail1')
one("['E-mail', MAa && MAa.email ? MAa.email : null]", "['E-mail', MAa && MAa.email ? String(MAa.email).split(/\\s*[;,]\\s*/).filter(Boolean).join(', ') : null]", 'mail2')
one("['Courriel', UD.courriel]", "['Courriel', UD.courriel ? String(UD.courriel).split(/\\s*[;,]\\s*/).filter(Boolean).join(', ') : null]", 'mail3')
open(p, 'w', encoding='utf-8').write(s); print('ok fibre mail')
