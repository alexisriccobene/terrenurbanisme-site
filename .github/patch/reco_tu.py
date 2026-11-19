# Recommandation de l'agence : notre fourchette (analyse TerrenUrbanisme) puis le prix conseillé par l'agence
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("  if (!AGRI) try {\n    const VS = (() => {", "  let VS_TU = null; // fourchette TerrenUrbanisme, rappelée dans la recommandation de l'agence\n  if (!AGRI) try {\n    const VS = (() => {")
rep("      const S = VS.surf, lo = S * VS.p25, mid = S * VS.p50, hi = S * VS.p75;\n", "      const S = VS.surf, lo = S * VS.p25, mid = S * VS.p50, hi = S * VS.p75;\n      VS_TU = { lo, mid, hi, n: VS.nCur, pa: VS.p25, pb: VS.p75, surf: S };\n")
rep("""    'Recommandation de l\\'agence': 'L\\'avis de valeur de votre conseiller : son prix recommandé, son commentaire et les photos du bien.'""",
    """    'Recommandation de l\\'agence': 'Deux regards sur le prix : la fourchette établie par TerrenUrbanisme à partir des ventes réelles, puis le prix recommandé par votre conseiller, son commentaire et les photos du bien.'""")
rep("""      'Recommandation de l\\'agence': 'Le prix recommandé par votre conseiller, son commentaire et les photos du bien.',""",
    """      'Recommandation de l\\'agence': 'Notre fourchette de prix, le prix recommandé par votre conseiller et les photos du bien.',""")
old_start = "    const cons = eurs(RC.conseille), bas = eurs(RC.bas), haut = eurs(RC.haut);\n    if (cons || bas || haut) {"
i = s.index(old_start); j = s.index("    if (RC.commentaire) { h3('Le mot de votre conseiller');", i)
new = """    const cons = eurs(RC.conseille), bas = eurs(RC.bas), haut = eurs(RC.haut);
    const boxV = (lab, big, sub, right, col) => {
      ensure(86);
      page.drawRectangle({ x: M, y: y - 74, width: CW, height: 74, color: col });
      page.drawRectangle({ x: M, y: y - 74, width: 4, height: 74, color: C.t });
      page.drawText(clean(lab), { x: M + 20, y: y - 22, size: 8.5, font: B, color: C.t });
      page.drawText(clean(big), { x: M + 20, y: y - 50, size: 24, font: B, color: C.ink });
      if (sub) page.drawText(clean(sub), { x: M + 20, y: y - 66, size: 8.5, font: F, color: C.muet });
      if (right) page.drawText(clean(right), { x: W - M - 20 - tw(clean(right), Md, 10.5), y: y - 48, size: 10.5, font: Md, color: C.muet });
      y -= 86;
    };
    const TYPB = { terrain: 'Terrain', maison: 'Maison', appartement: 'Appartement', autre: 'Autre bien' }[String(RC.type || '')] || '';
    if (TYPB || RC.designation) {
      h3('Désignation du bien');
      if (TYPB) kv([['Type de bien', TYPB]], { lw: 0.3 });
      if (RC.designation) String(RC.designation).split(/\n+/).filter(Boolean).forEach(par => text(par, { size: 10 }));
    }
    if (VS_TU || cons || bas || haut) {
      if (VS_TU) {
        h3('1. L\\'analyse TerrenUrbanisme');
        boxV('FOURCHETTE ÉTABLIE PAR TERRENURBANISME', eurK(VS_TU.lo) + ' à ' + eurK(VS_TU.hi), 'Valeur centrale ' + eurK(VS_TU.mid) + ' · ' + VS_TU.n + ' ventes réelles de terrains relevées autour de la parcelle (DVF)', '', C.soft2);
        text('Calcul automatique à partir des ventes publiées par la DGFiP, ajusté à la surface de la parcelle (' + fmt(VS_TU.surf) + ' m²). Il ne tient pas compte de la vue, de la viabilisation ni de l\\'état du terrain.', { size: 9, color: C.muet });
      }
      if (cons || bas || haut) {
        h3((VS_TU ? '2. ' : '') + 'La recommandation de votre agence');
        if (cons) boxV('PRIX RECOMMANDÉ PAR L\\'AGENCE', cons, (MQ && MQ.nom ? MQ.nom : 'Votre conseiller') + ', d\\'après sa connaissance du marché local et la visite du bien', bas && haut ? 'Fourchette : ' + bas + ' à ' + haut : '', C.cream);
        else boxV('FOURCHETTE RECOMMANDÉE PAR L\\'AGENCE', [bas, haut].filter(Boolean).join(' à '), (MQ && MQ.nom ? MQ.nom : 'Votre conseiller') + ', d\\'après sa connaissance du marché local et la visite du bien', '', C.cream);
        text('L\\'agence affine l\\'analyse des ventes avec ce que les chiffres ne voient pas : la vue, l\\'exposition, l\\'accès, la viabilisation, la demande actuelle et l\\'état du bien.', { size: 9, color: C.muet });
      }
    }
"""
s = s[:i] + new + s[j:]
rep("if (PERSO && PERSO.reco && (PERSO.reco.conseille || PERSO.reco.bas || PERSO.reco.haut || PERSO.reco.commentaire ||", "if (PERSO && PERSO.reco && (PERSO.reco.conseille || PERSO.reco.bas || PERSO.reco.haut || PERSO.reco.commentaire || PERSO.reco.designation || PERSO.reco.type ||")
rep("reco: { bas: t(rc.bas).slice(0, 20),", "reco: { type: /^(terrain|maison|appartement|autre)$/.test(t(rc.type)) ? t(rc.type) : '', designation: t(rc.designation).slice(0, 1200), bas: t(rc.bas).slice(0, 20),")
open(p, 'w', encoding='utf-8').write(s); print('patch reco appliqué')
