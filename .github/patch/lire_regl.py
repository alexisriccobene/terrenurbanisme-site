import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"19,90|12,90|14,90|3,50|39 €|175 €|390 €|250 €|par lot|abonnement", l) and i > 5300: print('%5d| %s' % (i + 1, l[:700]))
sys.exit(1)
