import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
print('LIGNES', len(L))
for i, l in enumerate(L):
    if re.search(r"deja_abonne|unit_amount|billing_address|meta\.pro|product_data\]\[name|customer_creation|^// v2", l): print('%5d| %s' % (i + 1, l[:260]))
sys.exit(1)
