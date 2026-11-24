"""ABF : coordonnées officielles du service de l'architecte pour chaque département (table udap, Annuaire de l'administration), courriel cliquable."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)
rep("    return PT;\n  })();\n\n  // ----- Document -----",
    "    if (PT.spr || PT.sites.length || PT.abords.length || PT.probables.length || (PT.mh || []).length) {\n      try { const dep = String(INS).startsWith('97') ? String(INS).slice(0, 3) : String(INS).slice(0, 2); const { data: ud } = await admin.from('udap').select('*').eq('dep', dep).limit(1); if (ud && ud[0]) PT.udap = ud[0]; } catch (e) { console.warn('udap', String(e && e.message || e).slice(0, 120)); }\n    }\n    return PT;\n  })();\n\n  // ----- Document -----", 'collect')
i = s.find("      const UD = String(R.insee || '').startsWith('2B')")
j = s.find("Comptez un mois d\\'instruction en plus.', { size: 9.5 });", i)
j = s.find("Comptez un mois d\\'instruction en plus.', { size: 9.5 });", j + 10)
if i < 0 or j < 0: print('ANCRE rendu', i, j); sys.exit(1)
j = s.find('\n', j)
new = """      const UD = PT.udap || null, is2B = String(R.insee || '').startsWith('2B');
      h4('Obtenir son avis avant de déposer le permis');
      text('Avant de dessiner le projet définitif, envoyez un avant-projet au service de l\\'architecte des Bâtiments de France du département : il indique ce qu\\'il faut reprendre. Le dossier de permis se dépose ensuite en mairie, qui le lui transmet automatiquement. Comptez un mois d\\'instruction en plus.', { size: 9.5 });
      text('Pièces à joindre : ' + (is2B ? 'extrait cadastral, plans, coupes et façades de l\\'existant et du projet, photos et vues d\\'insertion proches et lointaines en couleur, notice précisant matériaux et couleurs, fiche de renseignements du service (sur son site).' : 'plan de situation et extrait cadastral, plans, coupes et façades du projet, photos du terrain et de ses abords, matériaux et couleurs envisagés.'), { size: 9 });
      if (UD) {
        const it = [['Service', UD.nom], ['Adresse', UD.adresse], ['Téléphone', UD.tel ? UD.tel + (UD.horaires && UD.horaires.length < 160 ? ' (' + UD.horaires.replace(/^Accueil téléphonique\\s*:?\\s*/i, '').replace(/\\.$/, '') + ')' : '') : ''], ['Courriel', UD.courriel], ['Prise de rendez-vous', UD.rdv], ['Site du service', UD.site], ['Fiche officielle', UD.fiche]].filter(x => x[1]);
        kvn(it, { lw: 0.26 });
        text('Coordonnées issues de l\\'Annuaire de l\\'administration (service-public.gouv.fr), mises à jour chaque mois.', { size: 8, color: C.muet });
      } else text('Le service de l\\'architecte des Bâtiments de France du département (unité départementale de l\\'architecture et du patrimoine) est joignable par la mairie ou sur lannuaire.service-public.gouv.fr.', { size: 9.5 });"""
s = s[:i] + new + s[j:]
rep("      const isUrl = typeof v === 'string' && /^https?:\\/\\/\\S+$/.test(v);\n      const label = isUrl ? (",
    "      const isMail = typeof v === 'string' && /^[^@\\s]+@[^@\\s]+\\.[a-z]{2,}$/i.test(v);\n      const isUrl = typeof v === 'string' && /^https?:\\/\\/\\S+$/.test(v);\n      const label = isUrl ? (", 'kv1')
rep("      if (isUrl) { try { linkAnnot(page, M + CW * lw, y - size - 6, F.widthOfTextAtSize(label, size) + 4, size + 6, v); } catch (e) {} }",
    "      if (isUrl) { try { linkAnnot(page, M + CW * lw, y - size - 6, F.widthOfTextAtSize(label, size) + 4, size + 6, v); } catch (e) {} }\n      if (isMail) { try { linkAnnot(page, M + CW * lw, y - size - 6, F.widthOfTextAtSize(v, size) + 4, size + 6, 'mailto:' + v); } catch (e) {} }", 'kv2')
open(p, 'w', encoding='utf-8').write(s); print('ok')
