"""Lisibilité C : espèces protégées — en clair, que faire, impact sur le projet."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
start = "    h3('Espèces protégées observées près du terrain');"
endk = "    text('Sources : statuts de protection TAXREF"
i = s.find(start); j = s.find(endk, i); j = s.find('\n', j)
if i < 0 or j < 0 or s.count(start) != 1: print('ANCRE especes'); sys.exit(1)
new = r"""    h3('Espèces protégées observées près du terrain');
    if (!SP) text('Les bases d\'observations naturalistes n\'ont pas pu être consultées lors de l\'édition de ce rapport. En cas de doute (vieux arbres, murets, zone humide, maquis), faites passer un écologue avant les travaux.', { size: 9 });
    else if (!SP.liste.length) note('Aucune espèce protégée n\'a été signalée dans un rayon de ' + SP.rayon + ' km autour du terrain depuis 1990 (' + fmt(SP.obs) + ' observations naturalistes recensées dans ce rayon). Le risque de contrainte écologique est donc faible, sans être nul pour un secteur peu prospecté.', 'ok');
    else {
      const LS = SP.liste, oiseaux = LS.filter(x => x.groupe === 'Oiseau'), ex = oiseaux.filter(x => x.fr).slice(0, 2).map(x => x.fr.toLowerCase());
      note('En clair : ' + fmt(SP.nb) + ' espèce' + (SP.nb > 1 ? 's protégées ont' : ' protégée a') + ' été observée' + (SP.nb > 1 ? 's' : '') + ' à moins de ' + SP.rayon + ' km depuis 1990. ' + (oiseaux.length >= LS.length * 0.6 ? 'La plupart sont des oiseaux, protégés partout en France même lorsqu\'ils sont communs' + (ex.length ? ' (' + ex.join(', ') + ')' : '') + '. ' : '') + 'Cette présence autour du terrain est normale : elle ne bloque pas, à elle seule, un projet de maison.', 'info');
      h4('Les espèces les plus souvent observées');
      table([{ label: 'ESPÈCE', w: 0.56, bold: true }, { label: 'GROUPE', w: 0.18 }, { label: 'DERNIÈRE OBSERVATION', w: 0.26 }], LS.slice(0, 8).map(x => [x.fr ? x.fr + ' (' + x.sci + ')' : x.sci, x.groupe, x.der ? String(x.der) : '–']), { size: 8.5 });
    }
    h4('Concrètement, que faire ?');
    bullet('1. Regardez le terrain. Les espèces protégées vivent surtout dans les vieux arbres creux, les murets de pierres sèches, les mares et zones humides, le maquis dense ou les friches anciennes. Sur une parcelle entretenue ou entourée de maisons, le risque est faible.', { size: 9 });
    bullet('2. En cas de doute, faites passer un écologue : vous n\'avez pas à surveiller le terrain vous-même. Une visite, de préférence au printemps, suffit pour dire si une espèce protégée y vit (pré-diagnostic : 800 à 2 000 €).', { size: 9 });
    bullet('3. Dans tous les cas, coupez les arbres et les haies et débroussaillez en dehors de la période de nidification, de mars à août : c\'est la précaution la plus simple pour rester dans la loi.', { size: 9 });
    h4('Et si une espèce vit sur le terrain ?');
    text('Cela bloque rarement un projet. L\'écologue propose d\'adapter : placer la maison sur la partie la moins sensible, garder un arbre ou un muret, faire les travaux hors saison de reproduction (inventaire : 3 000 à 10 000 € ; mesures : 500 à 5 000 €). Ce n\'est que si la destruction de l\'habitat ne peut pas être évitée qu\'une dérogation est demandée à la préfecture : 4 à 12 mois d\'instruction et 8 000 à 25 000 € d\'études.', { size: 9.5 });
    text('Rappel : détruire ou déranger une espèce protégée, ou son lieu de reproduction, est puni de 3 ans d\'emprisonnement et 150 000 € d\'amende (articles L. 411-1 et L. 415-3 du Code de l\'environnement). Sources : statuts de protection TAXREF (INPN, Muséum national d\'Histoire naturelle) ; observations GBIF, qui rassemble les données de l\'INPN et du SINP.', { size: 8, color: C.muet });"""
s = s[:i] + new + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok C')
