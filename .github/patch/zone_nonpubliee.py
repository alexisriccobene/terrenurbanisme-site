"""Parcelle sans zonage publié en ligne : verdict neutre « À vérifier en mairie » au lieu de « Sous conditions », et type de document lu dans SUDOCUH."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: print('ANCRE', c, a[:120]); sys.exit(1)
    s = s.replace(a, b)
rep("let key, why, partiel = null;", "let key, why, partiel = null, nozone = false;")
rep(r"""else if (!zones.length) { key = 'cond'; why = 'Aucun zonage numérique n\'est publié pour cette parcelle. Le document d\'urbanisme doit être consulté en mairie.'; }""",
    r"""else if (!zones.length) { key = 'cond'; nozone = true; why = (c.doc.sduLib ? 'La commune dispose d' + (/^une /.test(c.doc.sduLib) ? '\'' + c.doc.sduLib : 'e ' + c.doc.sduLib) + ', mais son plan de zonage n\'est pas publié en ligne' : 'Aucun plan de zonage n\'est publié en ligne pour cette commune') + ' : la zone de la parcelle, et donc sa constructibilité, ne peuvent pas être déterminées de façon fiable dans ce rapport. Elles doivent être vérifiées en mairie, sur le plan de zonage du document en vigueur, avant tout engagement.'; }""")
rep("verdict: { key, word: partiel ? 'Constructible sous conditions' : WORD[key], partiel: partiel ? partiel.map(z => z.code) : null, title: partiel ?",
    "verdict: { key, nozone, word: nozone ? 'À vérifier en mairie' : partiel ? 'Constructible sous conditions' : WORD[key], partiel: partiel ? partiel.map(z => z.code) : null, title: nozone ? 'Zone non publiée en ligne : à vérifier en mairie' : partiel ?")
rep("ind.push({ label: 'Document d\\'urbanisme', value: (c.doc.type || 'Non déterminé') + (c.doc.date ? ' · ' + c.doc.date : ''), key: 'info' });",
    "ind.push({ label: 'Document d\\'urbanisme', value: (c.doc.type || ((String(c.doc.typeLabel || '').match(/\\(([^)]+)\\)/) || [])[1]) || (c.doc.typeLabel === 'Carte communale' ? 'Carte communale' : 'Non déterminé')) + (c.doc.date ? ' · ' + c.doc.date : ''), key: 'info' });")
open(p, 'w', encoding='utf-8').write(s); print('ok')
