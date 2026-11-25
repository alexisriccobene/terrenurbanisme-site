"""Foncier : référence BODACC courte (plus de lien qui déborde), accord « publiée »."""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "s.proc_url ? 'Annonce BODACC : ' + s.proc_url : ''"
b = "s.proc_url ? 'Annonce BODACC n° ' + ((String(s.proc_url).match(/id:([A-Z0-9]+)/) || [])[1] || '') + ', à consulter sur bodacc.fr' : ''"
if s.count(a) != 1: print('ANCRE url', s.count(a)); sys.exit(1)
s = s.replace(a, b)
if s.count("', publié le '") != 1: print('ANCRE publie', s.count("', publié le '")); sys.exit(1)
s = s.replace("', publié le '", "', publiée le '")
open(p, 'w', encoding='utf-8').write(s); print('ok lisible3')
