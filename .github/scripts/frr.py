# Lecture de la liste ANCT des communes FRR : affiche la structure, puis construit {insee: [statut, nom]}.
import json, re, sys, collections
import openpyxl
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
out = {}
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True))
    print('=== feuille', ws.title, len(rows), 'lignes')
    for r in rows[:8]: print('  ', r)
    # repère la ligne d'en-tête : celle qui contient un libellé de code commune
    hi = next((i for i, r in enumerate(rows[:30]) if any(c and re.search(r'(code|codgeo|insee)', str(c), re.I) for c in r)), None)
    if hi is None: continue
    H = [str(c or '').strip() for c in rows[hi]]
    print('  en-tête :', H)
    ic = next(i for i, h in enumerate(H) if re.search(r'(codgeo|code.*(commune|insee)|insee|^code$)', h, re.I))
    inom = next((i for i, h in enumerate(H) if re.search(r'(libgeo|nom|libell)', h, re.I) and i != ic), None)
    cnt = collections.Counter()
    for k, h in enumerate(H):
        if k in (ic, inom): continue
        vals = collections.Counter(str(r[k]).strip() for r in rows[hi + 1:] if k < len(r) and r[k] is not None)
        print('  colonne', repr(h), dict(vals.most_common(8)))
    for r in rows[hi + 1:]:
        if ic >= len(r) or r[ic] is None: continue
        code = str(r[ic]).strip()
        if re.fullmatch(r'\d{4}', code): code = '0' + code
        if not re.fullmatch(r'\d[\dAB]\d{3}', code): continue
        out.setdefault(code, {})[ws.title] = {H[k]: (str(v).strip() if v is not None else '') for k, v in enumerate(r) if k != ic and k < len(H) and H[k]}
print('communes :', len(out))
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False)
for c in ['2A247', '2A272', '91200', '48095', '23096', '75056']:
    print(c, out.get(c))
