"""Désinscription : retour au fonctionnement direct (un clic suffit), avec un message en texte simple lisible (l'hébergeur n'affiche pas le HTML)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
i = s.find("async function handleDesinscription(tok, meth = 'GET') {"); j = s.find("async function villeCfg(slug)")
if i < 0 or j < 0 or j < i: print('ANCRE', i, j); sys.exit(1)
new = """async function handleDesinscription(tok, meth = 'GET') {
  const page = (t) => new Response('TerrenUrbanisme\\n\\n' + t + '\\n\\nhttps://terrenurbanisme.com', { headers: { 'content-type': 'text/plain; charset=utf-8' } });
  if (!/^[0-9a-f-]{36}$/.test(tok)) return page('Lien invalide.');
  await admin.from('prospects').update({ statut: 'stop', stop_le: new Date().toISOString() }).eq('token', tok);
  return page('C\\'est noté : vous ne recevrez plus nos messages.');
}

"""
s = s[:i] + new + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
