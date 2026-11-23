import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = '5 € le rapport dès 50 crédits'
assert s.count(a) == 1, s.count(a)
s = s.replace(a, '11,90 € le rapport dès 30 crédits')
open(p, 'w', encoding='utf-8').write(s); print('ok')
