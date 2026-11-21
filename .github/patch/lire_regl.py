import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
print('LIGNES', len(L))
for i, l in enumerate(L):
    if re.search(r"reglement|règlement|urlfic|zonage_local|REGL_|regl_override|_reglement|documents/|annexes/gpu|diffuweb", l, re.I): print('%5d| %s' % (i + 1, l[:230]))
sys.exit(1)
