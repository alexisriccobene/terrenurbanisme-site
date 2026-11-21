# Prospection directe : 8 modèles, copie dans « Envoyés » (IMAP), liens vidéo
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
CODE = open(__file__.replace('prospection2.py', 'prospection_code.js'), encoding='utf-8').read()
a = s.index('// Modèles des e-mails de prospection TerrenUrbanisme'); b = s.index('\nasync function villeCfg(slug) {')
s = s[:a] + CODE + s[b:]
i0 = s.index('async function smtpSimple(toList, subject, text, html, xh) {'); i1 = s.index('    await conn.write(enc.encode(msg));', i0)
s = s[:i1] + '    globalThis.__dernierMail = msg;\n' + s[i1:]
open(p, 'w', encoding='utf-8').write(s); print('patch prospection 2 appliqué')
