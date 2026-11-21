import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    for m in re.finditer(r".{0,60}(19,90|12,90|14,90|3,50 €|3,90 €|\b39 €|175 €|\b60 €|250 €|29,80|38,70|5 € le).{0,40}", l): print('%5d| %s' % (i + 1, m.group(0)))
sys.exit(1)
