# Lot qualité : fibre préparée avant lecture + génération des rapports sur le serveur GitHub
import subprocess, sys
for f in ['fibre_attente.py', 'github_direct.py']:
    r = subprocess.run([sys.executable, '.github/patch/' + f, sys.argv[1]]); assert r.returncode == 0, f
