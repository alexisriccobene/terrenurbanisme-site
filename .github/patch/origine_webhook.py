"""Origine des ventes : enregistrée directement à chaque paiement reçu (réponse « Comment nous avez-vous connu ? », site d'origine, page d'arrivée, utm, code promo)."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "  let job = null;\n  if ((ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded') && o.metadata && o.metadata.remise"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
b = """  let job = null;
  if ((ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded') && o && o.status === 'complete') {
    try {
      const cf = Array.isArray(o.custom_fields) ? o.custom_fields : [], mo = o.metadata || {};
      const fo = cf.find((c: any) => c && c.key === 'origine'), fp = cf.find((c: any) => c && c.key === 'precision');
      const promo = (o.discounts || []).map((d: any) => d && (d.promotion_code || d.coupon)).filter(Boolean).join(',');
      await admin.from('ventes_origine').upsert({ session_id: o.id, paye_le: new Date((o.created || 0) * 1000).toISOString(), email: (o.customer_details && o.customer_details.email) || o.customer_email || null, montant: typeof o.amount_total === 'number' ? o.amount_total / 100 : null, offre: mo.kind || null, parcelle: mo.insee ? `${mo.commune || ''} ${mo.section || ''} ${mo.numero || ''}`.trim() : null, origine: (fo && fo.dropdown && fo.dropdown.value) || null, origine_detail: (fp && fp.text && fp.text.value) || null, referent: mo.src_ref || null, page_arrivee: mo.src_page || null, utm: mo.src_utm || null, code_promo: promo || null, maj_le: new Date().toISOString() }, { onConflict: 'session_id' }).then((x: any) => { if (x && x.error) console.error('ventes_origine', x.error); });
    } catch (e) { console.error('ventes_origine', e); }
  }
  if ((ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded') && o.metadata && o.metadata.remise"""
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok')
