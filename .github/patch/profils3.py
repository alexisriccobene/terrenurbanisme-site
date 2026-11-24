"""Rapport par profil : résultats partiels conservés si une source tarde, serveurs OpenStreetMap plus rapides, hauteur courte, argiles « important »."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: print('ANCRE', c, ':', old[:140]); sys.exit(1)
    s = s.replace(old, new)
rep("async function modulesPro(p, c, d) {\n  const out = {}, jobs = []", "async function modulesPro(p, c, d, out = {}) {\n  const jobs = []")
rep("""  if (d.profil && d.profil !== 'particulier') { try { d.pro = await withTimeout(modulesPro(d.profil, c, d), 30000); } catch (e) { console.warn('modules profil', String(e && e.message || e).slice(0, 160)); d.pro = {}; } }""",
    """  if (d.profil && d.profil !== 'particulier') { const PRO = {}; d.pro = PRO; try { await withTimeout(modulesPro(d.profil, c, d, PRO), 30000); } catch (e) { console.warn('modules profil', String(e && e.message || e).slice(0, 160), Object.keys(PRO).join(',')); } }""")
rep("signal: AbortSignal.timeout(20000) });\n      if (r.ok) { j = await r.json();", "signal: AbortSignal.timeout(9000) });\n      if (r.ok) { j = await r.json();")
rep("const q = `[out:json][timeout:18];", "const q = `[out:json][timeout:8];")
# Prix et loyers : distinguer « non publiés » et « source sans réponse »
rep("} else note('Prix et loyers non publiés pour cette commune par les sources officielles.", "} else note(!('prix' in P) && !('loyers' in P) ? 'Prix et loyers momentanément indisponibles (sources officielles sans réponse au moment du rapport).' + ' Les ventes réelles du secteur figurent au chapitre « Valeur de marché » ou « Environnement et marché immobilier ».' : 'Prix et loyers non publiés pour cette commune par les sources officielles.")
rep("else text(CP ? 'Aucune copropriété immatriculée", "else text(CP ? 'Aucune copropriété immatriculée")
rep("} else text('Aucun service recensé dans le rayon étudié, ou source momentanément indisponible.', { size: 9.5 });",
    "} else text(PR ? 'Aucun service recensé dans le rayon étudié.' : 'Source OpenStreetMap momentanément indisponible au moment du rapport.', { size: 9.5 });")
# Hauteur : texte court, sinon renvoi au chapitre
rep("['Hauteur', (() => { try { return typeof hauteurTexte === 'function' ? hauteurTexte(d) : null; } catch (e) { return null; } })()],",
    "['Hauteur', (() => { try { const h = typeof hauteurTexte === 'function' ? hauteurTexte(d) : null; return h && String(h).length <= 70 && !/…$/.test(h) ? h : 'Voir le chapitre « Ce que vous pouvez construire »'; } catch (e) { return null; } })()],")
rep("if (/moyen|fort/i.test(String(RKp.rga || ''))) note('Exposition ' + String(RKp.rga).toLowerCase() + ' au retrait-gonflement des argiles :",
    "if (/moyen|fort|important/i.test(String(RKp.rga || ''))) note('Retrait-gonflement des argiles (' + String(RKp.rga).toLowerCase() + ') :")
rep("['Assainissement', d.eau && (d.eau.ac || d.eau.anc) ? [d.eau.ac ? 'collectif dans la commune' : '', d.eau.anc ? 'non collectif (SPANC)' : ''].filter(Boolean).join(' · ') : null]",
    "['Assainissement', d.eau && (d.eau.ac || d.eau.anc) ? (d.eau.ac && d.eau.anc ? 'Réseau collectif et service d\\'assainissement non collectif (SPANC) dans la commune : raccordement de la parcelle à vérifier (chapitre accès et réseaux)' : d.eau.ac ? 'Réseau collectif dans la commune' : 'Assainissement non collectif (SPANC)') : null]")
open(p, 'w', encoding='utf-8').write(s); print('ok profils3')
