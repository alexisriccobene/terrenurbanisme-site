"""create-checkout : profil du demandeur (particulier, agent, notaire, moe) transmis au rapport par les métadonnées du paiement."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "      if (/^(maison|extension|piscine|annexe|division|achat)$/.test(pj)) parcel.projet = pj;\n"
assert s.count(old) == 1, 'ancre'
s = s.replace(old, old + "      // Profil du demandeur, choisi avant le paiement : la présentation du rapport s'adapte\n      const pr = String(b.profil || '');\n      if (/^(particulier|agent|notaire|moe)$/.test(pr)) parcel.profil = pr;\n")
open(p, 'w', encoding='utf-8').write(s); print('ok checkout')
