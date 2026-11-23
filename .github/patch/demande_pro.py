# Formulaire public « Offre personnalisée / Réserver une démonstration » : enregistrement (demandes_pro) + e-mail à contact@terrenurbanisme.com
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:80], s.count(a))
    s = s.replace(a, b)
rep("""async function handle(req) {
  const url = new URL(req.url);
""", """async function demandePro(req) {
  let b = {}; try { b = JSON.parse(await req.text()); } catch (e) { return jres({ error: 'format' }, 400); }
  const t = (v, n) => String(v == null ? '' : v).replace(/[\\u0000-\\u001f]+/g, ' ').trim().slice(0, n);
  if (t(b.site_web, 10)) return jres({ ok: true });
  const r = { type: b.type === 'demo' ? 'demo' : 'offre', nom: t(b.nom, 80), societe: t(b.societe, 120), email: t(b.email, 120).toLowerCase(), telephone: t(b.telephone, 30), profession: t(b.profession, 60), volume: t(b.volume, 40), creneau: t(b.creneau, 80), message: String(b.message || '').trim().slice(0, 2000), page: t(b.page, 120), ip: t((req.headers.get('x-forwarded-for') || '').split(',')[0], 60) };
  if (!r.nom || !/^[^@\\s]+@[^@\\s]+\\.[a-z]{2,}$/i.test(r.email)) return jres({ error: 'champs' }, 400);
  const depuis = new Date(Date.now() - 3600000).toISOString();
  const { count } = await admin.from('demandes_pro').select('id', { count: 'exact', head: true }).gte('created_at', depuis);
  if ((count || 0) >= 30) return jres({ error: 'limite' }, 429);
  if (r.ip) { const { count: c2 } = await admin.from('demandes_pro').select('id', { count: 'exact', head: true }).eq('ip', r.ip).gte('created_at', depuis); if ((c2 || 0) >= 5) return jres({ error: 'limite' }, 429); }
  await admin.from('demandes_pro').insert(r);
  const lib = r.type === 'demo' ? 'Demande de démonstration' : 'Demande d\\'offre personnalisée';
  const L = [['Nom', r.nom], ['Société', r.societe], ['E-mail', r.email], ['Téléphone', r.telephone], ['Profession', r.profession], ['Volume estimé', r.volume], ['Créneau souhaité', r.creneau], ['Page', r.page]].filter(x => x[1]);
  const txt = lib + '\\n\\n' + L.map(x => x[0] + ' : ' + x[1]).join('\\n') + (r.message ? '\\n\\nMessage :\\n' + r.message : '');
  const html = '<div style="font-family:Arial,sans-serif;font-size:14px;color:#2A1D17"><h2 style="font-size:18px">' + escH(lib) + '</h2><table style="border-collapse:collapse">' + L.map(x => '<tr><td style="padding:4px 14px 4px 0;color:#6E625A">' + escH(x[0]) + '</td><td style="padding:4px 0"><b>' + escH(x[1]) + '</b></td></tr>').join('') + '</table>' + (r.message ? '<p style="white-space:pre-wrap;margin-top:14px">' + escH(r.message) + '</p>' : '') + '</div>';
  try { await smtpSimple(['contact@terrenurbanisme.com'], lib + ' · ' + (r.societe || r.nom), txt, html); } catch (e) { console.error('demande pro mail', String(e && e.message || e).slice(0, 160)); }
  return jres({ ok: true });
}
async function handle(req) {
  const url = new URL(req.url);
  if (req.method === 'POST' && url.searchParams.get('demande') === 'pro') return await demandePro(req);
""")
open(p, 'w', encoding='utf-8').write(s); print('patch demande pro appliqué')
