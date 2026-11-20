/* TerrenUrbanisme — console de publication TikTok (Content Posting API, Direct Post) */
document.addEventListener('DOMContentLoaded', function(){
  'use strict';
  var A = window.TUAuth, sb = A && A.client, $ = function(id){ return document.getElementById(id); };
  var PRIV = { PUBLIC_TO_EVERYONE: 'Tout le monde', MUTUAL_FOLLOW_FRIENDS: 'Amis (abonnements réciproques)', FOLLOWER_OF_CREATOR: 'Mes abonnés', SELF_ONLY: 'Moi uniquement (privé)' };
  var ST = { PROCESSING_UPLOAD: 'Envoi de la vidéo à TikTok…', PROCESSING_DOWNLOAD: 'TikTok récupère la vidéo…', SEND_TO_USER_INBOX: 'Vidéo envoyée dans votre boîte de réception TikTok.', PUBLISH_COMPLETE: 'Publication terminée. La vidéo peut mettre quelques minutes à apparaître sur votre profil.', FAILED: 'TikTok a refusé la publication' };
  var MUSIC = '<a href="https://www.tiktok.com/legal/page/global/music-usage-confirmation/fr" target="_blank" rel="noopener">confirmation d\'utilisation de la musique</a>';
  var BC = '<a href="https://www.tiktok.com/legal/page/global/bc-policy/fr" target="_blank" rel="noopener">politique relative au contenu de marque</a>';
  var cr = null, reels = [], cur = null, dur = 0;
  function show(id){ ['tk-load','tk-login','tk-noauth','tk-connect','tk-app'].forEach(function(k){ $(k).hidden = k !== id; }); }
  function call(body){
    return sb.functions.invoke('tiktok-console', { body: body }).then(function(r){
      if (r.error){ return (r.error.context && r.error.context.json ? r.error.context.json() : Promise.resolve({})).then(function(j){ var m = (j && j.message) || '', c = (j && j.error) || 'erreur', e = new Error(c === 'unaudited_client_can_only_post_to_private_accounts' ? 'tant que TikTok n\'a pas validé l\'application, le compte TikTok doit être réglé en « Compte privé » (Profil > Paramètres > Confidentialité) pour publier. Remettez-le en public juste après.' : (m ? m + ' (' + c + ')' : c)); e.code = c; throw e; }); }
      return r.data;
    });
  }
  if (!sb){ $('tk-load').textContent = 'Service indisponible.'; return; }

  A.user().then(function(u){
    if (!u){ show('tk-login'); return; }
    charger();
  });

  function charger(){
    call({ action: 'etat' }).then(function(d){
      reels = d.reels || [];
      if (!d.connecte){ show('tk-connect'); return; }
      show('tk-app');
      cr = d.createur || null;
      if (!cr){ $('tk-cap').hidden = false; $('tk-cap').textContent = 'Le compte TikTok ne répond pas (' + (d.message || d.erreur || 'erreur') + '). Reconnectez le compte.'; return; }
      $('tk-avatar').src = cr.creator_avatar_url || ''; $('tk-nick').textContent = cr.creator_nickname || '';
      $('tk-user').textContent = '@' + (cr.creator_username || '');
      liste();
    }).catch(function(e){ if (e.code === 'auth') show('tk-noauth'); else { show('tk-load'); $('tk-load').textContent = 'Erreur de chargement : ' + e.message; } });
  }

  $('tk-go').addEventListener('click', function(){
    var b = this; b.disabled = true;
    call({ action: 'connecter' }).then(function(d){ location.href = d.url; }).catch(function(e){ b.disabled = false; alertErr(e); });
  });
  $('tk-off').addEventListener('click', function(){
    var b = this; b.disabled = true;
    call({ action: 'deconnecter' }).then(function(){ location.reload(); }).catch(function(){ b.disabled = false; });
  });

  function liste(){
    var L = $('tk-list'); L.innerHTML = '';
    reels.forEach(function(r){
      var b = document.createElement('button'); b.type = 'button'; b.className = 'it';
      b.innerHTML = '<b>Vidéo ' + r.numero + '</b><small></small>' + (r.publie ? '<span class="tag">Déjà publiée</span>' : '');
      b.querySelector('small').textContent = r.theme;
      b.addEventListener('click', function(){ L.querySelectorAll('.it').forEach(function(x){ x.classList.toggle('on', x === b); }); choisir(r); });
      L.appendChild(b);
    });
  }

  function choisir(r){
    cur = r; $('tk-form').hidden = false;
    var v = $('tk-video'); v.src = r.video; dur = 0; $('tk-dur').textContent = '';
    v.onloadedmetadata = function(){ dur = v.duration || 0; var max = cr.max_video_post_duration_sec || 0; $('tk-dur').textContent = 'Durée : ' + Math.round(dur) + ' s' + (max ? ' · maximum autorisé pour ce compte : ' + max + ' s' : ''); valider(); };
    $('tk-title').value = r.texte || ''; compter();
    var sel = $('tk-priv'); sel.innerHTML = '<option value="" selected disabled>Choisir la confidentialité</option>';
    (cr.privacy_level_options || []).forEach(function(p){ var o = document.createElement('option'); o.value = p; o.textContent = PRIV[p] || p; sel.appendChild(o); });
    [['com','comment_disabled'],['duo','duet_disabled'],['sti','stitch_disabled']].forEach(function(x){
      var i = $('tk-' + x[0]), dis = !!cr[x[1]]; i.checked = false; i.disabled = dis; $('l-' + x[0]).classList.toggle('off', dis);
      $('l-' + x[0]).title = dis ? 'Désactivé dans les réglages de votre compte TikTok' : '';
    });
    $('tk-cc').checked = false; $('tk-own').checked = false; $('tk-brand').checked = false; $('tk-cc-box').hidden = true; $('tk-ok').checked = false;
    $('tk-err').hidden = true; $('tk-st').hidden = true;
    regles(); valider();
    $('tk-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function compter(){ $('tk-count').textContent = $('tk-title').value.length; }
  $('tk-title').addEventListener('input', compter);

  function regles(){
    var cc = $('tk-cc').checked, own = $('tk-own').checked, brand = $('tk-brand').checked, sel = $('tk-priv');
    $('tk-cc-box').hidden = !cc;
    // Contenu de marque : la vidéo ne peut pas être privée
    Array.prototype.forEach.call(sel.options, function(o){ if (o.value === 'SELF_ONLY'){ o.disabled = cc && brand; o.textContent = PRIV.SELF_ONLY + (cc && brand ? ' (indisponible pour un contenu de marque)' : ''); } });
    if (cc && brand && sel.value === 'SELF_ONLY') sel.value = '';
    var w = $('tk-cc-warn');
    if (cc && !own && !brand){ w.hidden = false; w.textContent = 'Indiquez si vous faites la promotion de votre marque, d\'une autre marque, ou des deux.'; }
    else w.hidden = true;
    var lab = '';
    if (cc && brand) lab = 'La vidéo sera étiquetée « Partenariat rémunéré ». ';
    else if (cc && own) lab = 'La vidéo sera étiquetée « Contenu promotionnel ». ';
    $('tk-legal').innerHTML = lab + 'En publiant, vous acceptez ' + (cc && brand ? 'la ' + BC + ' et ' : '') + 'la ' + MUSIC + ' de TikTok.';
  }
  ['tk-cc','tk-own','tk-brand'].forEach(function(id){ $(id).addEventListener('change', function(){ regles(); valider(); }); });
  ['tk-priv','tk-ok','tk-title'].forEach(function(id){ $(id).addEventListener('input', valider); $(id).addEventListener('change', valider); });

  function valider(){
    var max = cr && cr.max_video_post_duration_sec || 0, trop = max && dur > max;
    var cc = $('tk-cc').checked, okcc = !cc || $('tk-own').checked || $('tk-brand').checked;
    var ok = cur && $('tk-priv').value && $('tk-ok').checked && okcc && !trop;
    $('tk-pub').disabled = !ok;
    if (trop){ $('tk-err').hidden = false; $('tk-err').textContent = 'Cette vidéo dépasse la durée maximale autorisée pour ce compte.'; }
  }

  function alertErr(e){ $('tk-err').hidden = false; $('tk-err').textContent = 'Publication impossible : ' + (e.message || e.code || 'erreur'); }

  $('tk-pub').addEventListener('click', function(){
    var b = this; b.disabled = true; $('tk-err').hidden = true;
    var st = $('tk-st'); st.hidden = false; st.textContent = 'Envoi de la vidéo à TikTok…';
    call({ action: 'publier', reel: cur.id, titre: $('tk-title').value, confidentialite: $('tk-priv').value,
      commentaires: $('tk-com').checked, duo: $('tk-duo').checked, collage: $('tk-sti').checked,
      commercial: { actif: $('tk-cc').checked, ma_marque: $('tk-own').checked, partenariat: $('tk-brand').checked }, consentement: $('tk-ok').checked })
    .then(function(d){ suivre(d.publish_id, 0); })
    .catch(function(e){ st.hidden = true; b.disabled = false; alertErr(e); });
  });

  function suivre(pid, n){
    call({ action: 'statut', publish_id: pid }).then(function(d){
      var st = $('tk-st');
      st.textContent = (ST[d.statut] || d.statut) + (d.statut === 'FAILED' && d.raison ? ' : ' + d.raison : '');
      if (d.statut === 'PUBLISH_COMPLETE' || d.statut === 'SEND_TO_USER_INBOX' || d.statut === 'FAILED'){ if (cur) cur.publie = d.statut !== 'FAILED'; liste(); return; }
      if (n < 40) setTimeout(function(){ suivre(pid, n + 1); }, 5000);
      else st.textContent = 'Publication en cours de traitement chez TikTok. Elle apparaîtra sur votre profil dans quelques minutes.';
    }).catch(function(){ if (n < 40) setTimeout(function(){ suivre(pid, n + 1); }, 5000); });
  }
});
