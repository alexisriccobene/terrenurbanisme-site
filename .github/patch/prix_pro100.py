# Pack de 100 crédits professionnels : 390 € (3,90 € le rapport) au lieu de 450 €
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "pro100: { mode: 'payment', amount: 45000, credits: 100,"
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "pro100: { mode: 'payment', amount: 39000, credits: 100,")
s = s.replace("// TerrenUrbanisme · fonction « create-checkout » (v20)\n", "// TerrenUrbanisme · fonction « create-checkout » (v21)\n// v21 : 100 crédits professionnels à 390 € (3,90 € le rapport).\n", 1)
open(p, 'w', encoding='utf-8').write(s); print('prix pro100 = 390 €')
