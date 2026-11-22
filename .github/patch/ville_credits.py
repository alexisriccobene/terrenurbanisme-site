# Mairies : stock de rapports prépayé (sans abonnement) ; un rapport décompté par demande
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + old[:80])
    s = s.replace(old, new)
rep("  if (await cnt('ville', V.slug) >= (V.plafond_jour || 300)) return jres({ error: 'limite_ville' }, 429);",
    "  if (await cnt('ville', V.slug) >= (V.plafond_jour || 300)) return jres({ error: 'limite_ville' }, 429);\n  // Stock de rapports prépayé par la commune (null : sans limite, démonstration ou ancienne offre)\n  if (!V.demo && V.credits != null) { const { data: reste, error: re } = await admin.rpc('ville_debit', { p_slug: V.slug }); if (re || reste == null) return jres({ error: 'credits_epuises' }, 402); }")
rep("return jres({ ville: { ...pub, fin: V.fin || null, formule: V.formule || null }, demandes: rows });",
    "return jres({ ville: { ...pub, fin: V.fin || null, formule: V.formule || null, credits: V.credits == null ? null : V.credits }, demandes: rows });")
open(p, 'w', encoding='utf-8').write(s); print('patch ville_credits appliqué')
