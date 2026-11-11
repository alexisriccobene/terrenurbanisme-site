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
      return Auth.user().then(function(u){ if (!u) return null; return sb.from('comptes').select('*').eq('user_id', u.id).maybeSingle().then(function(r){ var c = r.data || { credits_abonnement:0, credits_achetes:0 }; var sub = ['active','trialing'].indexOf(c.statut_abonnement) >= 0; c.total = (sub ? c.credits_abonnement : 0) + c.credits_achetes; c.abonne = ['active','trialing','past_due','unpaid','incomplete'].indexOf(c.statut_abonnement) >= 0; return Auth.mairie().then(function(mr){ if (mr && mr.illimite){ c.illimite = true; c.total = 9999; } return c; }); }); }).catch(function(){ return null; });
    },
    /* Paiement : kind = unit | pack2 | pack3 | essentiel | pro | cabinet | essentiel_an | pro_an | cabinet_an ; parcel facultatif (le premier rapport porte sur la parcelle) */
    checkout: function(kind, parcel){
      if (!sb) return Promise.reject(new Error('off'));
      return Auth.user().then(function(u){
        // Rapport à l'unité ou lot : paiement sans compte (e-mail saisi sur la page de paiement) ; abonnement : compte nécessaire
        var invite = !u && /^(unit|pack2|pack3)$/.test(kind);
        if (!u && !invite){ location.href = Auth.loginUrl(location.pathname + location.search); return new Promise(function(){}); }
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
    /* Abonnement mairie : communes couvertes pour ce compte (null sinon) */
    mairie: function(){
      if (!sb) return Promise.resolve(null);
      if (Auth._mairie) return Auth._mairie;
      Auth._mairie = Auth.user().then(function(u){ if (!u) return null; return sb.functions.invoke('stripe-webhook', { body: { action: 'mairie' } }).then(function(r){ return r.data && (r.data.mairie || r.data.illimite) ? r.data : null; }); }).catch(function(){ Auth._mairie = null; return null; });
      return Auth._mairie;
    },
    relance: function(session){
      if (!sb) return Promise.resolve();
      return sb.functions.invoke('stripe-webhook', { body: { action: 'relance', session: session || '' } }).catch(function(){});
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
  /* Annuaire des professionnels : chargé seulement sur les pages qui l'utilisent */
  if (document.getElementById('commune-page') || document.getElementById('annuaire') || document.getElementById('pro-form')){ var ps = document.createElement('script'); ps.src = '/assets/pros.js?v=' + ((document.querySelector('script[src*="auth.js"]') || {}).src || '').split('v=')[1]; ps.defer = true; document.head.appendChild(ps); }

  /* En-tête : « Se connecter » ou « Mon espace » */
  var link = $('auth-link');
  if (link) Auth.user().then(function(u){ if (u){ link.textContent = 'Mon espace'; link.href = '/espace.html'; } });

  /* Page de connexion : e-mail et mot de passe (connexion, création de compte, mot de passe oublié) */
  var form = $('login-form');
  if (form){
    var qs0 = new URLSearchParams(location.search);
    var redirect = safeRedirect(qs0.get('redirect'));
    var msg = $('login-msg'), btn = $('login-btn'), email = $('login-email'), pw = $('login-pw'), pw2 = $('login-pw2');
    var mode = 'login', recovery = qs0.get('nouveau') === '1' || /type=recovery/.test(location.hash);
    var L = {
      login:  ['Accédez à votre espace', 'Connectez-vous avec votre adresse e-mail et votre mot de passe.', 'Se connecter', 'Pas encore de compte ?', 'Créer un compte'],
      signup: ['Créez votre compte', 'Choisissez votre mot de passe : 8 caractères au minimum.', 'Créer mon compte', 'Déjà un compte ?', 'Se connecter'],
      reset:  ['Mot de passe oublié', 'Indiquez votre adresse e-mail : vous recevez un lien pour choisir un nouveau mot de passe.', 'Recevoir le lien', 'Vous vous en souvenez ?', 'Se connecter'],
      nouveau:['Nouveau mot de passe', 'Choisissez votre nouveau mot de passe : 8 caractères au minimum.', 'Enregistrer et continuer', '', '']
    };
    function setMode(m){
      mode = m; var l = L[m]; msg.textContent = '';
      $('lf-title').textContent = l[0]; $('lf-lede').textContent = l[1]; btn.textContent = l[2];
      $('lf-sw-t').textContent = l[3]; $('lf-sw-a').textContent = l[4]; $('lf-sw').hidden = m === 'nouveau';
      email.parentNode.hidden = m === 'nouveau'; $('lf-pw').hidden = m === 'reset'; $('lf-pw2').hidden = !(m === 'signup' || m === 'nouveau');
      $('lf-forgot').hidden = m !== 'login';
      pw.setAttribute('autocomplete', m === 'login' ? 'current-password' : 'new-password');
      var gb = $('google-btn'), orr = document.querySelector('.auth-or'); if (cfg.google && gb){ gb.hidden = m === 'nouveau' || m === 'reset'; if (orr) orr.hidden = gb.hidden; }
    }
    $('lf-sw-a').addEventListener('click', function(e){ e.preventDefault(); setMode(mode === 'login' ? 'signup' : 'login'); });
    $('lf-forgot').addEventListener('click', function(e){ e.preventDefault(); setMode('reset'); });
    if (recovery) setMode('nouveau');
    else if (qs0.get('mode') === 'premier'){ setMode('reset'); $('lf-title').textContent = 'Créez votre mot de passe'; $('lf-lede').textContent = 'Indiquez l\'adresse e-mail utilisée pour votre achat : vous recevez un lien pour choisir votre mot de passe et retrouver vos rapports.'; }
    else if (qs0.get('mode') === 'creer') setMode('signup');
    else Auth.user().then(function(u){ if (u) location.replace(redirect); });
    if (sb) sb.auth.onAuthStateChange(function(ev){ if (ev === 'PASSWORD_RECOVERY'){ recovery = true; setMode('nouveau'); } });
    /* Anti-robots Cloudflare Turnstile : invisible pour la plupart des visiteurs, case à cocher seulement en cas de doute */
    var tsToken = null, tsId = null;
    (function tsInit(n){
      if (!cfg.turnstile || !$('ts-box')) return;
      if (!window.turnstile){ if (n < 40) setTimeout(function(){ tsInit(n + 1); }, 250); return; }
      tsId = window.turnstile.render('#ts-box', { sitekey: cfg.turnstile, appearance: 'interaction-only', language: 'fr',
        callback: function(t){ tsToken = t; }, 'expired-callback': function(){ tsToken = null; }, 'error-callback': function(){ tsToken = null; } });
    })(0);
    function waitToken(){
      return new Promise(function(res){ var k = 0; (function w(){ if (tsToken || !tsId || ++k > 40) return res(tsToken); setTimeout(w, 250); })(); });
    }
    function tsReset(){ if (tsId && window.turnstile) { try { window.turnstile.reset(tsId); } catch (x) {} tsToken = null; } }
    function fail(t){ msg.className = 'err'; msg.textContent = t; btn.disabled = false; btn.textContent = L[mode][2]; }
    function sent(title, txt){ form.hidden = true; $('login-sent').hidden = false; $('sent-title').textContent = title; $('sent-txt').innerHTML = txt; }
    form.addEventListener('submit', function(e){
      e.preventDefault(); msg.textContent = '';
      if (!sb){ fail('La connexion n\'est pas encore activée sur ce site.'); return; }
      var em = email.value.trim(), p1 = pw.value, p2 = pw2.value;
      if (mode !== 'nouveau' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)){ fail('Indiquez une adresse e-mail valide.'); return; }
      if (mode !== 'reset' && p1.length < 8){ fail(mode === 'login' ? 'Indiquez votre mot de passe.' : 'Le mot de passe doit contenir au moins 8 caractères.'); return; }
      if ((mode === 'signup' || mode === 'nouveau') && p1 !== p2){ fail('Les deux mots de passe ne sont pas identiques.'); return; }
      btn.disabled = true; btn.textContent = 'Un instant…';
      if (mode === 'nouveau'){
        sb.auth.updateUser({ password: p1 }).then(function(r){ if (r.error) throw r.error; location.replace(redirect); })
          .catch(function(){ fail('Le lien a expiré. Recommencez avec « Mot de passe oublié ».'); });
        return;
      }
      waitToken().then(function(tok){
        var o = tok ? { captchaToken: tok } : {};
        if (mode === 'login') return sb.auth.signInWithPassword({ email: em, password: p1, options: o });
        if (mode === 'signup') return sb.auth.signUp({ email: em, password: p1, options: Object.assign({ emailRedirectTo: location.origin + redirect }, o) });
        return sb.auth.resetPasswordForEmail(em, Object.assign({ redirectTo: location.origin + '/connexion.html?nouveau=1&redirect=' + encodeURIComponent(redirect) }, o));
      }).then(function(r){
        tsReset();
        if (r.error) throw r.error;
        if (mode === 'login') { location.replace(redirect); return; }
        if (mode === 'signup') {
          if (r.data && r.data.session) { location.replace(redirect); return; }
          sent('Confirmez votre adresse e-mail', 'Nous avons envoyé un lien de confirmation à <strong>' + esc(em) + '</strong>. Cliquez dessus pour activer votre compte. Pensez à regarder dans les courriers indésirables.');
          return;
        }
        sent('Vérifiez votre boîte e-mail', 'Si un compte existe pour <strong>' + esc(em) + '</strong>, vous recevez un lien pour choisir un nouveau mot de passe. Pensez à regarder dans les courriers indésirables.');
      }).catch(function(err){
        tsReset();
        var m = String(err && (err.code || err.message) || '');
        if (tsId && !tsToken && /captcha/i.test(m)) return fail('Cochez la case « Vérifiez que vous êtes humain » ci-dessus, puis réessayez.');
        if (mode === 'login') return fail(/not.?confirmed/i.test(m) ? 'Confirmez d\'abord votre adresse e-mail avec le lien reçu.' : 'E-mail ou mot de passe incorrect. Première connexion avec un mot de passe ? Cliquez sur « Mot de passe oublié » pour en créer un.');
        if (mode === 'signup') return fail(/already|exists|registered/i.test(m) ? 'Un compte existe déjà avec cette adresse : connectez-vous, ou utilisez « Mot de passe oublié ».' : /weak|password/i.test(m) ? 'Mot de passe trop simple : choisissez-en un plus long.' : 'La création du compte a échoué. Réessayez dans un instant.');
        fail('L\'envoi a échoué. Vérifiez l\'adresse et réessayez.');
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
      askSource(u, merci, sid);
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
              if (c && c.illimite) return Auth.generate(parcel);
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

  /* Question « Comment nous avez-vous connu ? », posée une seule fois par client après son premier achat */
  function askSource(u, merci, sid){
    if (!sb || !merci) return;
    sb.from('sources_clients').select('user_id').eq('user_id', u.id).maybeSingle().then(function(r){
      if (r.error || r.data) return;
      var OPTS = [['google','Google'],['instagram','Instagram'],['facebook','Facebook'],['linkedin','LinkedIn'],['influenceur','Un influenceur'],['autre','Autre']];
      var box = document.createElement('div'); box.className = 'src-ask';
      box.innerHTML = '<b>Comment avez-vous connu TerrenUrbanisme ?</b><span>Une seule réponse, cela nous aide beaucoup.</span><div class="src-opts">' +
        OPTS.map(function(o){ return '<button type="button" data-src="' + o[0] + '">' + o[1] + '</button>'; }).join('') +
        '</div><div class="src-more" hidden><input type="text" maxlength="200"><button type="button" class="btn" data-ok>Envoyer</button></div>';
      merci.parentNode.appendChild(box);
      var more = box.querySelector('.src-more'), inp = more.querySelector('input'), choix = null;
      function save(detail){
        sb.from('sources_clients').insert({ user_id: u.id, email: u.email || null, source: choix, detail: detail || null, session_id: sid || null }).then(function(){
          box.innerHTML = '<b>Merci pour votre réponse.</b>'; box.classList.add('ok');
        });
      }
      box.querySelectorAll('[data-src]').forEach(function(b){
        b.addEventListener('click', function(){
          choix = b.getAttribute('data-src');
          box.querySelectorAll('[data-src]').forEach(function(x){ x.classList.toggle('on', x === b); });
          if (choix === 'influenceur' || choix === 'autre'){
            inp.placeholder = choix === 'influenceur' ? 'Lequel ? (nom ou code promo, facultatif)' : 'Précisez (facultatif)';
            more.hidden = false; inp.focus();
          } else save(null);
        });
      });
      more.querySelector('[data-ok]').addEventListener('click', function(){ save(inp.value.trim()); });
      inp.addEventListener('keydown', function(e){ if (e.key === 'Enter') save(inp.value.trim()); });
    });
  }

  /* Page de remerciement après paiement */
  var merci = $('merci-box');
  if (merci){
    var qs = new URLSearchParams(location.search), sid = qs.get('session_id'), achat = qs.get('achat'), tries = 0;
    Auth.user().then(function(u){
      // Mesure de la vente (Google Ads, Meta), envoyée une seule fois et seulement avec le consentement du visiteur
      if (sid && /^cs_/.test(sid) && window.TU_conversion){
        var PRIX = { unit:19.9, pack2:29.8, pack3:38.7, essentiel:29, pro:55, cabinet:139, essentiel_an:290, pro_an:550, cabinet_an:1390 };
        var once = true; try { once = !localStorage.getItem('tu_conv_' + sid); localStorage.setItem('tu_conv_' + sid, '1'); } catch (e) {}
        if (once) window.TU_conversion(PRIX[achat || qs.get('k') || 'unit'] || 19.9, sid);
      }
      if (!u && qs.get('invite')){
        // Achat sans compte : le rapport part par e-mail ; l'espace se crée ensuite, sans obligation
        var h0 = document.querySelector('#merci h1'), l0 = document.querySelector('#merci .lede');
        if (h0) h0.textContent = 'Merci, votre paiement est confirmé';
        if (l0) l0.textContent = achat ? 'Vos rapports sont crédités sur votre adresse e-mail.' : 'Votre rapport est en préparation : il arrive par e-mail dans quelques minutes, à l\'adresse indiquée lors du paiement. Pensez à regarder dans les courriers indésirables.';
        merci.innerHTML = '<div class="acct"><div><small>Pour retrouver vos rapports à tout moment</small><b style="font-size:18px">Créez votre mot de passe</b><span>Avec l\'adresse e-mail utilisée pour le paiement. Facultatif.</span></div><a class="btn" href="/connexion.html?mode=premier">Créer mon espace</a></div>';
        return;
      }
      if (!u){ location.replace(Auth.loginUrl('/espace.html')); return; }
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
          var el = Date.now() - t0; if (el > 160000 && (!poll.last || Date.now() - poll.last > 60000)) { poll.last = Date.now(); Auth.relance(sid); }
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
      var plan = c.formule ? ({ essentiel:'Solo', pro:'Agence', cabinet:'Réseau', essentiel_an:'Solo annuel', pro_an:'Agence annuel', cabinet_an:'Réseau annuel' })[c.formule] : null;
      var fin = c.fin_periode ? new Date(c.fin_periode).toLocaleDateString('fr-FR') : '';
      var status = !c.abonne ? 'Sans abonnement' : c.statut_abonnement === 'past_due' ? 'Paiement à régulariser' : c.resiliation_prevue ? 'Résilié, actif jusqu\'au ' + fin : 'Renouvellement le ' + fin;
      box.innerHTML = '<div class="acct">' +
        '<div><small>Rapports disponibles</small><b>' + (c.illimite ? 'Illimité' : c.total) + '</b>' + (c.abonne ? '<span>dont ' + (c.credits_abonnement || 0) + ' de l\'abonnement' + (c.credits_achetes ? ' et ' + c.credits_achetes + ' achetés' : '') + '</span>' : '') + '</div>' +
        '<div><small>Formule</small><b>' + (c.illimite ? 'Démonstration' : plan || 'À l\'unité') + '</b><span>' + esc(c.illimite ? 'Rapports illimités, sans décompte' : status) + '</span></div>' +
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
        var m = { trop_essais:'Trop de tentatives. Réessayez dans une heure.', deja_utilise:'Ce lien d\'essai a déjà été utilisé.', deja_utilise_par_vous:'Vous avez déjà utilisé ce lien : votre rapport offert est dans votre solde.', expire:'Ce lien d\'essai a expiré.', code:'Ce lien d\'essai n\'est pas valide.' }[e && e.code] || 'Le lien n\'a pas pu être validé. Réessayez dans un instant.';
        essai.innerHTML = '<p class="empty">' + m + ' <a href="/tarifs.html">Voir les offres</a></p>';
      });
    });
  }

  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]; }); }
})();
