import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"^\s*(unit|pack2|pack3|pro10|pro50|pro100|pro250|pro500|ab10|ab50|abo\w*)\s*:\s*\{", l): print('%5d| %s' % (i + 1, l[:260]))
sys.exit(1)
