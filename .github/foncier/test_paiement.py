# Contrôle des offres de paiement (rapport synthétique, passage au complet) sans payer : création de sessions Stripe de test
import json, urllib.request
U = 'https://nmoigruxnhsidrhqtzid.supabase.co/functions/v1/create-checkout'
def call(body, tok=None):
    h = {'Content-Type': 'application/json', 'Origin': 'https://terrenurbanisme.com'}
    if tok: h['Authorization'] = 'Bearer ' + tok
    r = urllib.request.Request(U, json.dumps(body).encode(), h, method='POST')
    try:
        with urllib.request.urlopen(r, timeout=60) as x: return x.status, json.loads(x.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b'{}')
for nom, b in [('synthétique sur parcelle', {'kind': 'synth', 'insee': '2B251', 'section': 'AB', 'numero': '282', 'commune': 'Prunelli-di-Fiumorbo'}),
               ('synthétique sans parcelle (refus attendu)', {'kind': 'synth'}),
               ('passage au complet sans compte (refus attendu)', {'kind': 'upgrade', 'upgrade': 'x'}),
               ('rapport complet', {'kind': 'unit', 'insee': '2B251', 'section': 'AB', 'numero': '282', 'commune': 'Prunelli-di-Fiumorbo'})]:
    st, j = call(b)
    print(nom, '->', st, 'URL Stripe OK' if j.get('url', '').startswith('https://checkout.stripe.com') else j)
