# Zonages communaux : (1) extrait du plan officiel (plu_local4) ; (2) découpage déporté autorisé sur les copies stockées par TerrenUrbanisme
import sys, os, runpy
p = sys.argv[1]
runpy.run_path(os.path.join(os.path.dirname(__file__), 'plu_local4.py'), run_name='__main__')
s = open(p, encoding='utf-8').read()
old = "  if (!/^https:\\/\\/data\\.geopf\\.fr\\//.test(String(du || ''))) return new Response('adresse refusée', { status: 400 });\n  const L = await loadSrc(du, PART_MAX);"
if s.count(old) != 1: sys.exit('ancre introuvable : handlePdfPart')
s = s.replace(old, "  const SBP = (Deno.env.get('SUPABASE_URL') || '') + '/storage/v1/object/public/plu/';\n  if (!/^https:\\/\\/data\\.geopf\\.fr\\//.test(String(du || '')) && !String(du || '').startsWith(SBP)) return new Response('adresse refusée', { status: 400 });\n  const L = await loadSrc(du, PART_MAX);")
open(p, 'w', encoding='utf-8').write(s); print('patch plu_local5 appliqué')
