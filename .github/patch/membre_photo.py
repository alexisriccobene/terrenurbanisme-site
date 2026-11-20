# Espace du collaborateur : photo, téléphone et e-mail de son profil
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old = "    return jres({ agence: (mq && mq.nom) || 'Votre agence', owner: mbr.user_id, nom: mbr.nom,"
if s.count(old) != 1: sys.exit('ancre')
s = s.replace(old, """    const { data: pf } = await admin.from('pro_agents').select('telephone, email, photo').eq('id', mbr.id).maybeSingle();
    let purl = null; if (pf && pf.photo) { const { data: su } = await admin.storage.from('perso').createSignedUrl(pf.photo, 3600); purl = su && su.signedUrl; }
    return jres({ agence: (mq && mq.nom) || 'Votre agence', owner: mbr.user_id, nom: mbr.nom, telephone: (pf && pf.telephone) || '', email: (pf && pf.email) || '', photo_url: purl,""")
open(p, 'w', encoding='utf-8').write(s); print('patch photo membre appliqué')
