"""Désinscription : un simple passage sur le lien (robots anti-spam des entreprises) ne désinscrit plus ; il faut cliquer sur « Confirmer » (ou un envoi POST du logiciel de messagerie)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', c, a[:100]); sys.exit(1)
    s = s.replace(a, b)
rep("return await handleDesinscription(String(url.searchParams.get('desinscription')));",
    "return await handleDesinscription(String(url.searchParams.get('desinscription')), req.method);")
rep("""async function handleDesinscription(tok) {""", """async function handleDesinscription(tok, meth = 'GET') {""")
rep("""  await admin.from('prospects').update({ statut: 'stop', stop_le: new Date().toISOString() }).eq('token', tok);
  return page('C\\'est noté : vous ne recevrez plus nos messages.');""",
"""  if (meth !== 'POST') return page('Vous ne souhaitez plus recevoir nos messages ?<br><br><form method="post" action="https://terrenurbanisme.com/desinscription/' + tok + '" style="margin:0"><button type="submit" style="background:#A3462C;color:#fff;border:0;border-radius:12px;padding:13px 24px;font-size:15px;font-weight:700;cursor:pointer">Confirmer la désinscription</button></form>');
  await admin.from('prospects').update({ statut: 'stop', stop_le: new Date().toISOString() }).eq('token', tok);
  return page('C\\'est noté : vous ne recevrez plus nos messages.');""")
open(p, 'w', encoding='utf-8').write(s); print('ok')
