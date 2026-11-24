"""Servitudes : libellé lisible (sans code en tête, sans identifiant technique, sans dernier mot tronqué par la source)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "label: String(p.nomass || p.nomreg || '').replace(/_/g, ' ') };"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
b = "label: String(p.nomass || p.nomreg || '').replace(/_/g, ' ').replace(/^\\s*[A-Za-z]{1,3}\\d{1,2}\\s+/, '').replace(/[-\\s]*\\b[A-Z]{4,}\\d+[A-Z0-9]*\\b/g, ' ').replace(/(\\w)-(?=\\w)/g, '$1 ').replace(/\\s+(abor|abo|ass|asse|zon|zo|peri|péri|prot|pro)\\.?\\s*$/i, '').replace(/\\s{2,}/g, ' ').replace(/[\\s\\-–,;:]+$/, '').trim() };"
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok')
