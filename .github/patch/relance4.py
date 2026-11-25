"""Relance : remise de 15 % (au lieu de 20 %), toujours valable 48 h."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
i = s.index("// ---------- Relance des inscrits sans achat"); j = s.index("async function remiseInscription(req: Request) {", i)
b = s[i:j]
n0 = b.count('20')
b = b.replace("&minus;20&nbsp;%", "&minus;15&nbsp;%").replace("-20 %", "-15 %").replace("de 20 %", "de 15 %").replace("taux: 20,", "taux: 15,").replace("relance20_", "relance15_").replace("Vos -20 % expirent", "Vos -15 % expirent").replace("(24 h après) : remise de 20 %", "(24 h après) : remise de 15 %")
left = [l for l in b.split('\n') if '20' in l and not any(x in l for x in ['2026', '320', '200', '20px', '20%', '120', 'padding:20', '0 20', '20 ', 'getFullYear'])]
for l in left: print('RESTE', l.strip()[:160])
s = s[:i] + b + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok relance4')
