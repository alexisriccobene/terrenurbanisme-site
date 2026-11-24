"""Lisibilité B : ensoleillement lisible, fibre expliquée (3 adresses), contacts des réseaux avec coordonnées."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag, n=1):
    global s
    c = s.count(a)
    if c != n: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)
def cut(start, end, new, tag):
    global s
    i = s.find(start); j = s.find(end, i + 1)
    if i < 0 or j < 0 or s.count(start) != 1: print('ANCRE', tag, i, j, s.count(start)); sys.exit(1)
    s = s[:i] + new + s[j:]

# Intercommunalité : coordonnées (geo.api.gouv.fr puis annuaire de l'administration)
rep("async function extras(b) {", """async function epciContact(insee) {
  const g = await getJSON(`https://geo.api.gouv.fr/communes/${insee}?fields=nom,codeEpci,epci`, 8000);
  const sir = g && (g.codeEpci || (g.epci && g.epci.code)); if (!sir) return null;
  const j = await getJSON(`https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/records?where=${encodeURIComponent(`siren="${sir}"`)}&select=nom,telephone,adresse_courriel,site_internet,pivot&limit=5`, 10000);
  const arr = v => { try { return typeof v === 'string' ? JSON.parse(v) : (v || []); } catch (e) { return []; } };
  const r = (j && j.results || []).find(x => /"epci"/.test(String(x.pivot || ''))) || (j && j.results || [])[0];
  if (!r) return { nom: (g.epci && g.epci.nom) || '' };
  return { nom: r.nom || (g.epci && g.epci.nom) || '', tel: (arr(r.telephone)[0] || {}).valeur || '', email: r.adresse_courriel || '', site: (arr(r.site_internet)[0] || {}).valeur || '' };
}
async function extras(b) {""", 'epcifn')
rep("  if (pm) delete pm.props;\n  return { pm, dpe, ta, elec, mairie, eau, opp, soleil, especes };",
    "  if (pm) delete pm.props;\n  const epci = await safe(withTimeoutC(epciContact(INS), 12000), null);\n  const eau2 = eau || (epci ? {} : null); if (eau2 && epci) eau2.epci = epci;\n  return { pm, dpe, ta, elec, mairie, eau: eau2, opp, soleil, especes };", 'extras')

# Ensoleillement : tableau lisible
rep("""      table([{ label: 'MOIS', w: 0.2, bold: true }, { label: 'SOLEIL POSSIBLE', w: 0.22 }, { label: 'SOLEIL SUR LE TERRAIN', w: 0.26 }, { label: 'PREMIER ET DERNIER RAYON', w: 0.32 }],
        SO.mois.map((r, i) => [MN[i], hm(r.th), r.eff ? hm(r.eff) : 'Aucun', r.lever && r.coucher ? r.lever.replace(':', ' h ') + ' – ' + r.coucher.replace(':', ' h ') : '—']), { size: 8 });""",
"""      { const r0 = SO.mois[0]; if (r0 && r0.eff && r0.lever && r0.coucher) text('Comment lire ce tableau : le 21 janvier, le soleil éclaire directement le terrain de ' + r0.lever.replace(':', ' h ') + ' à ' + r0.coucher.replace(':', ' h ') + ', soit ' + hm(r0.eff) + ' de soleil' + (r0.th > r0.eff + 0.2 ? ' ; le relief et les bâtiments voisins en retirent ' + hm(r0.th - r0.eff) + ' par rapport à un terrain sans obstacle.' : '.'), { size: 9 }); }
      table([{ label: 'MOIS', w: 0.24, bold: true }, { label: 'SOLEIL SUR LE TERRAIN', w: 0.42 }, { label: 'DURÉE', w: 0.34, bold: true }],
        SO.mois.map((r, i) => [MN[i], r.lever && r.coucher && r.eff ? 'de ' + r.lever.replace(':', ' h ') + ' à ' + r.coucher.replace(':', ' h ') : 'Pas de soleil direct', r.eff ? hm(r.eff) : '–']), { size: 8.5 });""", 'soleil')

# Fibre : boutons expliqués et 3 adresses fibrées
rep("        y -= bh + 12;\n      }\n      if (ok && FB.list && FB.list.length) table([{ label: 'DISTANCE', w: 0.12 }, { label: 'ADRESSE', w: 0.46 }, { label: 'FIBRE', w: 0.12, bold: true }, { label: 'AUTRES ACCÈS', w: 0.3 }],\n        FB.list.map(o => [fmt(o.d) + ' m', ad(o), o.fibre ? 'Oui' : 'Non', o.techs.filter(t => !/^(FO|FTTH|FIB)/i.test(t)).map(t => TECHNO_L[t] || t).join(', ') || '–']), { size: 8 });",
"""        y -= bh + 8;
        text('Carte fibre Orange : indique si l\\'adresse est raccordable à la fibre et, sinon, la date de déploiement prévue. Carte de l\\'Arcep : liste, adresse par adresse, les offres internet disponibles chez tous les opérateurs (fibre, ADSL, 4G, satellite). Une fois le terrain doté d\\'une adresse, saisissez-la sur ces cartes.', { size: 8.5, color: C.muet });
      }
      { const FL = ok && FB.list ? FB.list.filter(o => o.fibre).slice(0, 3) : [];
        if (FL.length) { h4('Les adresses fibrées les plus proches'); table([{ label: 'DISTANCE', w: 0.14 }, { label: 'ADRESSE', w: 0.5 }, { label: 'ACCÈS DISPONIBLES', w: 0.36 }],
        FL.map(o => [fmt(o.d) + ' m', ad(o), ['Fibre'].concat(o.techs.filter(t => !/^(FO|FTTH|FIB)/i.test(t)).map(t => TECHNO_L[t] || t)).filter((v, i2, a2) => a2.indexOf(v) === i2).join(', ')]), { size: 8.5 }); } }""", 'fibre')

# Réseaux : supprimer le doublon « Qui contacter » de 6.5 et refaire 6.7 avec coordonnées
cut("      const EA = d.eau, MA = d.mairie;\n      if (EA || MA) {\n        h4('Qui contacter');", "      text('Dans une promesse de vente, une condition suspensive portant sur le coût du raccordement", "", 'qui65')
new67 = r"""    if (d.acces || d.relief || FB) {
      h3('Qui contacter pour les réseaux');
      text('Avant d\'acheter, demandez à chaque gestionnaire si le terrain est desservi et combien coûte le raccordement : les réponses permettent de chiffrer le projet.', { size: 9 });
      const EA = d.eau || {}, MA = d.mairie, EP = EA.epci || null, maNom = MA ? MA.nom.replace(/^Mairie\s*-\s*/i, 'Mairie de ') : 'Mairie';
      const isInter = c => /communaut|m[ée]tropole|agglom|intercommun/i.test(String(c || ''));
      const isCom = c => String(c || '').toLowerCase() === String(d.ref.commune || '').toLowerCase();
      const contactOf = c => isInter(c) && EP && (EP.tel || EP.email) ? EP : (isCom(c) || !c) && MA ? { nom: maNom, tel: MA.tel, email: MA.email, site: MA.site } : null;
      let op = EA.o && !/^r[ée]gie/i.test(EA.o) ? EA.o : ''; if (op && d.ref.corse && /^veolia$/i.test(op.trim())) op = 'Kyrnolia (groupe Veolia)';
      const tc = t => t && t === t.toUpperCase() ? t.toLowerCase().replace(/(^|[\s'’-])(\p{L})/gu, (x, a, b) => a + b.toUpperCase()).replace(/\b(De|Du|Des|La|Le|Les|Et|D'|L')\b/g, w => w.toLowerCase()) : t;
      const bloc = (titre, qui, ct, ask) => {
        h4(titre);
        kvn([['Interlocuteur', qui], ['Téléphone', ct && ct.tel], ['Courriel', ct && ct.email], ['Site', ct && ct.site], ['À demander', ask]], { lw: 0.24 });
      };
      if (EA.c || MA) {
        const svc = EA.c ? tc(EA.c) + (EA.m && /r[ée]gie/i.test(EA.m) ? ' (régie' + (EA.o && EA.o !== EA.c ? ' ' + tc(EA.o) : '') + ')' : op ? ' (délégué à ' + tc(op) + ')' : '') : maNom;
        bloc('Eau potable et égouts', svc, contactOf(EA.c) || (MA ? { nom: maNom, tel: MA.tel, email: MA.email, site: MA.site } : null), 'Présence d\'une canalisation devant le terrain, coût du branchement, attestation de desserte.');
      }
      if (EA.anc && EA.anc.c && !(EA.c && EA.anc.c === EA.c)) bloc('Assainissement individuel (fosse, SPANC)', tc(EA.anc.c), contactOf(EA.anc.c), 'Avis sur la filière d\'assainissement, à partir de l\'étude de sol.');
      else if (EA.anc && EA.anc.c) text('Assainissement individuel (SPANC) : même service que l\'eau, à contacter pour valider la filière si le terrain n\'est pas raccordable aux égouts.', { size: 9 });
      { const g = d.elec && d.elec.grd ? d.elec.grd : (d.ref.corse ? 'EDF Corse' : /^97/.test(d.ref.insee) ? 'EDF' : 'Enedis'), I = String(d.ref.insee || '');
        const site = /enedis/i.test(g) ? 'https://www.enedis.fr' : d.ref.corse ? 'https://corse.edf.fr' : I.startsWith('971') ? 'https://guadeloupe.edf.fr' : I.startsWith('972') ? 'https://martinique.edf.fr' : I.startsWith('973') ? 'https://guyane.edf.fr' : I.startsWith('974') ? 'https://reunion.edf.fr' : I.startsWith('976') ? 'https://www.electricitedemayotte.com' : '';
        bloc('Électricité', g, { site }, 'Étude de raccordement et devis, sans frais, à partir de l\'adresse et du plan de situation.'); }
      bloc('Fibre et téléphone', 'Opérateurs présents à l\'adresse', { site: 'https://maconnexioninternet.arcep.fr/' }, 'Raccordement du futur logement, une fois la maison construite.');
      bloc('Avant de creuser (tous réseaux)', 'Guichet unique des réseaux', { site: 'https://www.reseaux-et-canalisations.ineris.fr/' }, 'Déclaration de projet de travaux (DT) : obligatoire et sans frais, elle localise les câbles et canalisations existants.');
      text('Sources : SISPEA (observatoire des services publics d\'eau), annuaire de l\'administration (service-public.gouv.fr), Agence ORE.', { size: 8, color: C.muet });
    }
"""
cut("    if (d.acces || d.relief || FB) {\n      h3('Qui contacter pour les réseaux');", "  // =====================================================================\n  // 5. ENVIRONNEMENT ET MARCHÉ", new67 + "  }\n\n", 'r67')
open(p, 'w', encoding='utf-8').write(s); print('ok B')
