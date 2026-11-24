# Compte de démonstration : accès à l'espace mairie de démonstration depuis Mon espace (mode Mairie)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("  if (b.action === 'mon_agence') {",
r"""  if (b.action === 'ville_demo') {
    if (!demoIllimite(u.user)) return jres({ error: 'demo' }, 403);
    const { data: vd } = await admin.from('villes').select('slug, cle_espace').eq('demo', true).order('created_at', { ascending: true }).limit(1).maybeSingle();
    if (!vd || !vd.cle_espace) return jres({ error: 'ville' }, 404);
    return jres({ slug: vd.slug, k: vd.cle_espace });
  }
  if (b.action === 'mon_agence') {""")
open(p, 'w', encoding='utf-8').write(s); print('patch ville démo appliqué')
