"""Relance : mise en page mobile (pastille -20 % sans débordement, point d'interrogation insécable, texte aligné à gauche)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("Vous avez trouvé un terrain qui vous plaît ?</div>", "Vous avez trouvé un terrain qui vous plaît&nbsp;?</div>")
rep("width:150px;height:150px;border-radius:75px;background:#A3462C;color:#FFFFFF;font-size:52px;line-height:150px;", "width:150px;height:150px;border-radius:75px;background:#A3462C;color:#FFFFFF;font-size:42px;line-height:150px;")
rep("font-size:16px;line-height:1.6;color:#3A2E28;text-align:justify;' + x + '", "font-size:16px;line-height:1.6;color:#3A2E28;text-align:left;' + x + '")
open(p, 'w', encoding='utf-8').write(s); print('ok relance3')
