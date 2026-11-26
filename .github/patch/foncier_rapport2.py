"""Foncier : nouveau rapport PDF (couverture photo, synthèse, carte, fiches illustrées, mandataires, quatrième de couverture),
nom de fichier recherche-fonciere-<commune>-<rayon>km-<société>, lien de téléchargement sur le domaine du site."""
import sys, os
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
bloc = open(os.path.join(os.path.dirname(__file__), 'foncier_rapport2.ts'), encoding='utf-8').read()
a = s.index('// ---------- PDF ----------'); b = s.index('// ---------- E-mail ----------')
s = s[:a] + bloc + s[b:]
R = [
 ("  return { nomC, procs, maj, links, ench };", "  let mj: any[] = [];\n  try { const { data } = await admin.from('fon_mandataires').select('nom,cles,tel,email,site').limit(3000); mj = data || []; } catch (_) {}\n  return { nomC, procs, maj, links, ench, mj };"),
 ("const slug = slugify('recherche-fonciere-' + row.commune + '-' + row.rayon_km + 'km') + '-' + Array.from(rnd, (x)=>a[x % a.length]).join('');", "const slug = nomFichier(row) + '-' + Array.from(rnd, (x)=>a[x % a.length]).join('');"),
 ("      const link = FN + '?r=' + slug;", "      const link = await lienRapport(slug);"),
 ("          filename: slug + '.pdf',", "          filename: nomFichier(row) + '.pdf',"),
 ("select('pdf_path').eq('slug', slug)", "select('pdf_path,commune,rayon_km,societe,nom').eq('slug', slug)"),
 ("'Content-Disposition': `inline; filename=\"${slug}.pdf\"`,", "'Content-Disposition': `inline; filename=\"${nomFichier(row)}.pdf\"`,"),
 ("link = FN + '?r=' + row.slug, n0", "link = await lienRapport(row.slug), n0"),
 ("{ filename: row.slug + '.pdf', b64", "{ filename: nomFichier(row) + '.pdf', b64"),
 ("url: FN + '?r=' + row.slug,", "url: await lienRapport(row.slug),"),
 ("url: FN + '?r=' + g.slug,", "url: await lienRapport(g.slug),"),
 ("const slugify = (t)=>", """let relaisP: Promise<boolean> | null = null;
const lienRapport = async (slug: string) => {
  relaisP = relaisP || fetch(SITE + '/rapport-foncier/verif', { signal: AbortSignal.timeout(6000) }).then(async (r) => (await r.text()).trim() === 'Rapport introuvable').catch(() => false);
  return (await relaisP) ? SITE + '/rapport-foncier/' + slug : FN + '?r=' + slug;
};
const slugify = (t)=>"""),
]
for o, n in R:
    if s.count(o) != 1: print('ANCRE', s.count(o), o[:60]); sys.exit(1)
    s = s.replace(o, n)
open(p, 'w', encoding='utf-8').write(s); print('ok rapport2')
