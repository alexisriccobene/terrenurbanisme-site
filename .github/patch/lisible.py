"""Rapport plus lisible : enchaîne les correctifs lisible_a à lisible_d."""
import sys, subprocess, os
here = os.path.dirname(os.path.abspath(__file__))
for x in 'abcd':
    r = subprocess.run([sys.executable, os.path.join(here, 'lisible_' + x + '.py'), sys.argv[1]])
    if r.returncode: sys.exit(r.returncode)
print('ok lisible')
