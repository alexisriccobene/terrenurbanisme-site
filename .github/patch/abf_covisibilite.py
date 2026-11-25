"""ABF : nature du périmètre (rayon 500 m ou périmètre délimité), covisibilité calculée sur le relief, ce que l'architecte examine et comment obtenir son avis avant le permis."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)

# 1) collecte : mode du périmètre + covisibilité
rep("      PT.mh = mh.slice(0, 8);\n",
"""      PT.mh = mh.slice(0, 8);
      try {
        const ac1L = supP_.filter(p => String(p.suptype || '').toLowerCase() === 'ac1');
        PT.abordsMode = ac1L.some(p => /délimit|PDA/i.test(String(p.typeass || '') + ' ' + String(p.nomass || ''))) ? 'pda' : (ac1L.length && ac1L.every(p => /tampon/i.test(String(p.modegeoass || '')) && (!p.paramcalc || Number(p.paramcalc) === 500))) ? 'rayon' : (ac1L.length ? 'inconnu' : 'rayon');
        const ringC = (pf.geometry.type === 'MultiPolygon' ? pf.geometry.coordinates[0][0] : pf.geometry.coordinates[0]);
        const obs = [turf.centroid(pf).geometry.coordinates]; const stC = Math.max(1, Math.floor((ringC.length - 1) / 6)); for (let i = 0; i < ringC.length - 1 && obs.length < 7; i += stC) obs.push(ringC[i]);
        const cand = (PT.abordsMode === 'pda') ? [] : mh.filter(x => x.d > 0).slice(0, 2);
        const cov = [];
        for (const x of cand) {
          const mo = (mons || []).find(m => m.ref === x.ref); if (!mo) continue;
          const N = 40, pts = [];
          obs.forEach(o => { for (let k = 0; k <= N; k++) pts.push([o[0] + (mo.lon - o[0]) * k / N, o[1] + (mo.lat - o[1]) * k / N]); });
          const Z = [];
          for (let i = 0; i < pts.length; i += 100) {
            const ch = pts.slice(i, i + 100);
            const j = await getJSON(`https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json?lon=${ch.map(q => q[0].toFixed(6)).join('|')}&lat=${ch.map(q => q[1].toFixed(6)).join('|')}&resource=ign_rge_alti_wld&zonly=true`, 15000);
            const z = (j.elevations || []).map(Number); if (z.length !== ch.length) throw new Error('altimétrie incomplète'); Z.push(...z);
          }
          let vis = false, okLines = 0;
          obs.forEach((o, oi) => {
            const z = Z.slice(oi * (N + 1), (oi + 1) * (N + 1)); if (z[0] < -100 || z[N] < -100) return; okLines++;
            const a = z[0] + 7, b = z[N] + 6; let clear = true;
            for (let k = 1; k < N; k++) { if (z[k] < -100) continue; if (z[k] > a + (b - a) * k / N + 0.5) { clear = false; break; } }
            if (clear) vis = true;
          });
          if (!okLines) continue;
          const z0 = Z[0], zm = Z[N];
          const br = (turf.bearing(turf.point(obs[0]), turf.point([mo.lon, mo.lat])) + 360) % 360;
          const dirs = ['au nord', 'au nord-est', 'à l\\'est', 'au sud-est', 'au sud', 'au sud-ouest', 'à l\\'ouest', 'au nord-ouest'];
          cov.push({ nom: x.nom, protection: x.protection, d: x.d, vis, dz: Math.round(zm - z0), dir: dirs[Math.round(br / 45) % 8] });
        }
        PT.covis = cov;
      } catch (e) { console.warn('covisibilité', String(e && e.message || e).slice(0, 120)); }
