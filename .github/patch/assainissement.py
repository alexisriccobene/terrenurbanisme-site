# Rapport : nouvelle rubrique « Quel raccordement pour les eaux usées ? »
# Verdict tiré du zonage d'assainissement (Géoportail de l'Urbanisme), de la zone du PLU et du service d'assainissement collectif de la commune (SISPEA).
# Le fait que le règlement admette l'assainissement individuel ne signifie plus « pas de tout-à-l'égout ».
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()

def indice(*mots):
    for i, l in enumerate(s.split('\n')):
        if any(m in l for m in mots): print('%d: %s' % (i + 1, l.strip()[:150]))
def rep(old, new, label):
    global s
    if s.count(old) != 1:
        indice('eauService', "h3('Assainissement')", "pas raccordable au réseau collectif")
        sys.exit('ancre introuvable ou multiple : ' + label)
    s = s.replace(old, new)

# 1. Données de la commune : service d'assainissement collectif et non collectif (SISPEA)
rep("async function eauService(insee) { const cd = await communeData(insee).catch(() => null); return cd && cd.eau ? cd.eau : null; }",
    "async function eauService(insee) { const cd = await communeData(insee).catch(() => null); if (!cd) return null; return Object.assign({}, cd.eau || {}, { ac: cd.ac || null, anc: cd.anc || null, sispea: !!(cd.ac || cd.anc) }); }",
    'eauService')

