(function(){var q=new URLSearchParams(location.search),c=q.get('code'),st=q.get('state')||'';
// Connexion lancée depuis la console de publication : l'autorisation est enregistrée directement, puis retour à la console
if(c&&/^c_[a-f0-9]{32}$/.test(st)){var p=document.createElement('p');p.textContent='Connexion du compte TikTok en cours…';document.getElementById('ko').parentNode.insertBefore(p,document.getElementById('ko'));
var cfg=window.TU_CONFIG||{};fetch((cfg.supabaseUrl||'https://nmoigruxnhsidrhqtzid.supabase.co')+'/functions/v1/tiktok-console',{method:'POST',headers:{'Content-Type':'application/json','apikey':cfg.supabaseKey||''},body:JSON.stringify({action:'retour',code:c,state:st})})
.then(function(r){return r.json()}).then(function(j){if(j&&j.ok){p.textContent='Compte TikTok connecté. Retour à la console…';location.replace('/tiktok-publier.html')}else{p.textContent='La connexion n’a pas abouti ('+((j&&j.error)||'erreur')+'). Recommencez depuis la console.'}})
.catch(function(){p.textContent='La connexion n’a pas abouti. Recommencez depuis la console.'});return}
if(c){document.getElementById('c').textContent=c;document.getElementById('ok').hidden=false;
var b=document.getElementById('cp');b.addEventListener('click',function(){navigator.clipboard.writeText(c).then(function(){b.textContent='Code copié'},function(){var r=document.createRange();r.selectNodeContents(document.getElementById('c'));var s=getSelection();s.removeAllRanges();s.addRange(r)})})}
else{document.getElementById('ko').hidden=false}})();
