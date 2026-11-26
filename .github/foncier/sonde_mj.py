# Sonde : pages « mandataires judiciaires » des 36 cours d'appel (nom, adresse, téléphone)
import requests, re, html
H = {'User-Agent': 'Mozilla/5.0 (TerrenUrbanisme; contact@terrenurbanisme.com)'}
CA = ['agen','aix-en-provence','amiens','angers','bastia','besancon','bordeaux','bourges','caen','chambery','colmar','dijon','douai','grenoble','limoges','lyon','metz','montpellier','nancy','nimes','orleans','paris','pau','poitiers','reims','rennes','riom','rouen','toulouse','versailles','basse-terre','fort-de-france','cayenne','saint-denis-de-la-reunion','noumea','papeete']
for ca in CA:
    found = []
    try:
        r = requests.get(f'https://www.cours-appel.justice.fr/{ca}/search?keys=mandataires+judiciaires', headers=H, timeout=30)
        links = sorted(set(re.findall(r'href="(/' + re.escape(ca) + r'/[^"#?]*mandataire[^"#?]*)"', r.text)))
        for l in links[:6]:
            t = requests.get('https://www.cours-appel.justice.fr' + l, headers=H, timeout=30).text
            tx = html.unescape(re.sub(r'<[^>]+>', ' ', t))
            tel = len(re.findall(r'(?:T[ée]l[ée]phone|T[ée]l)\s*\.?\s*:?\s*0\d[\s.]?\d\d', tx))
            mail = len(re.findall(r'[\w.-]+@[\w-]+\.\w+', tx))
            found.append((l, tel, mail))
    except Exception as e:
        found.append(('ERR ' + str(e)[:60], 0, 0))
    print(ca, found, flush=True)
