# Sommaire : une ligne par chapitre (titre, description courte, page), espacée et lisible, au lieu de la liste serrée des sous-parties
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index("    for (const t of all) {\n      const subs = (t.subs || [])")
b = s.index("    p.drawText(clean('Astuce : cliquez sur un titre ou une sous-partie pour y accéder directement.'), { x: M, y: 56, size: 8, font: F, color: C.muet });", a)
NEW = r"""    const COURT = {
      'Synthèse': 'Le verdict, les indicateurs clés et les points d\'attention en une page.',
      'Identification de la parcelle': 'Localisation, surface, références cadastrales et voisinage du terrain.',
      'Règles d\'urbanisme applicables': 'Document d\'urbanisme, zone du terrain, prescriptions et servitudes.',
      'Ce que vous pouvez construire': 'Surface constructible, hauteur, reculs, aspect et usages autorisés.',
      'Règles propres à la Corse': 'Loi Littoral, loi Montagne et PADDUC appliqués à la parcelle.',
      'Loi Littoral et loi Montagne': 'Les lois qui s\'ajoutent au document d\'urbanisme sur le littoral et en montagne.',
      'Risques naturels et technologiques': 'Inondation, feu de forêt, argiles, catastrophes naturelles et sites pollués.',
      'Le terrain : accès, relief et réseaux': 'Accès, pente, ensoleillement, eaux usées, électricité, eau et fibre.',
      'Valeur de marché': 'La fourchette de prix du terrain d\'après les ventes réelles du secteur.',
      'Environnement et marché immobilier': 'Espaces naturels, espèces protégées et ventes immobilières alentour.',
      'Historique du site': 'Le terrain vu du ciel au fil des années et les permis accordés autour.',
      'Opportunités autour du terrain': 'Grands terrains peu bâtis et logements énergivores à proximité.',
      'Votre projet, étape par étape': 'De l\'achat aux impôts : démarches, délais, coûts, contacts et taxe.',
      'État des risques (ERP) pré-rempli': 'Le formulaire réglementaire à remettre à l\'acquéreur, pré-rempli.',
      'Professionnels recommandés': 'Les professionnels partenaires qui interviennent dans votre commune.',
      'Avertissement et sources': 'La portée de ce rapport et les sources publiques consultées.',
      'Annexe : règlement de la zone': 'Les pages officielles du règlement de la zone, telles qu\'approuvées.',
      'Annexe : rapport officiel Géorisques': 'Le rapport de risques Géorisques, reproduit intégralement.'
    };
    const rowH = all.length > 16 ? 34 : 37;
    for (const t of all) {
      if (yy - rowH < 70) break;
      p.drawLine({ start: { x: M, y: yy }, end: { x: W - M, y: yy }, thickness: 0.5, color: C.ligne });
      const ns = t.num === '' ? 'S' : typeof t.num === 'number' ? String(t.num).padStart(2, '0') : String(t.num);
      p.drawRectangle({ x: M, y: yy - rowH + 7, width: 30, height: rowH - 14, color: t.num === '' ? C.soft : C.t });
      p.drawText(ns, { x: M + 15 - tw(ns, B, 10) / 2, y: yy - rowH / 2 - 3.5, size: 10, font: B, color: t.num === '' ? C.t : C.white });
      const pg = 'p. ' + t.page, pw = tw(pg, B, 10.5);
      p.drawText(clean(t.title), { x: M + 44, y: yy - 15, size: 11.5, font: B, color: C.ink });
      let ab = clean(COURT[t.title] || t.about || '');
      const maxW = CW - 44 - pw - 24;
      while (ab && tw(ab, F, 8.8) > maxW) ab = ab.replace(/\s+\S+$/, '') + (ab.endsWith('…') ? '' : '…');
      if (ab) p.drawText(ab, { x: M + 44, y: yy - 28, size: 8.8, font: F, color: C.muet });
      p.drawText(pg, { x: W - M - pw, y: yy - rowH / 2 - 3.5, size: 10.5, font: B, color: C.t });
      goTo(t.page, M, yy - rowH + 2, CW, rowH - 4);
      yy -= rowH;
    }
    p.drawLine({ start: { x: M, y: yy }, end: { x: W - M, y: yy }, thickness: 0.5, color: C.ligne });
"""
s = s[:a] + NEW + s[b:]
old = "p.drawText(clean('Astuce : cliquez sur un titre ou une sous-partie pour y accéder directement.'), { x: M, y: 56, size: 8, font: F, color: C.muet });"
if s.count(old) != 1: sys.exit('astuce')
s = s.replace(old, "p.drawText(clean('Astuce : cliquez sur un chapitre pour y accéder directement.'), { x: M, y: 56, size: 8, font: F, color: C.muet });")
open(p, 'w', encoding='utf-8').write(s); print('patch toc appliqué')
