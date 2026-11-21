# Zone France Ruralités Revitalisation (FRR / FRR+) : statut de la commune (liste ANCT du 10/07/2025, stockage foncier/frr.json),
# point d'attention dans la synthèse et rubrique « Implanter une entreprise » dans le chapitre « Votre projet, étape par étape ».
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:80], s.count(a))
    s = s.replace(a, b)

# 1. Lecture de la liste (une fois par exécution)
rep("// ---------- Fibre et internet (Arcep, « Ma connexion internet ») ----------", """// ---------- Zone France Ruralités Revitalisation (ANCT, liste au 10 juillet 2025) ----------
let FRR_LISTE = null;
async function frrStatut(insee) {
  try {
    if (!FRR_LISTE) {
      const { data: blob } = await admin.storage.from('foncier').download('frr.json');
      if (!blob) return null;
      FRR_LISTE = JSON.parse(await blob.text());
    }
    let c = String(insee || '').toUpperCase();
    if (/^751\\d\\d$/.test(c)) c = '75056'; else if (/^6938\\d$/.test(c)) c = '69123'; else if (/^132\\d\\d$/.test(c)) c = '13055';
    return { code: FRR_LISTE.c[c] || '', date: FRR_LISTE.date };
  } catch (e) { console.warn('frr', String(e && e.message || e).slice(0, 120)); return null; }
}

// ---------- Fibre et internet (Arcep, « Ma connexion internet ») ----------""")

# 2. Point d'attention (synthèse)
rep("""    (RK0.techno || []).filter(r => r.present && r.adresse).forEach(r => ex.push(""", """    const FZ = await frrStatut(R.insee); d.frr = FZ;
    if (FZ && /^(S|P|B)$/.test(FZ.code)) ex.push({ key: 'info', text: 'Entreprise : la commune est ' + (FZ.code === 'P' ? 'classée en zone France Ruralités Revitalisation renforcée (FRR+)' : FZ.code === 'B' ? 'bénéficiaire du zonage France Ruralités Revitalisation jusqu\\'au 31 décembre 2027' : 'classée en zone France Ruralités Revitalisation (FRR)') + ' : une entreprise qui s\\'y crée peut être exonérée d\\'impôt sur les bénéfices pendant 5 ans, sous conditions (voir le chapitre « Votre projet, étape par étape »).' });
    else if (FZ && /^(SP|BP)$/.test(FZ.code)) ex.push({ key: 'cond', text: 'Entreprise : la commune n\\'est classée qu\\'en partie en zone France Ruralités Revitalisation ; l\\'exonération d\\'impôt sur les bénéfices dépend de la situation exacte du terrain (voir le chapitre « Votre projet, étape par étape »).' });
    (RK0.techno || []).filter(r => r.present && r.adresse).forEach(r => ex.push(""")

