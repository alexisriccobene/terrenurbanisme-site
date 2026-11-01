# Audit de couverture : pour chaque commune, type de document d'urbanisme et accessibilité du règlement écrit.
# Mode "dep" : toutes les communes des départements donnés ; mode "echantillon" : les N plus peuplées de chaque département.
import json, os, sys, time, urllib.request, urllib.parse, concurrent.futures as cf
CARTO = 'https://apicarto.ign.fr/api'
UA = {'User-Agent': 'TerrenUrbanisme-audit/1.0 (contact@terrenurbanisme.com)'}
def get(url, t=40, raw=False, method='GET', headers=None):
    for k in range(3):
        try:
            rq = urllib.request.Request(url, headers={**UA, **(headers or {})}, method=method)
            with urllib.request.urlopen(rq, timeout=t) as r:
                return (r.status, dict(r.headers)) if raw else json.loads(r.read())
        except urllib.error.HTTPError as e:
            if raw: return (e.code, dict(e.headers or {}))
            if e.code in (400, 404): return None
        except Exception:
            pass
        time.sleep(2 * (k + 1))
    return None
def pt(c): return urllib.parse.quote(json.dumps({'type': 'Point', 'coordinates': c}))
def audit(c):
    r = {'insee': c['code'], 'nom': c['nom'], 'dep': c.get('codeDepartement'), 'pop': c.get('population')}
    m = get(f"{CARTO}/gpu/municipality?insee={c['code']}") or {}
    mp = ((m.get('features') or [{}])[0] or {}).get('properties') or {}
    r['rnu'] = bool(mp.get('is_rnu'))
    ctr = (c.get('centre') or {}).get('coordinates')
    if not ctr: r['etat'] = 'sans_centre'; return r
    d = get(f"{CARTO}/gpu/document?geom={pt(ctr)}") or {}
    dp = next((f.get('properties') or {} for f in d.get('features') or [] if (f.get('properties') or {}).get('du_type')), {})
    r['du'] = dp.get('du_type') or ''
    if r['rnu']: r['etat'] = 'RNU'; return r
    if not r['du']: r['etat'] = 'aucun_document_publie'; return r
    if r['du'] == 'CC': r['etat'] = 'CC'; return r
    z = get(f"{CARTO}/gpu/zone-urba?geom={pt(ctr)}") or {}
    zp = ((z.get('features') or [{}])[0] or {}).get('properties') or {}
    r['zone'] = zp.get('libelle')
    nom = str(zp.get('nomfic') or '').split('#')[0]
    url = f"https://data.geopf.fr/annexes/gpu/documents/{zp.get('partition')}/{zp.get('gpu_doc_id')}/{nom}" if zp.get('gpu_doc_id') and nom else ''
    if not url and zp.get('urlfic', '').lower().split('?')[0].endswith('.pdf'): url = zp['urlfic']
    if not zp: r['etat'] = 'centre_hors_zonage'; return r
    if not url or not url.lower().endswith('.pdf'): r['etat'] = 'reglement_absent'; r['urlfic'] = zp.get('urlfic'); r['nomfic'] = zp.get('nomfic'); return r
    st, h = get(url, raw=True, method='HEAD') or (None, {})
    size = int({k.lower(): v for k, v in h.items()}.get('content-length') or 0)
    r['taille_mo'] = round(size / 1048576, 1)
    if st != 200: r['etat'] = f'reglement_http_{st}'
    elif size and size < 300000: r['etat'] = 'reglement_suspect_petit'
    elif size > 32 * 1048576: r['etat'] = 'reglement_lourd_github'
    else: r['etat'] = 'reglement_ok'
    return r
mode, deps, n = os.environ.get('MODE', 'dep'), os.environ.get('DEPS', '2A 2B').split(), int(os.environ.get('N', '3'))
communes = []
for dep in deps:
    l = get(f"https://geo.api.gouv.fr/departements/{dep}/communes?fields=nom,code,centre,population,codeDepartement") or []
    if mode == 'echantillon': l = sorted(l, key=lambda c: -(c.get('population') or 0))[:n]
    communes += l
print('communes', len(communes))
with cf.ThreadPoolExecutor(8) as ex: res = list(ex.map(audit, communes))
from collections import Counter
print(Counter(r.get('etat') for r in res))
json.dump(res, open('audit.json', 'w'), ensure_ascii=False)
