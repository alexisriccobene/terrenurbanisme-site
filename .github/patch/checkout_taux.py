"""create-checkout : taux de la remise lu sur la remise (15 % de bienvenue, 20 % de relance)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("const { data: rm } = tk ? await admin.from('remises').select('token, utilise_le, expire_le').eq('token', tk).maybeSingle() : { data: null };",
    "const { data: rm } = tk ? await admin.from('remises').select('token, utilise_le, expire_le, taux').eq('token', tk).maybeSingle() : { data: null };")
rep("if (rm && !rm.utilise_le && new Date(rm.expire_le).getTime() > Date.now()) remise = rm.token;",
    "if (rm && !rm.utilise_le && new Date(rm.expire_le).getTime() > Date.now()) { remise = rm.token; taux = Math.min(30, Math.max(5, Number(rm.taux) || 15)); }")
rep("    let remise: string | null = null;", "    let remise: string | null = null, taux = 15;")
rep("const montant = remise ? Math.round(offer.amount * 0.85) : offer.amount;", "const montant = remise ? Math.round(offer.amount * (100 - taux) / 100) : offer.amount;")
rep("offer.name + (remise ? ' · remise de bienvenue −15 %' : '')", "offer.name + (remise ? (taux === 15 ? ' · remise de bienvenue −15 %' : ' · remise −' + taux + ' %') : '')")
open(p, 'w', encoding='utf-8').write(s); print('ok')
