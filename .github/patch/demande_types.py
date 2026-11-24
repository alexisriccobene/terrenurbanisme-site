# Formulaire public : types partenaire et intégration en plus de offre / démonstration
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a)); s = s.replace(a, b)
rep("const r = { type: b.type === 'demo' ? 'demo' : 'offre',", "const r = { type: ['demo', 'partenaire', 'integration'].includes(b.type) ? b.type : 'offre',")
rep("const lib = r.type === 'demo' ? 'Demande de démonstration' : 'Demande d\\'offre personnalisée';", "const lib = { demo: 'Demande de démonstration', partenaire: 'Candidature au programme partenaires', integration: 'Demande d\\'intégration', offre: 'Demande d\\'offre personnalisée' }[r.type];")
rep("['Volume estimé', r.volume]", "[r.type === 'partenaire' ? 'Audience' : 'Volume estimé', r.volume]")
open(p, 'w', encoding='utf-8').write(s); print('patch types appliqué')
