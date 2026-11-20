import sys, re
s = open(sys.argv[1], encoding='utf-8').read(); L = s.split('\n')
for i, l in enumerate(L):
    if re.search(r"claude-[a-z0-9-]+|api\.anthropic\.com|max_tokens|cache_control|anthropic-beta", l): print('%5d| %s' % (i + 1, l[:330]))
sys.exit(1)
