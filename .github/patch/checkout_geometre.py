"""create-checkout : profil « geometre » accepté."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "if (/^(particulier|agent|notaire|moe)$/.test(pr)) parcel.profil = pr;"
assert s.count(a) == 1, 'ancre'
s = s.replace(a, "if (/^(particulier|agent|notaire|moe|geometre)$/.test(pr)) parcel.profil = pr;")
open(p, 'w', encoding='utf-8').write(s); print('ok')
