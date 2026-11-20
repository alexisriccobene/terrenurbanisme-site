import requests, os, subprocess, json
H={'User-Agent':'Mozilla/5.0'}
p=requests.get('https://apicarto.ign.fr/api/cadastre/parcelle?code_insee=2B251&section=AB&numero=0282',headers=H,timeout=60).json()
g=p['features'][0]['geometry']['coordinates'][0][0]; print('COORD', g[:3])
r=requests.get('https://apicarto.ign.fr/api/cadastre/parcelle?code_insee=2B251&section=AB&numero=0282',headers=H,timeout=60)
os.makedirs('/tmp/out',exist_ok=True)
for i,u in enumerate(['https://prunellidifiumorbu.fr/wp-content/uploads/2022/11/Carte_PLU-zonage-reglementaire-planche-1.pdf','https://prunellidifiumorbu.fr/wp-content/uploads/2022/11/Carte_PLU-zonage-reglementaireplanche-2.pdf','https://prunellidifiumorbu.fr/wp-content/uploads/2022/11/Carte_PLU-zonage-reglementaireplanche-3.pdf']):
    b=requests.get(u,headers=H,timeout=300).content; open(f'/tmp/out/p{i+1}.pdf','wb').write(b); print('PDF',i+1,len(b))
    t=subprocess.run(['pdftotext',f'/tmp/out/p{i+1}.pdf','-'],capture_output=True,text=True).stdout
    print('TXT',i+1, ' 282' in t or '\n282' in t, t[:300].replace('\n',' | '))
