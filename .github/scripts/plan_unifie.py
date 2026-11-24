import json, collections, re, datetime as dt, copy
R='repo/.github/social/'
items=json.load(open(R+'plan.json',encoding='utf-8'))
pub=json.load(open(R+'publie.json',encoding='utf-8')); ptk=json.load(open(R+'publie_tiktok.json',encoding='utf-8'))
NOW='2026-11-20'; HEURE='18:00'
ALL=['instagram','facebook','linkedin','youtube','tiktok']
def key(e):
    if e.get('video'): return 'v:'+e['video']
    if e.get('images'): return 'i:'+e['images'][0]
    return 'x:'+e['id']
G=collections.OrderedDict()
for e in sorted(items,key=lambda x:x['date']):
    if e.get('type')=='story': continue
    g=G.setdefault(key(e),{'entries':[],'done':set()}); g['entries'].append(e)
    d={**pub.get(e['id'],{}),**ptk.get(e['id'],{})}
    for n in ALL:
        if d.get(n): g['done'].add(n)
    if e['date']<NOW:
        for n in e.get('reseaux',[]): g['done'].add(n)
fut=[(k,g) for k,g in G.items() if any(e['date']>=NOW and e.get('reseaux') for e in g['entries'])]
SEAS=re.compile(r"\bprintemps\b|\bcet été\b|avant l'été|pour l'été|\bl'été\b|\brentrée\b|\bno[eë]l\b|nouvel an|fin d'année|\bvacances\b|\bhiver\b|\bautomne\b|résolutions|^2027 ",re.I)
CTA_IG="Analysez votre terrain : terrenurbanisme.com (lien en bio)"
CTA_URL="Analysez votre terrain : https://terrenurbanisme.com"
def has_cta(t): return 'terrenurbanisme.com' in t or 'lien en bio' in t
def with_cta(t,cta):
    t=t.strip()
    if has_cta(t): return t
    lines=t.split('\n'); tags=[]
    while lines and lines[-1].strip().startswith('#'): tags.insert(0,lines.pop())
    return ('\n'.join(lines).rstrip()+'\n\n'+cta+('\n\n'+'\n'.join(tags) if tags else '')).strip()
def li_to_ig(t): return with_cta(re.sub(r'\n?https://terrenurbanisme\.com\n?','\n'+CTA_IG+'\n',t).replace('\n\n\n','\n\n'),CTA_IG)
contents=[]
for k,g in fut:
    E=g['entries']; f=lambda fld: next((e[fld] for e in E if e.get(fld)),None)
    first=min(e['date'] for e in E if e['date']>=NOW and e.get('reseaux'))
    c={'key':k,'orig':first,'theme':f('theme'),'need':[n for n in ALL if n not in g['done']],'old_ids':[e['id'] for e in E if e['date']>=NOW]}
    if k[0]=='v': c.update(type='reel',video=f('video')); 
    if f('video_tiktok'): c['video_tiktok']=f('video_tiktok')
    if k[0]=='i': c['images']=f('images')
    ig=f('texte_instagram'); li=f('texte_linkedin'); fb=f('texte_facebook')
    c['texte_linkedin']=with_cta(li or fb or ig,CTA_URL)
    c['texte_instagram']=with_cta(ig,CTA_IG) if ig else li_to_ig(li)
    c['texte_facebook']=with_cta(fb or ig or li,CTA_URL).replace('(lien en bio)','').replace('lien en bio','https://terrenurbanisme.com')
    c['texte_tiktok']=with_cta(f('texte_tiktok') or c['texte_instagram'],CTA_IG)[:2200]
    c['titre_youtube']=f('titre_youtube') or (c['theme'][:91].rstrip()+' #Shorts')
    c['texte_youtube']=with_cta(f('texte_youtube') or c['texte_facebook'],CTA_URL)[:4900]
    c['saison']=bool(SEAS.search((c['theme'] or '')+' '+c['texte_instagram'][:250]))
    contents.append(c)
# placement : saisonniers à leur date, puis le reste dans l'ordre d'origine sur les jours libres
day0=dt.date.fromisoformat(NOW); used={}
for c in sorted([c for c in contents if c['saison']],key=lambda c:c['orig']):
    d=dt.date.fromisoformat(c['orig'][:10])
    while d in used: d+=dt.timedelta(1)
    used[d]=c
rest=sorted([c for c in contents if not c['saison']],key=lambda c:c['orig']); d=day0
for c in rest:
    while d in used: d+=dt.timedelta(1)
    used[d]=c
last=max(used)
gaps=[str(day0+dt.timedelta(i)) for i in range((last-day0).days+1) if day0+dt.timedelta(i) not in used]
new=[e for e in items if e['date']<NOW or e.get('type')=='story']
for d,c in sorted(used.items()):
    e={'id':'j-'+str(d),'date':'%sT%s'%(d,HEURE),'theme':c['theme'],'reseaux':c['need'],'origine':c['old_ids']}
    for fld in ('type','video','video_tiktok','images','texte_instagram','texte_facebook','texte_linkedin','texte_tiktok','titre_youtube','texte_youtube'):
        if c.get(fld): e[fld]=c[fld]
    new.append(e)
# stories : une par jour jusqu'au dernier jour de publication, en reprenant des stories déjà vérifiées
st=sorted([e for e in items if e.get('type')=='story' and e['date']>=NOW and e.get('reseaux')],key=lambda e:e['date'])
sd={e['date'][:10] for e in st}; lastst=dt.date.fromisoformat(max(sd))
ocr={l.split(' | ')[1]:l.split(' | ',2)[2] for l in open('ocr/all.txt',encoding='utf-8') if ' | ' in l}
pool=[e for e in st if e['id'] in ocr and not SEAS.search(ocr[e['id']]) and not re.search(r'été|rentrée|printemps|lot de|dès|€',ocr[e['id']],re.I)]
i=0; d=dt.date.fromisoformat(NOW); add=[]
while d<=last:
    if str(d) not in sd:
        s=copy.deepcopy(pool[i%len(pool)]); i+=1; s['id']='story-r-'+str(d); s['date']='%sT12:30'%d; s['reprise_de']=pool[(i-1)%len(pool)]['id']; add.append(s)
    d+=dt.timedelta(1)
new+=add; new.sort(key=lambda e:e['date'])
json.dump(new,open('plan_propose.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('contenus',len(contents),'dernier jour',last,'trous',gaps[:10],len(gaps),'saisonniers',sum(c['saison'] for c in contents))
print('stories ajoutées',len(add),'(pool',len(pool),')')
print('réseaux restants', collections.Counter(len(c['need']) for c in contents))
for c in sorted([c for c in contents if c['saison']],key=lambda c:c['orig']): print('  saison',c['orig'][:10],c['theme'][:60])
