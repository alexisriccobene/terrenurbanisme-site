"""Correctifs : « dispose d'un PLU », hauteur de la synthèse lue dans les chiffres du règlement (jamais une règle de clôture ou de piscine)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: print('ANCRE', c, a[:120]); sys.exit(1)
    s = s.replace(a, b)
rep(r"""'La commune dispose d' + (/^une /.test(c.doc.sduLib) ? '\'' + c.doc.sduLib : 'e ' + c.doc.sduLib)""", r"""'La commune dispose d\'' + c.doc.sduLib""")
rep("let ht = null; try { ht = typeof hauteurTexte === 'function' ? hauteurTexte(d) : null; } catch (e) {}",
    "let ht = null; try { const chh = (RG.analysis && RG.analysis.chiffres) || {}, hf = Number(chh.hauteur_facade_max_m) || 0, hft = Number(chh.hauteur_faitage_max_m) || 0; ht = hf > 0 ? nb(hf) + ' m à l\\'égout ou à l\\'acrotère' + (hft > hf ? ', ' + nb(hft) + ' m au faîtage' : '') : hft > 0 ? nb(hft) + ' m au faîtage' : (typeof hauteurTexte === 'function' ? hauteurTexte(d) : null); } catch (e) {}")
rep("if (Array.isArray(o.regles)) { const r = o.regles.find(x => x && /hauteur/i.test(x.critere || '')); if (r && r.regle) return String(r.regle); }",
    "if (Array.isArray(o.regles)) { const hr = o.regles.filter(x => x && /hauteur/i.test(x.critere || '')); const r = hr.find(x => !/cl[oô]ture|piscine|annexe|\\bmur|haie|abri/i.test(x.critere || '')) || null; if (r && r.regle) return String(r.regle); }")
open(p, 'w', encoding='utf-8').write(s); print('ok')
