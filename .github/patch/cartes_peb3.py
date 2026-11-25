"""PEB : la couche DGAC ne répond qu'à partir d'une certaine échelle — fenêtre d'interrogation de 0,012° (pixel d'environ 13 m)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "const fb = [pt[1] - 0.0005, pt[0] - 0.0005, pt[1] + 0.0005, pt[0] + 0.0005];"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
s = s.replace(a, "const fb = [pt[1] - 0.006, pt[0] - 0.006, pt[1] + 0.006, pt[0] + 0.006];")
open(p, 'w', encoding='utf-8').write(s); print('ok peb3')
