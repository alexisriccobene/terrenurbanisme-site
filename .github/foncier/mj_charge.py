# Charge dans fon_mandataires les coordonnées relevées par mj_annuaire.py (fichier foncier/mj.json de la branche tests-rapports)
import json, re, unicodedata, os, subprocess, requests
subprocess.run(['git', 'fetch', '-q', '--depth=1', 'origin', 'tests-rapports:refs/remotes/origin/tests-rapports'], check=True)
raw = subprocess.run(['git', 'show', 'origin/tests-rapports:foncier/mj.json'], capture_output=True, text=True, check=True).stdout
L = json.loads(raw)
def norm(t): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFD', t).encode('ascii', 'ignore').decode().lower()).strip()
FORM = set('selarl sarl scp sas sasu selas selafa selasu etude etudes cabinet mj aj associes associe et de la le les du des d mandataires mandataire judiciaire judiciaires administrateurs administrateur societe office me maitre'.split())
TEL = re.compile(r'^(?:\+33\s?(?:\(0\)\s?)?|0)[1-9](?:[\s.-]?\d\d){4}$')
def ftel(t):
    d = re.sub(r'\D', '', t)[-9:]; return '0' + d if len(d) == 9 else ''
rows = []
for o in L:
    ls = [x.strip() for x in o['texte'].split('\n') if x.strip()]
    if 'Annuaire AJMJ' not in ls: continue
    i = ls.index('Annuaire AJMJ'); nom = ls[i + 1]; fonction = ls[i + 3] if i + 3 < len(ls) else ''
    if 'stagiaire' in fonction.lower() or 'judiciaire' not in fonction.lower(): continue
    etude = ls[ls.index('Étude') + 1] if 'Étude' in ls else ''
    adr = ''
    if 'Informations de contact' in ls:
        j = ls.index('Informations de contact') + 1
        if j < len(ls) and '@' not in ls[j] and not ls[j].startswith('http'): adr = ls[j]
    imps = []
    if 'Implantations' in ls:
        k = ls.index('Implantations') + 1; cur = None
        while k < len(ls) and not ls[k].startswith('Bannière'):
            x = ls[k]
            if '@' in x and cur is not None: cur['email'] = cur.get('email') or x
            elif TEL.match(x) and cur is not None: cur['tel'] = cur.get('tel') or ftel(x)
            elif x in ('T.', 'F.', 'Tél.'): pass
            elif not re.search(r'\d', x) and len(x) < 40: cur = {'ville': x.title()}; imps.append(cur)
            k += 1
    pn = norm(nom); parts = pn.split(); keys = {pn}
    if len(parts) >= 2: keys.add(' '.join(parts[1:] + parts[:1])); keys.add(parts[-1] + ' ' + parts[0])
    en = ' '.join(w for w in norm(etude).split() if w not in FORM)
    if len(en) >= 6: keys.add(en)
    rows.append({'nom': nom, 'fonction': fonction, 'etude': etude, 'adresse': adr, 'tel': ftel(o['tels'][0]) if o['tels'] else '',
                 'email': (o['mails'] or [''])[0], 'site': (o['sites'] or [''])[0], 'cles': sorted(k for k in keys if len(k) >= 6),
                 'implantations': [m for m in imps if m.get('tel') or m.get('email')], 'url': o['url']})
base = f"https://{os.environ['REF']}.supabase.co/rest/v1/fon_mandataires"
H = {'apikey': os.environ['SR'], 'Authorization': 'Bearer ' + os.environ['SR'], 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates,return=minimal'}
r = requests.post(base + '?on_conflict=url', headers=H, data=json.dumps(rows), timeout=120)
print('chargés', len(rows), r.status_code, r.text[:200])
