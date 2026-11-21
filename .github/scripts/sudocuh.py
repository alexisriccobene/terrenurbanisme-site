# Charge l'état officiel des documents d'urbanisme par commune (SuDocUH, ministère) dans sudocuh_commune
import json, os, re, sys, urllib.request, urllib.error
import openpyxl
URL = os.environ['SRC']
UA = {'User-Agent': 'TerrenUrbanisme/1.0 (contact@terrenurbanisme.com)'}
open('e.xlsx', 'wb').write(urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=300).read())
wb = openpyxl.load_workbook('e.xlsx', read_only=True, data_only=True)
def sql(q):
    rq = urllib.request.Request(f"https://api.supabase.com/v1/projects/{os.environ['REF']}/database/query", data=json.dumps({'query': q}).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + os.environ['SUPABASE_ACCESS_TOKEN'], 'Content-Type': 'application/json'})
    try: return urllib.request.urlopen(rq, timeout=120).status
    except urllib.error.HTTPError as e: print(e.code, e.read()[:400]); sys.exit(1)
for ws in wb.worksheets:
    if re.search(r'lisez|readme|notice', ws.title, re.I): continue
    rows = ws.iter_rows(values_only=True)
    head = None; n = 0; lot = []
    for r in rows:
        if head is None:
            cells = [str(c or '').strip() for c in r]
            if any(len(c) < 60 and re.search(r'insee|code ?com', c, re.I) for c in cells): head = cells; print('feuille', ws.title, 'colonnes', head)
            continue
        d = {head[i]: (str(v) if v is not None else None) for i, v in enumerate(r) if i < len(head) and head[i]}
        ic = next((k for k in d if re.search(r'insee|code ?com', k, re.I)), None)
        if not ic or not d.get(ic): continue
        insee = d[ic].strip().zfill(5)
        nom = next((d[k] for k in d if re.search(r'^(nom|libell)', k, re.I) and d[k]), '')
        dep = next((d[k] for k in d if re.search(r'^(dep|départ|code ?d)', k, re.I) and d[k]), insee[:2])
        etat = next((d[k] for k in d if re.search(r'(etat|état|type).*(opposable|du)|opposable', k, re.I) and d[k]), '')
        if n < 3 or insee.startswith('2A') or insee.startswith('2B'):
            if insee in ('2B096', '2B143', '2A006', '2B148'): print(insee, d)
        lot.append((insee, nom, dep, etat, d)); n += 1
        if len(lot) == 1500:
            vals = ','.join("(%s,%s,%s,%s,%s::jsonb,'sudocuh')" % tuple("$q$%s$q$" % str(x).replace('$q$', '') for x in (a, b, c, e, json.dumps(f, ensure_ascii=False))) for a, b, c, e, f in lot)
            sql('insert into public.sudocuh_commune (insee,nom,dep,etat,data,source) values ' + vals + ' on conflict (insee) do update set nom=excluded.nom, dep=excluded.dep, etat=excluded.etat, data=excluded.data, charge_le=now()')
            lot = []
    if lot:
        vals = ','.join("(%s,%s,%s,%s,%s::jsonb,'sudocuh')" % tuple("$q$%s$q$" % str(x).replace('$q$', '') for x in (a, b, c, e, json.dumps(f, ensure_ascii=False))) for a, b, c, e, f in lot)
        sql('insert into public.sudocuh_commune (insee,nom,dep,etat,data,source) values ' + vals + ' on conflict (insee) do update set nom=excluded.nom, dep=excluded.dep, etat=excluded.etat, data=excluded.data, charge_le=now()')
    print('feuille', ws.title, 'lignes', n)
    if n > 100: break
