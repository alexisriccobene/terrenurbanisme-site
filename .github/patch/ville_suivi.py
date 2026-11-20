# Page de la commune : suivi de la préparation du rapport, puis consultation en ligne et téléchargement
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("return jres({ ok: true, ref: orderRef }); }\n  const job = buildAndSend(sessionId, { user_id: null, insee, section, numero, commune, projet: projetCle(projet) }, orderRef, email, origine)",
    "return jres({ ok: true, ref: orderRef, s: sessionId }); }\n  const job = buildAndSend(sessionId, { user_id: null, insee, section, numero, commune, projet: projetCle(projet) }, orderRef, email, origine)")
rep("  if (typeof EdgeRuntime !== 'undefined' && EdgeRuntime.waitUntil) EdgeRuntime.waitUntil(job); else await job;\n  return jres({ ok: true, ref: orderRef });\n}",
    "  if (typeof EdgeRuntime !== 'undefined' && EdgeRuntime.waitUntil) EdgeRuntime.waitUntil(job); else await job;\n  return jres({ ok: true, ref: orderRef, s: sessionId });\n}")
rep("  if (b.action !== 'rapport') return jres({ error: 'action' }, 400);",
r"""  if (b.action === 'suivi') {
    const sid = String(b.s || '');
    if (!/^ville_[0-9a-f-]{36}$/.test(sid)) return jres({ error: 'session' }, 400);
    const { data: dz } = await admin.from('dossiers').select('status, download_slug, origine').eq('stripe_session_id', sid).maybeSingle();
    if (!dz || dz.origine !== 'ville_' + V.slug) return jres({ error: 'session' }, 404);
    return jres({ status: dz.status, lien: dz.status === 'ready' && dz.download_slug ? SITE + '/r/' + dz.download_slug : null, pdf: dz.status === 'ready' && dz.download_slug ? SITE + '/rapport/' + dz.download_slug + '.pdf' : null });
  }
  if (b.action !== 'rapport') return jres({ error: 'action' }, 400);""")
open(p, 'w', encoding='utf-8').write(s); print('patch suivi ville appliqué')
