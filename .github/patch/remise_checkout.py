# Paiement : remise de bienvenue de 15 % (lien reçu par e-mail) et e-mail du client sans compte saisi sur le site
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('ancre', a[:80], s.count(a))
    s = s.replace(a, b)
a = "error: 'deja_abonne'"
assert s.count(a) == 1, ('ancre deja_abonne', s.count(a))
k = s.index('\n', s.index('409);', s.index(a))) + 1
s = s[:k] + """    // Remise de bienvenue de 15 % : valable 14 jours, une seule fois, sur 1, 2 ou 3 rapports
    let remise: string | null = null;
    if (b.remise && /^(unit|pack2|pack3)$/.test(kind)) {
      const tk = String(b.remise).replace(/[^a-f0-9]/gi, '').slice(0, 64);
      const { data: rm } = tk ? await admin.from('remises').select('token, utilise_le, expire_le').eq('token', tk).maybeSingle() : { data: null };
      if (rm && !rm.utilise_le && new Date(rm.expire_le).getTime() > Date.now()) remise = rm.token;
    }
    const montant = remise ? Math.round(offer.amount * 0.85) : offer.amount;
""" + s[k:]
rep("""f.set('billing_address_collection', 'required');""", """f.set('billing_address_collection', 'required');
    if (!user && /^[^@\\s]+@[^@\\s]+\\.[a-z]{2,}$/i.test(String(b.email || '').trim())) f.set('customer_email', String(b.email).trim().slice(0, 120));""")
rep("""f.set('line_items[0][price_data][unit_amount]', String(offer.amount));""", """f.set('line_items[0][price_data][unit_amount]', String(montant));""")
rep("""f.set('line_items[0][price_data][product_data][name]', offer.name);""", """f.set('line_items[0][price_data][product_data][name]', offer.name + (remise ? ' · remise de bienvenue −15 %' : ''));""")
rep("""if (offer.pro) meta.pro = '1';""", """if (offer.pro) meta.pro = '1';
    if (remise) meta.remise = remise;""")
s = s.replace("// TerrenUrbanisme · fonction « create-checkout » (v21)\n", "// TerrenUrbanisme · fonction « create-checkout » (v22)\n// v22 : remise de bienvenue de 15 % (lien e-mail) et e-mail du client saisi sur le site.\n", 1)
open(p, 'w', encoding='utf-8').write(s); print('patch remise checkout appliqué')
