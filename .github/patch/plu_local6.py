# Enchaîne : extrait du plan officiel + découpage des copies (plu_local5), puis verdict qui suit le zonage du PLU (verdict_plu)
import sys, os, runpy
d = os.path.dirname(os.path.abspath(__file__))
runpy.run_path(os.path.join(d, 'plu_local5.py'), run_name='__main__')
runpy.run_path(os.path.join(d, 'verdict_plu.py'), run_name='__main__')
