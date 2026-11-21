import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"checkout\.session\.completed|const meta = |session\.metadata|async function smtpSimple|function escH|function jres", l): print('%5d| %s' % (i + 1, l[:300]))
sys.exit(1)
