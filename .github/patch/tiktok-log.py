# Console TikTok : journalise le refus de TikTok (code, options de confidentialité du compte) pour diagnostic
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = 'if (!init.ok)'
if s.count(a) != 1: sys.exit('ancre introuvable')
s = s.replace(a, "if (!init.ok) console.error('init', JSON.stringify({ err: init.j.error, options: cr.privacy_level_options, user: cr.creator_username, priv }));\n      " + a, 1)
open(p, 'w', encoding='utf-8').write(s); print('ok')
