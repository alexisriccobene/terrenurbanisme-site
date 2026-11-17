import requests, re
H={'User-Agent':'Mozilla/5.0'}
for u in ['https://prunellidifiumorbu.fr/plu/','https://prunellidifiumorbu.fr/revision-plu/']:
    try:
        t=requests.get(u,headers=H,timeout=60).text
        for m in sorted(set(re.findall(r'href="([^"]+\.(?:pdf|PDF|zip|jpg|png))"',t))): print('LIEN',u,m)
    except Exception as e: print('ERR',u,e)
