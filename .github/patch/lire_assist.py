import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"assistant|29,80|38,70|14,90|12,90|lot de 2|lot de 3", l): print('%5d| %s' % (i + 1, l.strip()[:600]))
sys.exit(1)