# 2. Rubrique du rapport
if "h3('Assainissement')" not in s: indice('Assainissement', 'eauService'); sys.exit('rubrique introuvable')
a = s.index("    if (A && A.assainissement) {\n      h3('Assainissement');")
b = s.index("      ensure(150); h4('Si le terrain n\\'est pas raccordable au réseau collectif');")
NEW = r"""    if ((A && A.assainissement) || (d.eau && d.eau.sispea)) {
      h3('Quel raccordement pour les eaux usées ?');
      const AS = String((A && A.assainissement) || '');
      const inf = (d.infos || []).concat(d.prescriptions || []).filter(p => /assainiss|eaux us/i.test(p.label || ''));
      const Z0a = d.zones && d.zones[0], tz = String((Z0a && Z0a.tz) || '').toUpperCase(), enU = /^U/.test(tz), enAU = /^AU/.test(tz);
      const zColl = inf.find(p => /collectif/i.test(p.label || '') && !/non[- ]?collectif/i.test(p.label || ''));
      const zAnc = inf.find(p => /non[- ]?collectif|autonome|individuel/i.test(p.label || ''));
      const EAa = d.eau || {}, AC = EAa.ac, connu = !!EAa.sispea;
      const opA = AC && AC.o && !/^r[ée]gie/i.test(AC.o) ? (d.ref.corse && /^veolia$/i.test(AC.o.trim()) ? 'Kyrnolia (groupe Veolia)' : AC.o) : '';
      const svcA = AC && AC.c ? (AC.c.toLowerCase() === String(d.ref.commune || '').toLowerCase() ? 'Commune de ' + AC.c : AC.c) : '';
      // Verdict : collectif (tout-à-l'égout) ou individuel (fosse, micro-station)
      let V, lvl, why;
      if (zColl && !zAnc) { V = 'Tout-à-l\'égout (assainissement collectif)'; lvl = 'ok'; why = 'Le terrain est classé en zone d\'assainissement collectif par le zonage d\'assainissement de la commune : la construction se raccorde au réseau public.'; }
      else if (zAnc && !zColl) { V = 'Assainissement individuel (fosse ou micro-station)'; lvl = 'cond'; why = 'Le terrain est classé en zone d\'assainissement non collectif par le zonage d\'assainissement de la commune : il n\'est pas prévu de le raccorder au réseau public.'; }
      else if (enU && (AC || !connu)) { V = 'Tout-à-l\'égout très probable'; lvl = 'ok'; why = 'Le terrain est en zone urbaine (' + (Z0a.code || tz) + ')' + (AC ? ' et la commune dispose d\'un réseau public d\'assainissement collectif' : '') + '. Dans ces zones, le réseau passe en général dans la voie et le règlement impose le raccordement lorsqu\'il existe. À confirmer par le service d\'assainissement pour ce terrain précis.'; }
      else if (connu && !AC) { V = 'Assainissement individuel (fosse ou micro-station)'; lvl = 'cond'; why = 'Aucun service public d\'assainissement collectif n\'est recensé pour cette commune : les constructions y sont équipées d\'un assainissement individuel, contrôlé par le SPANC.'; }
      else if (enAU && AC) { V = 'Tout-à-l\'égout prévu, selon l\'aménagement de la zone'; lvl = 'info'; why = 'Le terrain est en zone à urbaniser (' + (Z0a.code || tz) + ') : le raccordement au réseau public est en principe prévu avec l\'aménagement de la zone. Le service d\'assainissement indique si le réseau est déjà réalisé au droit du terrain.'; }
      else { V = 'Assainissement individuel probable'; lvl = 'cond'; why = 'Le terrain est hors zone urbaine' + (tz ? ' (zone ' + (Z0a.code || tz) + ')' : '') + ' : ces secteurs sont rarement desservis par le réseau public. Sauf canalisation existante dans la voie, prévoyez une fosse toutes eaux avec épandage ou une micro-station agréée.'; }
      const coll = /^Tout/.test(V);
      kvn([
        ['Raccordement à prévoir', V],
        ['Zone du PLU', Z0a ? (Z0a.code || tz) + (Z0a.typeLabel ? ' · ' + Z0a.typeLabel : '') : null],
        ['Zonage d\'assainissement', zColl && !zAnc ? 'Zone d\'assainissement collectif' : zAnc && !zColl ? 'Zone d\'assainissement non collectif' : inf.length ? inf[0].label : 'Non publié au Géoportail de l\'Urbanisme (consultable en mairie)'],
        ['Réseau collectif sur la commune', AC ? 'Oui' + (svcA ? ' · ' + svcA : '') + (AC.m ? ' · ' + (/d[ée]l[ée]g/i.test(AC.m) ? 'délégation' + (opA ? ' à ' + opA : '') : /r[ée]gie/i.test(AC.m) ? 'régie publique' : AC.m) : '') : connu ? 'Aucun service collectif recensé' : 'Information non disponible']
      ], { lw: 0.38 });
      note(why, lvl);
      if (AS) { h4('Ce que dit le règlement de la zone'); text(AS, { size: 9 }); if (/non[- ]collectif|individuel|autonome/i.test(AS) && coll) text('Le règlement admet un assainissement individuel uniquement là où le réseau public n\'existe pas : cette mention ne signifie pas que le terrain n\'est pas desservi.', { size: 8.5, color: C.muet }); }
      h4('Ce que cela coûte');
      if (coll) text('Raccordement au tout-à-l\'égout : branchement sous la voie réalisé par le service d\'assainissement (souvent 1 500 à 5 000 € selon la distance), canalisation sur le terrain jusqu\'à la maison, et participation pour le financement de l\'assainissement collectif (PFAC) fixée par la commune ou l\'intercommunalité, généralement de 1 000 à 5 000 €. Le service remet un devis à partir du plan de situation.', { size: 9 });
      else text('Assainissement individuel : 5 000 à 15 000 € selon la filière (détail ci-dessous), plus l\'étude de sol à la parcelle (500 à 1 000 €). Étapes : étude de sol, puis avis favorable du SPANC sur le projet, à joindre à la demande de permis de construire. ' + (d.ref.corse ? 'Installateur partenaire en Corse : Epuracqua, 04 95 58 57 10, contactepuracqua@rina.fr.' : 'Besoin d\'un installateur agréé ? Nous vous mettons en relation : contact@terrenurbanisme.com.'), { size: 9 });
      h4('Qui contacter pour obtenir la confirmation');
      const MAa = d.mairie;
      kvn([
        ['Service d\'assainissement', AC ? (svcA || 'Service de la commune') + (opA ? ' · exploitant : ' + opA : '') : connu ? 'SPANC (service public d\'assainissement non collectif), via la mairie' : 'Mairie, service urbanisme ou assainissement'],
        ['Mairie', MAa ? MAa.nom.replace(/^Mairie\s*-\s*/i, 'Mairie de ') : null],
        ['Téléphone', MAa && MAa.tel ? MAa.tel : null],
        ['E-mail', MAa && MAa.email ? MAa.email : null]
      ], { lw: 0.38 });
      bullet('Demandez au service d\'assainissement, avec la référence cadastrale, si une canalisation publique passe au droit du terrain, à quelle profondeur, et le montant de la PFAC. Sa réponse écrite vaut attestation de raccordabilité.', { size: 9 });
      bullet('Certificat d\'urbanisme opérationnel (formulaire Cerfa 13410, gratuit) : la mairie y indique officiellement si le terrain est desservi par le réseau d\'assainissement.', { size: 9 });
      bullet('Plan des réseaux : la présence des canalisations enterrées près du terrain peut être vérifiée sur reseaux-et-canalisations.gouv.fr, le guichet unique des réseaux.', { size: 9 });
      text('Sources : zonage d\'assainissement et règlement (Géoportail de l\'Urbanisme) ; services publics d\'assainissement (SISPEA, Office français de la biodiversité) ; annuaire de l\'administration (service-public.fr).', { size: 8, color: C.muet });

"""
s = s[:a] + NEW + s[b:]
rep("      ensure(150); h4('Si le terrain n\\'est pas raccordable au réseau collectif');",
    "      ensure(150); h4(coll ? 'Si le réseau public n\\'était finalement pas accessible' : 'Les solutions d\\'assainissement individuel');",
    'titre filieres')
open(p, 'w', encoding='utf-8').write(s)
print('patch assainissement appliqué')
