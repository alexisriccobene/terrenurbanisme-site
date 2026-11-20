import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
def show(a, b):
    for i in range(a, b): print('%5d| %s' % (i + 1, L[i][:300]))
for i, l in enumerate(L):
    if re.search(r"^  function (ensure|bullet|h3|newPage|wrap|text)\(|^  const (ensure|bullet|wrap)\b", l): show(i, i + 8); print('----')
i = next(i for i, l in enumerate(L) if "// Points d'attention" in l and 'complémentaires' not in l)
show(i - 2, i + 40)
sys.exit(1)
