# Étude géotechnique préalable (art. L. 132-5 CCH) : seulement si la zone permet la réalisation de maisons individuelles.
# Exclusion légale : terrains situés dans des secteurs dont les règles d'urbanisme ne permettent pas les maisons individuelles
# (zones d'activités, zones A/N, zones où le logement n'est admis que s'il est lié à l'activité). Remarque d'un notaire, 21/11/2026.
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = """    if (/mod[ée]r|moyen|fort|important/i.test(rgaT)) ex.push({ key: 'cond', text: 'Retrait-gonflement des argiles (exposition ' + (/fort|important/i.test(rgaT) ? 'forte' : 'moyenne') + ') : en cas de vente d\\'un terrain non bâti constructible, le vendeur doit fournir une étude géotechnique préalable (loi ELAN, article L. 132-5 du Code de la construction et de l\\'habitation) ; une étude géotechnique de conception est exigée avant de construire.' });"""
assert s.count(a) == 1, s.count(a)
b = """    if (/mod[ée]r|moyen|fort|important/i.test(rgaT)) {
      const expo = /fort|important/i.test(rgaT) ? 'forte' : 'moyenne', Z0g = (d.zones && d.zones[0]) || {};
      const libZ = [Z0g.code, Z0g.longLabel, Z0g.typeLabel, Z0g.explain].join(' ');
      const activite = /activit|[ée]conomi|industri|artisan|commerci|tertiaire|portuaire|a[ée]roport|zone d.[ée]quipement|gardiennage|li[ée]e?s? [àa] l.activit/i.test(libZ) || /^(1|2)?AU?[XYZIE]|^U[XYZIE]|^UAE|^UEA?|^AUE/i.test(String(Z0g.code || ''));
      const sansMaison = d.verdict.key === 'non' || K0.neuf === false || K0.logement === false || Z0g.v === 'non';
      if (sansMaison || activite) ex.push({ key: 'info', text: 'Retrait-gonflement des argiles (exposition ' + expo + ') : l\\'étude géotechnique préalable à la vente (article L. 132-5 du Code de la construction et de l\\'habitation) n\\'est exigée que dans les secteurs où les règles d\\'urbanisme permettent la réalisation de maisons individuelles. ' + (activite && !sansMaison ? 'La zone ' + nz0 + ' est réservée aux activités : si le logement n\\'y est admis que lié à l\\'activité (gardiennage, direction), l\\'obligation ne s\\'applique en principe pas.' : 'La zone ' + nz0 + ' ne permettant pas de maison individuelle, cette obligation ne s\\'applique pas à la vente.') + ' Une étude géotechnique de conception reste nécessaire avant tout projet de construction.' });
      else ex.push({ key: 'cond', text: 'Retrait-gonflement des argiles (exposition ' + expo + ') : la zone ' + nz0 + ' permettant la réalisation de maisons individuelles, le vendeur d\\'un terrain non bâti constructible doit fournir une étude géotechnique préalable, annexée à la promesse de vente ou, à défaut, à l\\'acte authentique (article L. 132-5 du Code de la construction et de l\\'habitation) ; une étude géotechnique de conception est exigée avant de construire.' });
    }"""
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('patch geotechnique appliqué')
