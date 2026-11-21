import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"amount|OFFERS|offers|recurring|interval|credits|pro10|pro50|pro100|unit|pack2|pack3|abo", l): print('%5d| %s' % (i + 1, l[:220]))
sys.exit(1)
