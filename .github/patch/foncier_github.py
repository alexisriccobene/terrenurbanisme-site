"""Foncier entreprises : génération sur un serveur GitHub (sans limite de calcul) puis envoi par la fonction."""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
m = re.findall(r"const g = await generer\(row,", s)
if len(m) != 1: print('ANCRE generer', len(m)); sys.exit(1)
s = s.replace(m[0], """if (!isAdmin && !Deno.env.get('TU_LOCAL')) {
        if (row.statut === 'pret' && row.slug) return json({ statut: 'pret', url: FN + '?r=' + row.slug, n: row.nb_sites, commune: row.commune, rayon_km: row.rayon_km });
        const lance = row.gh_lance ? new Date(row.gh_lance).getTime() : 0;
        if (Date.now() - lance > 8 * 60000) {
          const tok = Deno.env.get('GITHUB_TOKEN');
          if (!tok) return json({ error: 'token' }, 500);
          const gh = await fetch('https://api.github.com/repos/alexisriccobene/terrenurbanisme-site/dispatches', { method: 'POST', headers: { Authorization: 'Bearer ' + tok, Accept: 'application/vnd.github+json', 'User-Agent': 'TerrenUrbanisme', 'content-type': 'application/json' }, body: JSON.stringify({ event_type: 'foncier_generer', client_payload: { id: row.id } }) });
          if (!gh.ok) { console.error('dispatch', gh.status, await gh.text()); return json({ error: 'dispatch' }, 502); }
          await admin.from('fon_demandes').update({ statut: 'generation', gh_lance: new Date().toISOString() }).eq('id', row.id);
        }
        return json({ statut: 'generation' }, 202);
      }
      const g = await generer(row,""", 1)
m = re.findall(r"if \(b\.action === ['\"]generer['\"]\) \{", s)
if len(m) != 1: print('ANCRE action', len(m)); sys.exit(1)
s = s.replace(m[0], """if (b.action === 'envoyer') {
      const isAdm = !!Deno.env.get('ADMIN_KEY') && req.headers.get('x-tu-admin') === Deno.env.get('ADMIN_KEY');
      if (!isAdm) return json({ error: 'admin' }, 403);
      const { data: row } = await admin.from('fon_demandes').select('*').eq('id', Number(b.id)).maybeSingle();
      if (!row || row.statut !== 'pret' || !row.pdf_path) return json({ error: 'pas_pret' }, 409);
      if (row.envoye_le && !b.force) return json({ statut: 'deja_envoye' });
      const { data } = await admin.storage.from('foncier').download(row.pdf_path);
      if (!data) return json({ error: 'pdf' }, 404);
      const bytes = new Uint8Array(await data.arrayBuffer()), link = FN + '?r=' + row.slug, n0 = row.nb_sites || 0;
      await smtpRaw([row.email], 'Votre recherche foncière : ' + row.commune + ' (' + row.rayon_km + ' km)', 'Bonjour,\\n\\nLe rapport de votre recherche foncière autour de ' + row.commune + ' (' + row.rayon_km + ' km) recense ' + nb(n0) + ' sites. Il est joint en PDF.\\nTéléchargement : ' + link + '\\n\\nTerrenUrbanisme · ' + SITE + ' · contact@terrenurbanisme.com', mailHtml(row, n0, link), { filename: row.slug + '.pdf', b64: b64bytes(bytes) });
      await admin.from('fon_demandes').update({ envoye_le: new Date().toISOString() }).eq('id', row.id);
      return json({ statut: 'envoye' });
    }
    """ + m[0], 1)
open(p, 'w', encoding='utf-8').write(s); print('ok github')
