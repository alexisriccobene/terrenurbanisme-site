# Version client : prix net vendeur saisi par l'agent repris tel quel dans le rapport
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("if (HP) { const net = Math.round(PC / (1 + HP / 100) / 100) * 100;",
    "if (HP) { const net = Number(String(RC.net || '').replace(/[^0-9]/g, '')) || Math.round(PC / (1 + HP / 100) / 100) * 100;")
rep("hono_charge: rc.hono_charge === 'acquereur' ? 'acquereur' : 'vendeur',", "hono_charge: rc.hono_charge === 'acquereur' ? 'acquereur' : 'vendeur', net: t(rc.net).replace(/[^0-9]/g, '').slice(0, 10), net_saisi: rc.net_saisi === true,")
open(p, 'w', encoding='utf-8').write(s); print('patch net vendeur appliqué')
