/* TerrenUrbanisme — annuaire des professionnels (fiches, recherche, demandes de contact) */
(function(){
  'use strict';
  var A = window.TUAuth, sb = A && A.client;
  if (!sb) return;
  var $ = function(id){ return document.getElementById(id); };
  var esc = function(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); };
  var METIERS = { agent_immobilier:'Agent immobilier', architecte:'Architecte', geometre:'Géomètre-expert', notaire:'Notaire', diagnostiqueur:'Diagnostiqueur', promoteur:'Promoteur', constructeur:'Constructeur de maisons', autre:'Autre professionnel' };
  var DEPS = [['01','Ain'],['02','Aisne'],['03','Allier'],['04','Alpes-de-Haute-Provence'],['05','Hautes-Alpes'],['06','Alpes-Maritimes'],['07','Ardèche'],['08','Ardennes'],['09','Ariège'],['10','Aube'],['11','Aude'],['12','Aveyron'],['13','Bouches-du-Rhône'],['14','Calvados'],['15','Cantal'],['16','Charente'],['17','Charente-Maritime'],['18','Cher'],['19','Corrèze'],['2A','Corse-du-Sud'],['2B','Haute-Corse'],['21',"Côte-d'Or"],['22',"Côtes-d'Armor"],['23','Creuse'],['24','Dordogne'],['25','Doubs'],['26','Drôme'],['27','Eure'],['28','Eure-et-Loir'],['29','Finistère'],['30','Gard'],['31','Haute-Garonne'],['32','Gers'],['33','Gironde'],['34','Hérault'],['35','Ille-et-Vilaine'],['36','Indre'],['37','Indre-et-Loire'],['38','Isère'],['39','Jura'],['40','Landes'],['41','Loir-et-Cher'],['42','Loire'],['43','Haute-Loire'],['44','Loire-Atlantique'],['45','Loiret'],['46','Lot'],['47','Lot-et-Garonne'],['48','Lozère'],['49','Maine-et-Loire'],['50','Manche'],['51','Marne'],['52','Haute-Marne'],['53','Mayenne'],['54','Meurthe-et-Moselle'],['55','Meuse'],['56','Morbihan'],['57','Moselle'],['58','Nièvre'],['59','Nord'],['60','Oise'],['61','Orne'],['62','Pas-de-Calais'],['63','Puy-de-Dôme'],['64','Pyrénées-Atlantiques'],['65','Hautes-Pyrénées'],['66','Pyrénées-Orientales'],['67','Bas-Rhin'],['68','Haut-Rhin'],['69','Rhône'],['70','Haute-Saône'],['71','Saône-et-Loire'],['72','Sarthe'],['73','Savoie'],['74','Haute-Savoie'],['75','Paris'],['76','Seine-Maritime'],['77','Seine-et-Marne'],['78','Yvelines'],['79','Deux-Sèvres'],['80','Somme'],['81','Tarn'],['82','Tarn-et-Garonne'],['83','Var'],['84','Vaucluse'],['85','Vendée'],['86','Vienne'],['87','Haute-Vienne'],['88','Vosges'],['89','Yonne'],['90','Territoire de Belfort'],['91','Essonne'],['92','Hauts-de-Seine'],['93','Seine-Saint-Denis'],['94','Val-de-Marne'],['95',"Val-d'Oise"],['971','Guadeloupe'],['972','Martinique'],['973','Guyane'],['974','La Réunion'],['976','Mayotte']];
  var DEPNAME = {}; DEPS.forEach(function(d){ DEPNAME[d[0]] = d[1]; });
  function depOf(insee){ insee = String(insee || '').toUpperCase(); return /^97/.test(insee) ? insee.slice(0, 3) : insee.slice(0, 2); }
  function list(dep, metier, limit){ return sb.rpc('pros_publics', { p_dep: dep || null, p_metier: metier || null, p_limit: limit || 60 }).then(function(r){ return r.data || []; }); }

  function card(p, ctx){
    var deps = (p.departements || []).slice(0, 4).map(function(d){ return DEPNAME[d] || d; }).join(', ') + ((p.departements || []).length > 4 ? '…' : '');
    var site = p.site ? '<a href="' + esc(p.site) + '" target="_blank" rel="noopener nofollow">Site web</a>' : '';
    var tel = p.telephone ? '<span>' + esc(p.telephone) + '</span>' : '';
    return '<article class="pro-card' + (p.partenaire ? ' is-partner' : '') + '" id="pro-' + esc(p.id) + '">' +
      '<div class="pro-top"><span class="pro-metier">' + esc(METIERS[p.metier] || p.metier) + '</span>' + (p.partenaire ? '<span class="pro-badge">Partenaire TerrenUrbanisme</span>' : '') + '</div>' +
      '<h3>' + esc(p.nom) + '</h3>' +
      '<p class="pro-loc">' + esc(p.ville ? p.ville + ' · ' : '') + esc(deps) + '</p>' +
      (p.description ? '<p class="pro-desc">' + esc(p.description) + '</p>' : '') +
      '<div class="pro-foot">' + tel + site + '<button type="button" class="btn pro-contact" data-id="' + esc(p.id) + '" data-nom="' + esc(p.nom) + '">Être recontacté</button></div></article>';
  }
  function wire(root, ctx){
    root.querySelectorAll('.pro-contact').forEach(function(b){ b.addEventListener('click', function(){ openContact(b.getAttribute('data-id'), b.getAttribute('data-nom'), ctx); }); });
  }

  /* Fenêtre « Être recontacté » : réservée aux visiteurs connectés (limite les abus) */
  function openContact(id, nom, ctx){
    A.user().then(function(u){
      if (!u){ location.href = A.loginUrl(location.pathname + location.search + '#pro-' + id); return; }
      var ov = document.createElement('div'); ov.className = 'pro-modal'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true');
      var msg = 'Bonjour, je souhaite être recontacté au sujet d\'un projet' + (ctx && ctx.commune ? ' à ' + ctx.commune : '') + '.';
      ov.innerHTML = '<form class="pro-box" novalidate><button type="button" class="pro-x" aria-label="Fermer">×</button><h3>Être recontacté par ' + esc(nom) + '</h3>' +
        '<label class="field"><span>Nom et prénom</span><input id="pc-nom" required maxlength="100" autocomplete="name"></label>' +
        '<label class="field"><span>E-mail</span><input id="pc-mail" type="email" required maxlength="160" autocomplete="email"></label>' +
        '<label class="field"><span>Téléphone (facultatif)</span><input id="pc-tel" maxlength="30" autocomplete="tel"></label>' +
        '<label class="field"><span>Votre projet</span><textarea id="pc-msg" required maxlength="1000" rows="4"></textarea></label>' +
        '<p class="fine">Vos coordonnées sont transmises uniquement à ce professionnel, pour qu\'il vous recontacte.</p>' +
        '<button class="btn" type="submit">Envoyer ma demande</button><p class="err" id="pc-err" role="alert"></p></form>';
      document.body.appendChild(ov);
      $('pc-mail').value = u.email || ''; $('pc-msg').value = msg; $('pc-nom').focus();
      var close = function(){ ov.remove(); };
      ov.querySelector('.pro-x').addEventListener('click', close);
      ov.addEventListener('click', function(e){ if (e.target === ov) close(); });
      ov.querySelector('form').addEventListener('submit', function(e){
        e.preventDefault();
        var nomv = $('pc-nom').value.trim(), mail = $('pc-mail').value.trim(), m = $('pc-msg').value.trim(), err = $('pc-err');
        if (nomv.length < 2 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail) || m.length < 5){ err.textContent = 'Indiquez votre nom, un e-mail valide et quelques mots sur votre projet.'; return; }
        var btn = ov.querySelector('button[type=submit]'); btn.disabled = true; btn.textContent = 'Envoi…';
        sb.from('demandes_pro').insert({ pro_id: id, user_id: u.id, nom: nomv, email: mail, telephone: $('pc-tel').value.trim() || null, message: m, insee: ctx && ctx.insee || null, commune: ctx && ctx.commune || null }).then(function(r){
          if (r.error){ btn.disabled = false; btn.textContent = 'Envoyer ma demande'; err.textContent = /Limite/.test(r.error.message) ? 'Vous avez atteint la limite de 5 demandes par jour.' : 'L\'envoi a échoué. Réessayez dans un instant.'; return; }
          ov.querySelector('form').innerHTML = '<button type="button" class="pro-x" aria-label="Fermer">×</button><h3>Demande envoyée</h3><p>' + esc(nom) + ' reçoit votre demande par e-mail et vous recontactera directement.</p>';
          ov.querySelector('.pro-x').addEventListener('click', close);
        });
      });
    });
  }

  /* Bloc sur les pages communes */
  var cp = $('commune-page');
  if (cp && cp.getAttribute('data-insee')){
    var insee = cp.getAttribute('data-insee'), nom = cp.getAttribute('data-nom') || '', dep = depOf(insee);
    var anchor = document.querySelector('[data-pro-links]');
    var sec = document.createElement('section'); sec.className = 'sec tight pro-sec';
    sec.innerHTML = '<div class="wrap"><div class="pro-head"><div><h2>Professionnels près de ' + esc(nom) + '</h2><p class="lede">Géomètres, architectes, agents immobiliers et notaires qui interviennent dans le secteur.</p></div><a class="btn ghost" href="/professionnels.html?dep=' + esc(dep) + '&insee=' + esc(insee) + '">Voir l\'annuaire</a></div><div class="pro-grid" id="pro-grid"></div></div>';
    if (anchor) anchor.parentNode.insertBefore(sec, anchor); else (document.querySelector('main') || document.body).appendChild(sec);
    list(dep, null, 6).then(function(rows){
      var g = $('pro-grid');
      if (!rows.length){ g.innerHTML = '<div class="pro-empty"><b>Vous êtes professionnel à ' + esc(nom) + ' ?</b><span>Soyez le premier référencé dans ce secteur et recevez les demandes des propriétaires qui vérifient leur terrain.</span><a class="btn" href="/referencer-mon-cabinet.html">Référencer mon cabinet gratuitement</a></div>'; return; }
      g.innerHTML = rows.map(function(p){ return card(p); }).join('') + '<div class="pro-empty slim"><span>Vous êtes professionnel dans ce secteur ?</span><a href="/referencer-mon-cabinet.html">Référencez votre cabinet gratuitement</a></div>';
      wire(g, { insee: insee, commune: nom });
    });
  }

  /* Page annuaire */
  var an = $('annuaire');
  if (an){
    var qs = new URLSearchParams(location.search), fd = $('an-dep'), fm = $('an-metier'), res = $('an-res');
    fd.innerHTML = '<option value="">Tous les départements</option>' + DEPS.map(function(d){ return '<option value="' + d[0] + '">' + d[0] + ' · ' + esc(d[1]) + '</option>'; }).join('');
    fm.innerHTML = '<option value="">Tous les métiers</option>' + Object.keys(METIERS).map(function(k){ return '<option value="' + k + '">' + esc(METIERS[k]) + '</option>'; }).join('');
    var ctx = { insee: qs.get('insee') || null, commune: null };
    fd.value = qs.get('dep') || (ctx.insee ? depOf(ctx.insee) : ''); fm.value = qs.get('metier') || '';
    var run = function(){
      res.innerHTML = '<p class="empty">Recherche…</p>';
      var u = new URL(location.href); fd.value ? u.searchParams.set('dep', fd.value) : u.searchParams.delete('dep'); fm.value ? u.searchParams.set('metier', fm.value) : u.searchParams.delete('metier'); history.replaceState(null, '', u.pathname + u.search + location.hash);
      list(fd.value, fm.value, 100).then(function(rows){
        if (!rows.length){ res.innerHTML = '<div class="pro-empty"><b>Aucun professionnel référencé pour cette recherche pour l\'instant.</b><span>L\'annuaire s\'enrichit chaque semaine. Vous êtes professionnel ? Votre fiche est gratuite.</span><a class="btn" href="/referencer-mon-cabinet.html">Référencer mon cabinet</a></div>'; return; }
        res.innerHTML = '<div class="pro-grid">' + rows.map(function(p){ return card(p); }).join('') + '</div>';
        wire(res, ctx);
        if (location.hash){ var t = document.querySelector(location.hash.replace(/[^#\w-]/g, '')); if (t) t.scrollIntoView({ block: 'center' }); }
      });
    };
    fd.addEventListener('change', run); fm.addEventListener('change', run); run();
  }

  /* Page d'inscription des professionnels */
  var pf = $('pro-form');
  if (pf){
    A.user().then(function(u){
      if (!u){ $('pro-login').hidden = false; pf.hidden = true; $('pro-login-btn').href = A.loginUrl('/referencer-mon-cabinet.html'); return; }
      var box = $('pf-deps'), filt = $('pf-depfilter');
      box.innerHTML = DEPS.map(function(d){ return '<label class="pf-dep"><input type="checkbox" value="' + d[0] + '"><span>' + d[0] + ' · ' + esc(d[1]) + '</span></label>'; }).join('');
      $('pf-metier').innerHTML = Object.keys(METIERS).map(function(k){ return '<option value="' + k + '">' + esc(METIERS[k]) + '</option>'; }).join('');
      filt.addEventListener('input', function(){ var q = filt.value.trim().toLowerCase(); box.querySelectorAll('.pf-dep').forEach(function(l){ l.hidden = q && l.textContent.toLowerCase().indexOf(q) < 0; }); });
      $('pf-email').value = u.email || '';
      var existing = null;
      sb.from('pros').select('*').eq('user_id', u.id).maybeSingle().then(function(r){
        var p = r.data; if (!p) return; existing = p;
        $('pf-nom').value = p.nom || ''; $('pf-metier').value = p.metier; $('pf-ville').value = p.ville || ''; $('pf-tel').value = p.telephone || ''; $('pf-email').value = p.email || ''; $('pf-site').value = p.site || ''; $('pf-desc').value = p.description || ''; $('pf-publie').checked = p.publie;
        (p.departements || []).forEach(function(d){ var c = box.querySelector('input[value="' + d + '"]'); if (c) c.checked = true; });
        $('pf-consent').checked = true; $('pf-submit').textContent = 'Mettre à jour ma fiche'; $('pf-view').hidden = false;
      });
      pf.addEventListener('submit', function(e){
        e.preventDefault();
        var err = $('pf-err'), deps = [].map.call(box.querySelectorAll('input:checked'), function(c){ return c.value; });
        var site = $('pf-site').value.trim(); if (site && !/^https?:\/\//i.test(site)) site = 'https://' + site;
        var row = { user_id: u.id, nom: $('pf-nom').value.trim(), metier: $('pf-metier').value, ville: $('pf-ville').value.trim() || null, departements: deps, telephone: $('pf-tel').value.trim() || null, email: $('pf-email').value.trim(), site: site || null, description: $('pf-desc').value.trim() || null, publie: $('pf-publie').checked };
        if (row.nom.length < 2){ err.textContent = 'Indiquez le nom de votre cabinet ou de votre agence.'; return; }
        if (!deps.length || deps.length > 20){ err.textContent = 'Sélectionnez entre 1 et 20 départements d\'intervention.'; return; }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(row.email)){ err.textContent = 'Indiquez l\'e-mail où recevoir les demandes de contact.'; return; }
        if (!$('pf-consent').checked){ err.textContent = 'Merci d\'accepter la publication de votre fiche.'; return; }
        err.textContent = ''; var b = $('pf-submit'); b.disabled = true;
        (existing ? sb.from('pros').update(row).eq('user_id', u.id).select().single() : sb.from('pros').insert(row).select().single()).then(function(r){
          b.disabled = false;
          if (r.error){ err.textContent = 'L\'enregistrement a échoué. Vérifiez les champs et réessayez.'; return; }
          existing = r.data; b.textContent = 'Mettre à jour ma fiche'; $('pf-view').hidden = false;
          $('pf-ok').hidden = false; $('pf-ok').scrollIntoView({ block: 'center' });
        });
      });
    });
  }
})();
