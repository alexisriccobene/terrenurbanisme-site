"""Télécharge les documents PLU de Corte repérés (zonage en vigueur, servitudes, comparaison)."""
import requests, os
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0'
for lid, nom in [(1741, 'zonage_1010.pdf'), (1739, 'reglement_plu.pdf'), (1743, 'servitudes_1.pdf'), (1744, 'servitudes_2.pdf'),
                 (1682, 'comparaison_01.jpeg'), (1683, 'comparaison_02.jpeg'), (1745, 'dci.pdf'), (1606, 'padd_2023.pdf')]:
    r = S.get('https://www.mairie-corte.fr/modules.php?name=Downloads&d_op=getit&lid=%d' % lid, timeout=300)
    open('/tmp/out/' + nom, 'wb').write(r.content); print(lid, nom, len(r.content))
