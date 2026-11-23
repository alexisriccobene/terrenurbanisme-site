import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if re.search(r"gpu_non_publie|sudocuh|non publi|nonPub|RNU en|isRnu|etat ===? ?'RNU'|DU_Opposable", l): print('%5d| %s' % (i + 1, l.strip()[:300]))
sys.exit(1)
