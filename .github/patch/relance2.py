"""Relance : accepte aussi la clé des tâches planifiées de la base (tu_cron_key), comme l'e-mail J+1."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "  if (url.searchParams.get('relance') && adminKey && safeEq(req.headers.get('x-tu-admin'), adminKey)) {"
assert s.count(a) == 1
s = s.replace(a, """  if (url.searchParams.get('relance') && req.method === 'POST' && await (async () => { const k = req.headers.get('x-tu-admin') || ''; if (adminKey && safeEq(k, adminKey)) return true; if (k.length !== 64) return false; try { const { data } = await admin.rpc('tu_check_cron_key', { k }); return data === true; } catch (e) { return false; } })()) {""")
open(p, 'w', encoding='utf-8').write(s); print('ok relance2')
