# Console TikTok : journalise le refus de TikTok (code, options de confidentialité du compte) pour diagnostic
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "if (!init.ok) return out({ error: init.j.error?.code || 'init', message: init.j.error?.message || '' }, 400);"
if s.count(old) != 1: sys.exit('ancre introuvable')
s = s.replace(old, "if (!init.ok) { console.error('init', JSON.stringify({ err: init.j.error, options: cr.privacy_level_options, user: cr.creator_username, priv })); return out({ error: init.j.error?.code || 'init', message: init.j.error?.message || '', options: cr.privacy_level_options || [] }, 400); }")
open(p, 'w', encoding='utf-8').write(s); print('ok')
