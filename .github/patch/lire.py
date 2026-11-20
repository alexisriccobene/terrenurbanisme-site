import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"amount\s*:\s*\d|unit_amount|Crédits professionnels|Abonnement Essentiel|ab50|pro100", l): print('%5d| %s' % (i + 1, l[:240]))
sys.exit(1)
