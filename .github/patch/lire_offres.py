import sys
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i in range(0, 175): print('%5d| %s' % (i + 1, L[i][:240]))
for i, l in enumerate(L):
    if any(k in l for k in ('pro10','pro50','pro100','abo','synth','upgrade','mois','OFFERS[')) and i>=175: print('%5d| %s' % (i + 1, l[:240]))
sys.exit(1)
