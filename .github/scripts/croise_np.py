# Charge la liste des communes sans document au Géoportail (couverture-france.csv) dans gpu_non_publie
import csv, json, os, sys, urllib.request, urllib.error
def sql(q):
    rq = urllib.request.Request(f"https://api.supabase.com/v1/projects/{os.environ['REF']}/database/query", data=json.dumps({'query': q}).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + os.environ['SUPABASE_ACCESS_TOKEN'], 'Content-Type': 'application/json'})
    try: return urllib.request.urlopen(rq, timeout=120).read()
    except urllib.error.HTTPError as e: print(e.code, e.read()[:400]); sys.exit(1)
sql("create table if not exists public.gpu_non_publie (insee text primary key, nom text, dep text, etat text, pop int); alter table public.gpu_non_publie enable row level security; truncate public.gpu_non_publie;")
r = [x for x in csv.DictReader(open('.github/plu/couverture-france.csv')) if x['etat'] in ('non_publie', 'inconnu')]
q = lambda s: "'" + str(s).replace("'", "''") + "'"
for i in range(0, len(r), 1000):
    sql('insert into public.gpu_non_publie values ' + ','.join('(%s,%s,%s,%s,%d)' % (q(x['insee']), q(x['commune']), q(x['dep']), q(x['etat']), int(x['population'] or 0)) for x in r[i:i+1000]) + ' on conflict do nothing')
print(len(r), 'communes')
