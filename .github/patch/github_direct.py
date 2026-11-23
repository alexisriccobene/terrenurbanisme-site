# Rapports : génération confiée d'emblée au serveur GitHub (sans limite de calcul, version complète), comme pour les communes ;
# la fonction ne génère elle-même qu'en cas d'échec du déclenchement (et sur le serveur GitHub lui-même, TU_LOCAL).
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = """async function buildAndSend(sessionId, m, orderRef, email, origine, leger) {
  try {
"""
assert s.count(a) == 1
s = s.replace(a, a + """    if (!leger && !Deno.env.get('TU_LOCAL') && !String(origine || '').startsWith('ville_') && /^[A-Za-z0-9_-]+$/.test(sessionId)) {
      const tok = Deno.env.get('GITHUB_TOKEN');
      const { data: ex } = await admin.from('dossiers').select('status').eq('stripe_session_id', sessionId).maybeSingle();
      if (tok && ex) {
        try {
          const g = await fetch(`https://api.github.com/repos/${GH_REPO()}/dispatches`, { method: 'POST', headers: { Authorization: 'Bearer ' + tok, Accept: 'application/vnd.github+json', 'User-Agent': 'TerrenUrbanisme', 'content-type': 'application/json' }, body: JSON.stringify({ event_type: 'rapport_secours', client_payload: { session: sessionId } }) });
          if (g.ok) {
            await admin.from('dossiers').update({ status: 'pending', relances: 3, updated_at: new Date().toISOString() }).eq('stripe_session_id', sessionId);
            console.log('rapport confié au serveur GitHub', orderRef);
            return;
          }
          console.warn('serveur GitHub : déclenchement', g.status);
        } catch (e) { console.warn('serveur GitHub', String(e && e.message || e).slice(0, 160)); }
      }
    }
""")
open(p, 'w', encoding='utf-8').write(s); print('patch GitHub direct appliqué')
