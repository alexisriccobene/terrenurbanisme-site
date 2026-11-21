import sys, re
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
print('lignes', len(L))
for i, l in enumerate(L):
    if re.search(r"aucun_document|aucun document|rnuInfo|isRnu|is_rnu|\brnu\b *[:=]|noDoc|sansDoc|function (gpuDoc|zonesFor|diagnostic|docInfo)|non publi", l): print('%5d| %s' % (i + 1, l.strip()[:230]))
sys.exit(1)