# 3. Rubrique détaillée, après la taxe d'aménagement
rep("""  } catch (e) { console.warn('taxe aménagement', String(e && e.message || e)); }
""", """  } catch (e) { console.warn('taxe aménagement', String(e && e.message || e)); }

  // Implanter une entreprise : zone France Ruralités Revitalisation
  try {
    const FZ = d.frr !== undefined ? d.frr : await frrStatut(R.insee);
    if (FZ) {
      const cn = R.commune || 'la commune', cd = FZ.code;
      ensure(150); h3('Implanter une entreprise : zone France Ruralités Revitalisation');
      if (cd === 'N') note('La commune de ' + cn + ' n\\'est pas classée en zone France Ruralités Revitalisation (FRR). Une entreprise qui s\\'y installe ne bénéficie pas de l\\'exonération d\\'impôt sur les bénéfices liée à ce zonage.', 'info');
      else if (!cd) note('La commune de ' + cn + ' ne figure pas dans la liste officielle des communes FRR du 10 juillet 2025 (commune créée ou modifiée depuis cette date). Son classement est à vérifier auprès du service des impôts des entreprises avant toute implantation.', 'cond');
      else {
        const plus = cd === 'P', ben = cd === 'B' || cd === 'BP', part = cd === 'SP' || cd === 'BP';
        note(part ? 'La commune de ' + cn + ' n\\'est classée qu\\'en partie' + (ben ? ' (commune bénéficiaire du zonage)' : '') + ' en zone France Ruralités Revitalisation. L\\'exonération dépend de la situation exacte du terrain : faites confirmer par le service des impôts des entreprises que l\\'adresse est dans la partie classée.'
          : plus ? 'La commune de ' + cn + ' est classée en zone France Ruralités Revitalisation renforcée (FRR+) depuis le 1er janvier 2025. Une entreprise qui s\\'y crée ou y reprend une activité peut être exonérée d\\'impôt sur les bénéfices pendant 5 ans, puis partiellement pendant 3 ans.'
          : ben ? 'La commune de ' + cn + ' fait partie des communes bénéficiaires du zonage France Ruralités Revitalisation (anciennes zones de revitalisation rurale). Les avantages FRR s\\'y appliquent aux entreprises créées ou reprises jusqu\\'au 31 décembre 2027.'
          : 'La commune de ' + cn + ' est classée en zone France Ruralités Revitalisation (FRR) depuis le 1er juillet 2024. Une entreprise qui s\\'y crée ou y est reprise peut être exonérée d\\'impôt sur les bénéfices pendant 5 ans, puis partiellement pendant 3 ans.', part ? 'cond' : 'ok');
        kv([
          ['Impôt sur les bénéfices (IS ou IR)', 'Exonération totale pendant 5 ans, puis exonération de 75 %, 50 % et 25 % des bénéfices les 3 années suivantes'],
          ['Création ou reprise', plus ? 'Entre le 1er janvier 2025 et le 31 décembre 2029' : ben ? 'Entre le 1er juillet 2024 et le 31 décembre 2027' : 'Entre le 1er juillet 2024 et le 31 décembre 2029'],
          ['Activités concernées', 'Industrielle, commerciale, artisanale ou libérale'],
          ['Taille de l\\'entreprise', plus ? 'Micro, petite ou moyenne entreprise au sens européen pour une création ; moins de 11 salariés pour une reprise' : 'Moins de 11 salariés'],
          ['Régime d\\'imposition', plus ? 'Tous régimes, y compris la micro-entreprise pour une création' : 'Régime réel obligatoire (micro-entreprise exclue, sauf option pour le réel)'],
          ['Implantation', plus ? 'Pas d\\'obligation d\\'exercer toute l\\'activité dans la zone' : 'Siège et totalité de l\\'activité dans la zone (activité sédentaire : 25 % du chiffre d\\'affaires au plus réalisé hors zone)'],
          ['Plafond', 'Aides de minimis : 300 000 € sur trois exercices'],
          ['Taxe foncière et CFE', 'Exonération possible si la commune ou l\\'intercommunalité l\\'a votée : à vérifier en mairie']
        ], { lw: 0.34 });
        text('Exclus : les activités agricoles, la gestion ou la location d\\'immeubles (une SCI de location nue n\\'est pas éligible) et la location meublée sans services de type hôtelier. Une location touristique ou des chambres d\\'hôtes peuvent être éligibles si le ménage quotidien et le linge sont fournis et inclus dans le prix.', { size: 8.5 });
        text('Ces avantages dépendent de la situation de l\\'entreprise (article 44 quindecies A du code général des impôts). Faites valider votre éligibilité par votre expert-comptable ou le service des impôts des entreprises avant de vous installer.', { size: 8.5, color: C.muet });
      }
      text('Source : ANCT, liste des communes classées FRR et FRR+ au 10 juillet 2025 (collectivites-locales.gouv.fr).', { size: 8, color: C.muet });
    }
  } catch (e) { console.warn('frr rubrique', String(e && e.message || e).slice(0, 120)); }
""")

# 4. Sources consultées
rep("""    ['Rapport officiel de risques', 'Géorisques, ministère chargé de l\\'environnement'],""", """    ['Rapport officiel de risques', 'Géorisques, ministère chargé de l\\'environnement'],
    ['Zone France Ruralités Revitalisation', 'ANCT, liste des communes classées FRR et FRR+ au 10 juillet 2025 ; article 44 quindecies A du code général des impôts'],""")
open(p, 'w', encoding='utf-8').write(s); print('patch zfrr appliqué')