""", 'collecte')

# 2) verdict : accord à prévoir si visible, avis simple probable si masqué (rayon de 500 m seulement)
rep("  let abf = '';\n", "  let abf = '', abfCov = '';\n  const COV = (PAT.abordsMode === 'rayon' && !PAT.spr && !(PAT.sites || []).length && (PAT.covis || []).length) ? PAT.covis : null;\n  if (COV) abfCov = COV.some(x => x.vis) ? 'vis' : 'masque';\n", 'abf')
a = "'l\\'architecte des Bâtiments de France donne son avis sur les travaux et peut imposer des prescriptions (matériaux, couleurs, volumes).');\n    if (key === 'ok') key = 'cond';"
rep(a, "(abfCov === 'vis' ? 'd\\'après le relief, le terrain est visible depuis le monument : l\\'accord de l\\'architecte des Bâtiments de France est à prévoir, avec des prescriptions possibles (matériaux, couleurs, volumes).' : abfCov === 'masque' ? 'd\\'après le relief, le terrain n\\'est pas visible depuis le monument : l\\'architecte des Bâtiments de France devrait rendre un avis simple, sauf si le terrain et le monument se voient ensemble depuis un autre point.' : 'l\\'architecte des Bâtiments de France donne son avis sur les travaux et peut imposer des prescriptions (matériaux, couleurs, volumes).'));\n    if (abfCov === 'masque') abf = 'probable';\n    if (key === 'ok') key = 'cond';", 'why')
rep("abf === 'sur' && key === 'cond' ? 'Accord de l\\'architecte des Bâtiments de France obligatoire'", "abf === 'sur' && key === 'cond' ? (abfCov === 'vis' ? 'Accord de l\\'architecte des Bâtiments de France à prévoir' : 'Accord de l\\'architecte des Bâtiments de France obligatoire')", 'titre')
rep("abf === 'probable' && key === 'cond' ? 'Avis de l\\'architecte des Bâtiments de France probable'", "abf === 'probable' && key === 'cond' ? (abfCov === 'masque' ? 'Avis simple de l\\'architecte des Bâtiments de France probable' : 'Avis de l\\'architecte des Bâtiments de France probable')", 'titre2')

# 3) point clé
rep("pts.push({ key: 'cond', text: 'Abords de monument historique (' + PAT.abords.slice(0, 2).join(', ') + ') : accord de l\\'architecte des Bâtiments de France pour les travaux.' });",
    "pts.push({ key: 'cond', text: 'Abords de monument historique (' + PAT.abords.slice(0, 2).join(', ') + ') : ' + (abfCov === 'vis' ? 'terrain visible depuis le monument d\\'après le relief, accord de l\\'architecte des Bâtiments de France à prévoir.' : abfCov === 'masque' ? 'terrain masqué par le relief, avis simple de l\\'architecte des Bâtiments de France probable.' : 'accord de l\\'architecte des Bâtiments de France pour les travaux.') });", 'point')

# 4) synthèse
rep("if ((PT.abords || []).length) return 'Abords de monument historique : accord de l\\'architecte';",
    "if ((PT.abords || []).length) { const cv = PT.abordsMode === 'rayon' && (PT.covis || []).length ? (PT.covis.some(x => x.vis) ? 'vis' : 'masque') : ''; return cv === 'vis' ? 'Abords de monument historique : terrain visible depuis le monument, accord de l\\'architecte à prévoir' : cv === 'masque' ? 'Abords de monument historique : terrain masqué par le relief, avis simple probable' : PT.abordsMode === 'pda' ? 'Périmètre délimité des abords : accord de l\\'architecte' : 'Abords de monument historique : accord de l\\'architecte'; }", 'synthese')

# 5) section 2.5
rep("(PT.abords || []).length ? 'le terrain est aux abords d\\'un monument historique. Les travaux visibles de l\\'extérieur doivent recevoir l\\'accord de l\\'architecte des Bâtiments de France, qui peut imposer des prescriptions.'",
    "(PT.abords || []).length ? (PT.abordsMode === 'pda' ? 'le terrain est dans le périmètre délimité des abords d\\'un monument historique. Tous les travaux qui modifient l\\'aspect extérieur doivent recevoir l\\'accord de l\\'architecte des Bâtiments de France, qui peut imposer des prescriptions.' : 'le terrain est à moins de 500 m d\\'un monument historique. Si le terrain est visible depuis le monument, ou en même temps que lui, le projet doit recevoir l\\'accord de l\\'architecte des Bâtiments de France ; sinon, l\\'architecte rend un avis simple.')", 'enclair')
rep("(PT.abords || []).forEach(n => rows.push(['Abords de monument historique', n, 'Accord de l\\'architecte pour les travaux visibles (périmètre publié)']));",
    "(PT.abords || []).forEach(n => rows.push([PT.abordsMode === 'pda' ? 'Périmètre délimité des abords' : 'Abords de monument historique', n, PT.abordsMode === 'pda' ? 'Accord de l\\'architecte pour tous les travaux extérieurs' : PT.abordsMode === 'rayon' ? 'Rayon de 500 m autour du monument : accord de l\\'architecte en cas de covisibilité, avis simple sinon' : 'Accord de l\\'architecte pour les travaux visibles (périmètre publié)']));", 'ligne')

anc = "      text('Conseils : consulter l\\'architecte des Bâtiments de France (unité départementale"
i = s.find(anc)
if i < 0 or s.count(anc) != 1: print('ANCRE conseils', s.count(anc)); sys.exit(1)
j = s.find('\n', i)
old = s[i:j]
new = """      const COVr = PT.abordsMode === 'rayon' && !PT.spr && (PT.covis || []).length ? PT.covis : [];
      if (COVr.length) {
        h4('Le terrain est-il visible depuis le monument ?');
        COVr.forEach(x => {
          text(x.nom + ' (monument ' + (x.protection || 'protégé') + ') : à environ ' + fmt(Math.max(10, Math.round(x.d / 10) * 10)) + ' m ' + x.dir + ' du terrain, ' + (Math.abs(x.dz) < 5 ? 'à la même altitude.' : fmt(Math.abs(x.dz)) + ' m plus ' + (x.dz > 0 ? 'haut.' : 'bas.')), { size: 9.5 });
          note(x.vis ? 'D\\'après le relief, le terrain est visible depuis le monument. Il faut s\\'attendre à un avis conforme : le permis ne pourra être accordé qu\\'avec l\\'accord de l\\'architecte, en respectant ses prescriptions.' : 'D\\'après le relief, le terrain n\\'est pas visible depuis le monument. L\\'architecte devrait rendre un avis simple, que la mairie n\\'est pas tenue de suivre, sauf si le terrain et le monument se voient ensemble depuis un autre point (route, place, belvédère).', x.vis ? 'cond' : 'info');
        });
        text('Calcul sur le relief de l\\'IGN (RGE ALTI), entre le haut d\\'une construction de 7 m et le monument. Les arbres et les bâtiments ne sont pas pris en compte : l\\'architecte apprécie la covisibilité sur place.', { size: 8, color: C.muet });
      }
      h4('Ce que l\\'architecte examinera');
      ['L\\'implantation et le volume : une construction qui suit la pente et ne domine pas le paysage ni le monument.', 'La toiture : pente, matériau et couleur des couvertures, débords et installations en toiture (panneaux solaires, climatiseurs).', 'Les façades : teinte des enduits, proportions des ouvertures, menuiseries et volets.', 'Les abords : clôtures, murs, soutènements, piscine, plantations.'].forEach(t => bullet(t, { size: 9 }));
      text('Les règles d\\'aspect du règlement de la zone, au chapitre « Ce que vous pouvez construire », sont le premier cadre de son avis.', { size: 9 });
      const UD = String(R.insee || '').startsWith('2B') ? { n: 'Unité départementale de l\\'architecture et du patrimoine de Haute-Corse (UDAP 2B)', a: '2, rue de la Paroisse, La Citadelle, 20200 Bastia', t: '04 95 32 19 30', m: 'udap.haute-corse@culture.gouv.fr', p: 'extrait cadastral, plans, coupes et façades de l\\'existant et du projet, photos et vues d\\'insertion proches et lointaines en couleur, notice précisant matériaux et couleurs, fiche de renseignements du service' } : String(R.insee || '').startsWith('2A') ? { n: 'Unité départementale de l\\'architecture et du patrimoine de Corse-du-Sud (UDAP 2A)', a: 'Villa San Lazaro, 1 chemin de la Pietrina, 20704 Ajaccio cedex 9', t: '04 95 51 52 09', m: 'udap.corse-du-sud@culture.gouv.fr', p: '' } : null;
      h4('Obtenir son avis avant de déposer le permis');
      if (UD) {
        text('Envoyez un avant-projet par courriel pour une consultation préalable : l\\'architecte répond en indiquant ce qu\\'il faut reprendre pour le projet définitif. Le dossier de permis, déposé ensuite en mairie, lui est transmis automatiquement. Comptez un mois d\\'instruction en plus.', { size: 9.5 });
        if (UD.p) text('Pièces demandées : ' + UD.p + '.', { size: 9 });
        kvn([['Service', UD.n], ['Adresse', UD.a], ['Téléphone', UD.t], ['Courriel', UD.m]], { lw: 0.22 });
      } else text('Consultez l\\'unité départementale de l\\'architecture et du patrimoine (UDAP) du département avant de dessiner le projet, avec un avant-projet (plans, photos du site, matériaux et couleurs). Comptez un mois d\\'instruction en plus.', { size: 9.5 });"""
s = s[:i] + new + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
