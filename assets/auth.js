/* TerrenUrbanisme — connexion (Supabase Auth : lien e-mail ou Google) */
(function(){
  'use strict';
  var cfg = window.TU_CONFIG || {};
  var ready = !!(cfg.supabaseUrl && cfg.supabaseKey && window.supabase);
  var sb = ready ? window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseKey, { auth: { flowType: 'implicit', detectSessionInUrl: true, persistSession: true } }) : null;
  var $ = function(id){ return document.getElementById(id); };

  function safeRedirect(r){ r = (r || '').split('#')[0]; return (r && r.charAt(0) === '/' && r.charAt(1) !== '/') ? r : '/espace.html'; }

  var Auth = {
    ready: ready,
    client: sb,
    user: function(){ return sb ? sb.auth.getSession().then(function(r){ return r.data.session ? r.data.session.user : null; }) : Promise.resolve(null); },
    loginUrl: function(redirect){ return '/connexion.html?redirect=' + encodeURIComponent((redirect || (location.pathname + location.search)).split('#')[0]); },
    /* Solde et abonnement du client */
    account: function(){
      if (!sb) return Promise.resolve(null);
      return Auth.user().then(function(u){ if (!u) return null; return sb.from('comptes').select('*').eq('user_id', u.id).maybeSingle().then(function(r){ var c = r.data || { credits_abonnement:0, credits_achetes:0 }; var sub = ['active','trialing'].indexOf(c.statut_abonnement) >= 0; c.total = (sub ? c.credits_abonnement : 0) + c.credits_achetes; c.abonne = ['active','trialing','past_due','unpaid','incomplete'].indexOf(c.statut_abonnement) >= 0; return c; }); }).catch(function(){ return null; });
    },
    /* Paiement : kind = unit | pack3 | pack5 | essentiel | pro | cabinet ; parcel facultatif */
    checkout: function(kind, parcel){
      if (!sb) return Promise.reject(new Error('off'));
      return Auth.user().then(function(u){
        if (!u){ location.href = Auth.loginUrl(location.pathname + location.search); return new Promise(function(){}); }
        var body = Object.assign({ kind: kind }, parcel || {});
        return sb.functions.invoke('create-checkout', { body: body }).then(function(r){
          if (r.error){ return (r.error.context && r.error.context.json ? r.error.context.json() : Promise.resolve({})).then(function(j){ var e = new Error(j && j.error || 'stripe'); e.code = j && j.error; throw e; }); }
          if (!r.data || !r.data.url) throw new Error('no url');
          location.href = r.data.url;
        });
      });
    },
    portal: function(){
      return sb.functions.invoke('create-checkout', { body: { action: 'portal' } }).then(function(r){ if (r.error || !r.data || !r.data.url) throw r.error || new Error('portal'); location.href = r.data.url; });
    },
    /* Générer un rapport avec un crédit du solde */
    generate: function(parcel){
      return sb.functions.invoke('stripe-webhook', { body: parcel }).then(function(r){
        if (r.error){ return (r.error.context && r.error.context.json ? r.error.context.json() : Promise.resolve({})).then(function(j){ var e = new Error(j && j.error || 'gen'); e.code = j && j.error; throw e; }); }
        location.href = '/merci.html?session_id=' + encodeURIComponent(r.data.session) + '&credit=1';
      });
    },
    redeem: function(code){
      return sb.functions.invoke('stripe-webhook', { body: { action: 'redeem', code: code } }).then(function(r){
        if (r.error){ return (r.error.context && r.error.context.json ? r.error.context.json() : Promise.resolve({})).then(function(j){ var e = new Error(j && j.error || 'redeem'); e.code = j && j.error; throw e; }); }
        return r.data;
      });
    },
    track: function(etape, p){
      if (!sb) return;
      try {
        Auth.user().then(function(u){
          return sb.from('essais_diagnostic').insert({ etape: etape, insee: p && p.insee || null, commune: p && p.commune ? String(p.commune).slice(0,80) : null, connecte: !!u });
        }).catch(function(){});
      } catch(e){}
    },
    saveDiagnostic: function(row){
      if (!sb) return Promise.resolve();
      return Auth.user().then(function(u){
        if (!u) return; row.user_id = u.id;
        return sb.from('diagnostics').select('id').eq('insee', row.insee).eq('section', row.section).eq('numero', row.numero).limit(1).then(function(r){
          if (r.data && r.data.length) return sb.from('diagnostics').update({ verdict: row.verdict, zone: row.zone }).eq('id', r.data[0].id);
          return sb.from('diagnostics').insert(row);
        });
      }).catch(function(){});
    }
  };
  window.TUAuth = Auth;

  /* En-tête : « Se connecter » ou « Mon espace » */
  var link = $('auth-link');
  if (link) Auth.user().then(function(u){ if (u){ link.textContent = 'Mon espace'; link.href = '/espace.html'; } });

  /* Page de connexion */
  var form = $('login-form');
  if (form){
    var redirect = safeRedirect(new URLSearchParams(location.search).get('redirect'));
    var msg = $('login-msg'), btn = $('login-btn'), email = $('login-email');
    Auth.user().then(function(u){ if (u) location.replace(redirect); });
    email.addEventListener('input', function(){ btn.disabled = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()); });
    form.addEventListener('submit', function(e){
      e.preventDefault();
      if (!sb){ msg.className = 'err'; msg.textContent = 'La connexion n\'est pas encore activée sur ce site.'; return; }
      btn.disabled = true; btn.textContent = 'Envoi en cours…';
      sb.auth.signInWithOtp({ email: email.value.trim(), options: { emailRedirectTo: location.origin + redirect } }).then(function(r){
        if (r.error) throw r.error;
        form.hidden = true; $('login-sent').hidden = false; $('sent-to').textContent = email.value.trim();
      }).catch(function(){
        msg.className = 'err'; msg.textContent = 'L\'envoi du lien a échoué. Vérifiez l\'adresse et réessayez.';
        btn.disabled = false; btn.textContent = 'Recevoir mon lien et mon diagnostic';
      });
    });
    if (!cfg.google){ var gb = $('google-btn'), orr = document.querySelector('.auth-or'); if (gb) gb.hidden = true; if (orr) orr.hidden = true; }
    $('google-btn').addEventListener('click', function(){
      if (!sb){ msg.className = 'err'; msg.textContent = 'La connexion n\'est pas encore activée sur ce site.'; return; }
      sb.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: location.origin + redirect } });
    });
  }

  /* Espace client */
  var space = $('espace');
  if (space){
    Auth.user().then(function(u){
      if (!u){ location.replace(Auth.loginUrl('/espace.html')); return; }
      $('esp-mail').textContent = u.email;
      sb.from('diagnostics').select('*').order('created_at', { ascending:false }).limit(50).then(function(r){
        var seen = {}, rows = (r.data || []).filter(function(d){ var k = d.insee + '|' + d.section + '|' + d.numero; if (seen[k]) return false; seen[k] = 1; return true; }), list = $('esp-list');
        if (!rows.length){ list.innerHTML = '<p class="empty">Aucune recherche pour le moment. <a href="/#recherche">Recherchez votre premier terrain</a>.</p>'; return; }
        list.innerHTML = rows.map(function(d){
          var url = '/?commune=' + encodeURIComponent(d.commune) + '&section=' + encodeURIComponent(d.section) + '&numero=' + encodeURIComponent(d.numero) + '#recherche';
          var badge = { ok:['v-ok','Constructible'], cond:['v-cond','Sous conditions'], non:['v-non','Non constructible'] }[d.verdict] || ['v-cond','À vérifier'];
          return '<div class="drow"><a class="dlink" href="' + url + '"><b>' + esc(d.commune) + ' · section ' + esc(d.section) + ' · n° ' + esc(d.numero) + '</b><small>' + new Date(d.created_at).toLocaleDateString('fr-FR') + (d.zone ? ' · zone ' + esc(d.zone) : '') + '</small></a><div class="dact"><button type="button" class="dl gen" data-insee="' + esc(d.insee) + '" data-commune="' + esc(d.commune) + '" data-section="' + esc(d.section) + '" data-numero="' + esc(d.numero) + '">Rapport complet</button></div></div>';
        }).join('');
        list.querySelectorAll('button.gen').forEach(function(b){
          b.addEventListener('click', function(){
            var parcel = { insee: b.dataset.insee, commune: b.dataset.commune, section: b.dataset.section, numero: b.dataset.numero };
            b.disabled = true; b.textContent = 'Un instant…';
            Auth.account().then(function(c){
              if (c && c.total > 0){ if (!confirm('Générer le rapport complet de ' + parcel.commune + ' ' + parcel.section + ' ' + parcel.numero + ' ? 1 rapport sera décompté de votre solde (' + c.total + ').')) { b.disabled = false; b.textContent = 'Rapport complet'; return; } return Auth.generate(parcel); }
              return Auth.checkout('unit', parcel);
            }).catch(function(){ b.disabled = false; b.textContent = 'Réessayer'; });
          });
        });
      });
      loadDossiers($('esp-dossiers'), null);
      renderOffer();
    });
    $('logout').addEventListener('click', function(){ sb.auth.signOut().then(function(){ location.href = '/'; }); });
  }
  /* Rapports complets payés */
  function dossierRow(d){
    var title = esc(d.commune) + ' · section ' + esc(d.section) + ' · n° ' + esc(d.numero);
    var right = d.status === 'ready' ? (d.download_slug ? '<a class="dl" href="/r/' + encodeURIComponent(d.download_slug) + '" target="_blank" rel="noopener">Ouvrir le rapport</a>' : '<a class="dl" href="#" data-path="' + esc(d.pdf_path) + '">Télécharger le PDF</a>')
      : d.status === 'error' ? '<span class="wait">En cours de traitement, nous revenons vers vous</span>'
      : '<span class="wait">Préparation…</span>';
    return '<div class="drow"><div><b>' + title + '</b><small>Rapport du ' + new Date(d.created_at).toLocaleDateString('fr-FR') + (d.order_ref ? ' · n° ' + esc(d.order_ref) : '') + '</small></div>' + right + '</div>';
  }
  function bindDl(box){
    box.querySelectorAll('a.dl[data-path]').forEach(function(a){
      a.addEventListener('click', function(e){
        e.preventDefault();
        sb.storage.from('dossiers').createSignedUrl(a.getAttribute('data-path'), 300).then(function(r){ if (r.data) location.href = r.data.signedUrl; });
      });
    });
  }
  function loadDossiers(box, sessionId){
    if (!box) return Promise.resolve([]);
    var q = sb.from('dossiers').select('*').order('created_at', { ascending:false }).limit(50);
    if (sessionId) q = q.eq('stripe_session_id', sessionId);
    return q.then(function(r){
      var rows = r.data || [];
      if (!rows.length){ box.innerHTML = '<p class="empty">' + (sessionId ? 'Préparation du rapport…' : 'Aucun rapport complet pour le moment.') + '</p>'; return rows; }
      box.innerHTML = rows.map(dossierRow).join(''); bindDl(box); return rows;
    });
  }

  /* Page de remerciement après paiement */
  var merci = $('merci-box');
  if (merci){
    var qs = new URLSearchParams(location.search), sid = qs.get('session_id'), achat = qs.get('achat'), tries = 0;
    Auth.user().then(function(u){
      if (!u){ location.replace(Auth.loginUrl('/espace.html')); return; }
      // Mesure de la vente (Google Ads, Meta), envoyée une seule fois et seulement avec le consentement du visiteur
      if (sid && /^cs_/.test(sid) && window.TU_conversion){
        var PRIX = { unit:19.9, pack3:49.9, pack5:74.9, essentiel:29, pro:69, cabinet:149, essentiel_an:276, pro_an:660, cabinet_an:1428 };
        var once = true; try { once = !localStorage.getItem('tu_conv_' + sid); localStorage.setItem('tu_conv_' + sid, '1'); } catch (e) {}
        if (once) window.TU_conversion(PRIX[achat || 'unit'], sid);
      }
      if (achat){
        var h1 = document.querySelector('#merci h1'), lede = document.querySelector('#merci .lede');
        var abo = ['essentiel','pro','cabinet','essentiel_an','pro_an','cabinet_an'].indexOf(achat) >= 0;
        if (h1) h1.textContent = abo ? 'Bienvenue, votre abonnement est actif' : 'Merci, vos rapports sont crédités';
        if (lede) lede.textContent = abo ? 'Vos rapports du mois sont disponibles. Lancez une recherche, puis générez le rapport complet en un clic.' : 'Votre solde est mis à jour. Lancez une recherche, puis générez le rapport complet en un clic.';
        (function pollAcc(){
          Auth.account().then(function(c){
            var n = c ? c.total : 0;
            merci.innerHTML = '<div class="acct"><div><small>Rapports disponibles</small><b>' + n + '</b></div><a class="btn" href="/#recherche">Rechercher une parcelle</a></div>';
            if (!n && ++tries < 20) setTimeout(pollAcc, 3000);
          });
        })();
        return;
      }
      if (qs.get('credit')){ var t1 = document.querySelector('#merci h1'); if (t1) t1.textContent = 'Votre rapport est en préparation'; }
      // Suivi de la préparation : le rapport demande en général 1 à 3 minutes (lecture du règlement, croisement des sources)
      var t0 = Date.now(), wait = document.createElement('div'); wait.className = 'gen-wait'; merci.parentNode.insertBefore(wait, merci);
      var STEPS = ['Lecture du cadastre et du zonage', 'Lecture du règlement de la zone', 'Risques, réseaux et fibre', 'Marché immobilier et permis', 'Mise en page du rapport'];
      function showWait(done){
        if (done){ wait.innerHTML = '<b>Votre rapport est prêt.</b> Il vient aussi de vous être envoyé par e-mail.'; wait.classList.add('ok'); return; }
        var s = Math.round((Date.now() - t0) / 1000), k = Math.min(STEPS.length - 1, Math.floor(s / 25));
        wait.innerHTML = '<span class="spin"></span><div><b>Préparation de votre rapport… ' + (s < 60 ? s + ' s' : Math.floor(s / 60) + ' min ' + (s % 60) + ' s') + '</b><span>' + STEPS[k] + '. Comptez 1 à 3 minutes : vous pouvez laisser cette page ouverte, le rapport vous sera aussi envoyé par e-mail.</span></div>';
      }
      showWait(false); var tick = setInterval(function(){ showWait(false); }, 1000);
      (function poll(){
        loadDossiers(merci, sid).then(function(rows){
          var pending = !rows.length || rows[0].status === 'pending';
          if (!pending){ clearInterval(tick); showWait(true); return; }
          if (++tries < 150) setTimeout(poll, 4000); else { clearInterval(tick); wait.innerHTML = 'La préparation prend plus de temps que prévu. Le rapport vous sera envoyé par e-mail dès qu\'il sera prêt, et apparaîtra dans <a href="/espace.html">votre espace</a>.'; }
        }).catch(function(){ if (++tries < 150) setTimeout(poll, 4000); });
      })();
    });
  }

  /* Bloc « Mon offre » de l'espace client */
  function renderOffer(){
    var box = $('esp-offre'); if (!box) return;
    Auth.account().then(function(c){
      c = c || { total:0 };
      var plan = c.formule ? ({ essentiel:'Essentiel', pro:'Agence', cabinet:'Réseau', essentiel_an:'Essentiel annuel', pro_an:'Agence annuel', cabinet_an:'Réseau annuel' })[c.formule] : null;
      var fin = c.fin_periode ? new Date(c.fin_periode).toLocaleDateString('fr-FR') : '';
      var status = !c.abonne ? 'Sans abonnement' : c.statut_abonnement === 'past_due' ? 'Paiement à régulariser' : c.resiliation_prevue ? 'Résilié, actif jusqu\'au ' + fin : 'Renouvellement le ' + fin;
      box.innerHTML = '<div class="acct">' +
        '<div><small>Rapports disponibles</small><b>' + c.total + '</b>' + (c.abonne ? '<span>dont ' + (c.credits_abonnement || 0) + ' de l\'abonnement' + (c.credits_achetes ? ' et ' + c.credits_achetes + ' achetés' : '') + '</span>' : '') + '</div>' +
        '<div><small>Formule</small><b>' + (plan || 'À l\'unité') + '</b><span>' + esc(status) + '</span></div>' +
        '<div class="acct-act"><a class="btn" href="/tarifs.html">' + (c.abonne ? 'Ajouter des rapports' : 'Voir les formules') + '</a>' + (c.stripe_customer ? '<button type="button" class="btn ghost" id="portal">' + (c.abonne ? 'Gérer mon abonnement' : 'Mes factures') + '</button>' : '') + '</div></div>';
      var pb = $('portal'); if (pb) pb.addEventListener('click', function(){ pb.disabled = true; pb.textContent = 'Ouverture…'; Auth.portal().catch(function(){ pb.disabled = false; pb.textContent = 'Réessayer'; }); });
    });
  }

  /* Page d'essai offert */
  var essai = $('essai-box');
  if (essai){
    var code = new URLSearchParams(location.search).get('code') || '';
    Auth.user().then(function(u){
      if (!u){ location.replace(Auth.loginUrl('/essai.html?code=' + encodeURIComponent(code))); return; }
      Auth.redeem(code).then(function(r){
        var n = r && r.credits || 1;
        essai.innerHTML = '<div class="acct"><div><small>Essai offert</small><b>' + n + ' rapport' + (n > 1 ? 's' : '') + ' offert' + (n > 1 ? 's' : '') + '</b><span>Crédité' + (n > 1 ? 's' : '') + ' sur votre compte</span></div><div><small>Prochaine étape</small><b style="font-size:18px">Recherchez votre terrain</b><span>Puis cliquez sur « Générer le rapport complet »</span></div><div class="acct-act"><a class="btn" href="/#recherche">Rechercher une parcelle</a></div></div>';
      }).catch(function(e){
        var m = { deja_utilise:'Ce lien d\'essai a déjà été utilisé.', deja_utilise_par_vous:'Vous avez déjà utilisé ce lien : votre rapport offert est dans votre solde.', expire:'Ce lien d\'essai a expiré.', code:'Ce lien d\'essai n\'est pas valide.' }[e && e.code] || 'Le lien n\'a pas pu être validé. Réessayez dans un instant.';
        essai.innerHTML = '<p class="empty">' + m + ' <a href="/tarifs.html">Voir les offres</a></p>';
      });
    });
  }

  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]; }); }
})();
