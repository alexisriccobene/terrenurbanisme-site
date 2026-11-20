# Vocabulaire des rapports et e-mails clients : « sans frais » et « mis à disposition » à la place de « gratuit » et « offert »
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
R = [("Gratuit, il indique", "Délivré sans frais, il indique"), (": gratuit, il précise", ": délivré sans frais, il précise"), ("peut être édité gratuitement, à tout moment", "peut être édité sans frais, à tout moment"),
     ("peut aussi être édité gratuitement sur", "peut aussi être édité sans frais sur"), ("Cerfa 13410, gratuit)", "Cerfa 13410, délivré sans frais)"), ("plan de situation (gratuit)", "plan de situation (sans frais)"),
     ("Contact gratuit et sans engagement", "Contact sans frais et sans engagement"), ("Rapport <strong>offert par ${d.offert}</strong>.", "Rapport <strong>mis à disposition par ${d.offert}</strong>.")]
for a, b in R:
    assert s.count(a) == 1, (a, s.count(a)); s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('patch vocabulaire appliqué')
