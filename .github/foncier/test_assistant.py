"""Test de l'assistant du site : questions de prix et questions courantes."""
import requests, json
U = 'https://nmoigruxnhsidrhqtzid.supabase.co/functions/v1/stripe-webhook?assistant=1'
C = [
 [('user', 'prix pour 15 rapports'), ('assistant', 'Environ 45 pages : verdict, plan de zonage...'), ('user', 'je te demande le prix')],
 [('user', 'combien pour 5 rapports ?')],
 [('user', 'je suis agent immobilier, je fais environ 20 terrains par mois, quelle formule ?')],
 [('user', 'je ne connais pas le numéro de ma parcelle, comment faire ?')],
 [('user', 'combien coûte un rapport pour mon terrain à Sotta ?')],
 [('user', 'est-ce que vous remboursez si le rapport ne me convient pas ?')],
]
for c in C:
    r = requests.post(U, data=json.dumps({'page': '/', 'messages': [{'role': a, 'content': b} for a, b in c]}), headers={'Content-Type': 'text/plain;charset=UTF-8'}, timeout=60)
    print('Q:', c[-1][1]); print('R:', r.status_code, (r.json().get('reply') or r.text)[:900]); print()
