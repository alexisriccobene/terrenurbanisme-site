# Tableau « Document d'urbanisme » : type et statut issus de SuDocUH quand rien n'est publié au Géoportail
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:80], s.count(a))
    s = s.replace(a, b)
rep("typeLabel: DU[duType] || (duType || 'Non déterminé')",
    "typeLabel: DU[duType] || (duType || ((!zones.length && !zLocalF && !cc.length && SDU && /^(PLU|PLUI|PLUIS|CC|POS)$/i.test(String(SDU.DU_Opposable || ''))) ? ({ PLU: 'Plan local d\\'urbanisme (PLU)', PLUI: 'Plan local d\\'urbanisme intercommunal (PLUi)', PLUIS: 'Plan local d\\'urbanisme intercommunal (PLUi)', CC: 'Carte communale', POS: 'Plan d\\'occupation des sols' })[String(SDU.DU_Opposable).toUpperCase()] : 'Non déterminé'))")
rep("(zones.length ? 'Publié au Géoportail de l\\'Urbanisme' : ''), url:",
    "(zones.length ? 'Publié au Géoportail de l\\'Urbanisme' : ((!zLocalF && SDU && SDU.DU_Opposable && SDU.DU_Opposable !== 'RNU') ? 'En vigueur, non publié au Géoportail de l\\'Urbanisme' : '')), url:")
rep("date: zones[0] && zones[0].date ? zones[0].date : '',",
    "date: zones[0] && zones[0].date ? zones[0].date : ((!zones.length && !zLocalF && SDU && /^\\d{4}-\\d{2}-\\d{2}/.test(String(SDU['Approbation DU en vigueur'] || ''))) ? String(SDU['Approbation DU en vigueur']).slice(0, 10).replace(/-/g, '') : ''),")
open(p, 'w', encoding='utf-8').write(s); print('patch sudocuh_doc2 appliqué')
