# Prospection directe : envoi d'un e-mail à la fois depuis contact@terrenurbanisme.com, désinscription, import des contacts
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
CODE = open(__file__.replace('prospection.py', 'prospection_code.js'), encoding='utf-8').read()
rep("async function smtpSimple(toList, subject, text, html) {", "async function smtpSimple(toList, subject, text, html, xh) {")
rep("'Message-ID: <' + crypto.randomUUID() + '@terrenurbanisme.com>', 'MIME-Version: 1.0',", "'Message-ID: <' + crypto.randomUUID() + '@terrenurbanisme.com>', ...(xh || []), 'MIME-Version: 1.0',")
rep("async function villeCfg(slug) {", CODE + "\nasync function villeCfg(slug) {")
rep("  if (url.searchParams.get('ville')) { try { return await handleVille(req, url); }",
    "  if (url.searchParams.get('prospection')) { try { return await handleProspection(req, url); } catch (e) { console.error('prospection', e); return jres({ error: 'server' }, 500); } }\n  if (url.searchParams.get('desinscription')) return await handleDesinscription(String(url.searchParams.get('desinscription')));\n  if (url.searchParams.get('ville')) { try { return await handleVille(req, url); }")
open(p, 'w', encoding='utf-8').write(s); print('patch prospection appliqué')
