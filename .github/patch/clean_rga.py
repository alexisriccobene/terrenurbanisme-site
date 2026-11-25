"""Texte : deux e-mails collés par « ; » séparés par une virgule partout. ERP : argiles « Non connu » = Non (aucune exposition recensée), plus de « Oui » contradictoire."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def one(a, b, label):
    global s
    n = s.count(a)
    if n != 1: print('ANCRE', label, n); sys.exit(1)
    s = s.replace(a, b)
one(".replace(/≥/g, '>=').replace(/\\s+/g, ' ').trim();\n    let out = '';", ".replace(/≥/g, '>=').replace(/\\s*;\\s*(?=[A-Za-z0-9._-]+@)/g, ', ').replace(/\\s+/g, ' ').trim();\n    let out = '';", 'clean')
one("RKe.rga && !/non concern/i.test(RKe.rga) ? 'Oui' : 'Non', RKe.rga || 'Non concerné']", "RKe.rga && !/non concern|non connu|inconnu|nulle/i.test(RKe.rga) ? 'Oui' : 'Non', RKe.rga && !/non connu|inconnu|nulle/i.test(RKe.rga) ? RKe.rga : 'Aucune exposition recensée par Géorisques']", 'rga')
open(p, 'w', encoding='utf-8').write(s); print('ok clean rga')
