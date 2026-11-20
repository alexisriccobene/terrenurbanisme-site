import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"^(const|function) (jres|escH)\b|^const jres|^function escH|const escH", l): print('%5d| %s' % (i + 1, l[:300]))
for i in range(4198, 4206): print('%5d| %s' % (i + 1, L[i][:300]))
sys.exit(1)
