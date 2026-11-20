import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
print('LIGNES', len(L))
for i, l in enumerate(L):
    if re.search(r"^async function (sendMail|smtp|mail|envoyer)|^function (sendMail|cors|jres)|url\.searchParams\.get\('action'\)|action === '|Deno\.serve|req\.method === 'OPTIONS'|^const (CORS|ALLOW)", l):
        print('%5d| %s' % (i + 1, l[:260]))
def ctx(p, a=0, n=20):
    for i, l in enumerate(L):
        if re.search(p, l):
            print('==== %s @%d' % (p, i + 1))
            for j in range(max(0, i - a), min(len(L), i + n)): print('%5d| %s' % (j + 1, L[j][:400]))
            return
ctx(r"^async function (sendMail|smtp|envoyerMail)", 0, 25)
ctx(r"Deno\.serve", 0, 60)
sys.exit(1)
