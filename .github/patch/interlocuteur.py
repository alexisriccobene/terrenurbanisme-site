# Page de garde : « Votre interlocuteur » = le collaborateur qui remet le rapport (nom, téléphone, e-mail) + site de l'agence ; libellé des prix raccourci
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable (%d) : %s' % (s.count(old), old[:90]))
    s = s.replace(old, new)
rep("  const fitLogo = (mw, mh) => {", "  if (MQ && MQ.site) MQ.site = String(MQ.site).replace(/[?#].*$/, '').replace(/\\/$/, '');\n  const CSV0 = (d.perso && d.perso.conseiller) || d.conseiller || null;\n  const fitLogo = (mw, mh) => {")
rep("  const MQC = mqContacts(), cardH =", "  const MQC = (() => { if (!CSV0 || !MQ) return mqContacts(); const sv = { t: MQ.telephone, e: MQ.email }; MQ.telephone = CSV0.tel || MQ.telephone; MQ.email = CSV0.email || MQ.email; const r = mqContacts(); MQ.telephone = sv.t; MQ.email = sv.e; return r; })(), cardH =")
rep("    cover.drawText(clean(MQ.nom || 'Votre conseiller').slice(0, 60), { x: x + 20, y: top - 40, size: 14, font: B, color: C.ink });",
    "    cover.drawText(clean((CSV0 && CSV0.nom) || MQ.nom || 'Votre conseiller').slice(0, 60), { x: x + 20, y: top - 40, size: 14, font: B, color: C.ink });\n    if (CSV0 && CSV0.nom && MQ.nom) { const an = clean(MQ.nom).slice(0, 60); cover.drawText(an, { x: x + 20 + tw(clean(CSV0.nom).slice(0, 60), B, 14) + 10, y: top - 40, size: 10, font: F, color: C.muet }); }")
rep("const rows = [['Prix de présentation' + (HP ? ' (honoraires inclus)' : ''), fmt(PC) + ' €']];", "const rows = [['Prix de présentation', fmt(PC) + ' €' + (HP ? ', honoraires inclus' : '')]];")
# Rapport complet demandé par un collaborateur : même interlocuteur sur la page de garde
rep("  try { d.marque = meta.marque || await loadMarque(m.user_id); } catch (e) { console.warn('marque', String(e && e.message || e).slice(0, 160)); d.marque = null; }",
r"""  try { d.marque = meta.marque || await loadMarque(m.user_id); } catch (e) { console.warn('marque', String(e && e.message || e).slice(0, 160)); d.marque = null; }
  try {
    if (d.marque && meta.orderRef) {
      const { data: dz } = await admin.from('dossiers').select('agent, user_id').eq('order_ref', meta.orderRef).maybeSingle();
      if (dz && dz.agent) { const { data: ag } = await admin.from('pro_agents').select('nom, telephone, email').eq('user_id', dz.user_id).eq('nom', dz.agent).limit(1).maybeSingle(); if (ag) d.conseiller = { nom: ag.nom, tel: ag.telephone || '', email: ag.email || '' }; }
    }
  } catch (e) { console.warn('interlocuteur', String(e && e.message || e).slice(0, 120)); }""")
open(p, 'w', encoding='utf-8').write(s); print('patch interlocuteur appliqué')
