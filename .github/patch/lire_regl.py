import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"const muni\b|muni = |\.rnu\b|rnu:|const sb\b|createClient|from\('zonage_local'\)|zLocalF =|zLocalSrc =", l): print('%5d| %s' % (i + 1, l.strip()[:600]))
print('%5d| %s' % (1286, L[1285][:1500]))
sys.exit(1)
