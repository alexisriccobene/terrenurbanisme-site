# Communes sans document sur le Géoportail : état officiel SuDocUH (ministère) pour dire précisément quel document s'applique
# (RNU traité comme tel ; PLU ou carte communale nommés avec leur date d'approbation)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:80], s.count(a))
    s = s.replace(a, b)
rep("let zLocalF = null, zLocalSrc = '';",
    "let zLocalF = null, zLocalSrc = '';\n  let SDU = null;\n  try { const { data: sdr } = await admin.from('sudocuh_commune').select('data').eq('insee', INS).maybeSingle(); SDU = (sdr && sdr.data) || null; } catch (e) { console.warn('sudocuh', String(e && e.message || e).slice(0, 120)); }")
rep("(muni.is_rnu ? 'RNU' : (cc.length ? 'CC'",
    "((muni.is_rnu || (!zones.length && !zLocalF && SDU && SDU.DU_Opposable === 'RNU')) ? 'RNU' : (cc.length ? 'CC'")
rep("rnu: !!muni.is_rnu, name:",
    "rnu: !!muni.is_rnu || (!zones.length && !zLocalF && !cc.length && !!SDU && SDU.DU_Opposable === 'RNU'), sduLib: (!zones.length && !zLocalF && !cc.length && SDU && /^(PLU|PLUI|PLUIS|CC|POS)$/i.test(String(SDU.DU_Opposable || ''))) ? (({ PLU: 'un plan local d\\'urbanisme (PLU)', PLUI: 'un plan local d\\'urbanisme intercommunal (PLUi)', PLUIS: 'un plan local d\\'urbanisme intercommunal (PLUi)', CC: 'une carte communale', POS: 'un plan d\\'occupation des sols' })[String(SDU.DU_Opposable).toUpperCase()] + (/^\\d{4}-\\d{2}-\\d{2}/.test(String(SDU['Approbation DU en vigueur'] || '')) ? (String(SDU.DU_Opposable).toUpperCase() === 'CC' ? ' approuvée le ' : ' approuvé le ') + String(SDU['Approbation DU en vigueur']).slice(0, 10).split('-').reverse().join('/') : '') + (/r[ée]vision|[ée]laboration/i.test(String(SDU['Etat Commune'] || '')) ? ', actuellement en cours de révision' : '')) : '', name:")
rep("'La commune dispose d\\'un document d\\'urbanisme, mais ne l\\'a pas encore mis en ligne sur",
    "(d.doc.sduLib ? 'La commune dispose d\\'' + d.doc.sduLib + ' (source : enquête nationale SuDocUH du ministère chargé de l\\'urbanisme), mais ne l\\'a pas encore mis en ligne sur' : 'La commune dispose d\\'un document d\\'urbanisme, mais ne l\\'a pas encore mis en ligne sur') + '")
rep("note('La commune n\\'a pas publié son document d\\'urbanisme sur le Géoportail de l\\'Urbanisme.",
    "note((d.doc.sduLib ? 'Document en vigueur : ' + d.doc.sduLib + ' (source : enquête nationale SuDocUH du ministère chargé de l\\'urbanisme). ' : '') + 'La commune n\\'a pas publié son document d\\'urbanisme sur le Géoportail de l\\'Urbanisme.")
open(p, 'w', encoding='utf-8').write(s); print('patch sudocuh_doc appliqué')
