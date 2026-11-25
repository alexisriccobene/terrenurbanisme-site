"""Usages interdits : on retire les lignes qui répètent une règle déjà présentée dans le tableau (aspect, toitures…) ou une ligne précédente."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "    if (A.interdit_ou_conditionne && A.interdit_ou_conditionne.length) { h3(ZP('Usages interdits ou soumis à conditions')); A.interdit_ou_conditionne.forEach(t => bullet(t, { size: 9.5, color: C.non })); }"
if s.count(a) != 1: print('ANCRE', s.count(a)); sys.exit(1)
b = """    if (A.interdit_ou_conditionne && A.interdit_ou_conditionne.length) {
      const W = t => (String(t || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').match(/[a-z0-9]{4,}/g) || []).filter(x => !/^(interdit\\w*|conditionn\\w*|sauf|dans|pour|avec|sont|toute?s?|leurs?)$/.test(x));
      const regW = new Set(W(JSON.stringify(A.regles || [])));
      const seen = new Set(), IU = [];
      for (const t of A.interdit_ou_conditionne) {
        const w = W(t); if (!w.length) continue;
        const inReg = w.filter(x => regW.has(x)).length / w.length, inPrev = w.filter(x => seen.has(x)).length / w.length;
        if (inReg >= 0.8 || inPrev >= 0.8) continue;
        IU.push(t); w.forEach(x => seen.add(x));
      }
      if (IU.length) { h3(ZP('Usages interdits ou soumis à conditions')); IU.forEach(t => bullet(t, { size: 9.5, color: C.non })); }
    }"""
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok')
