/* TerrenUrbanisme — scripts du site */
(function(){
  'use strict';
  var $ = function(id){ return document.getElementById(id); };
  var CARTO = 'https://apicarto.ign.fr/api';
  var GEO = 'https://geo.api.gouv.fr';
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]; }); }
  function norm(s){ return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[-']/g,' ').replace(/\s+/g,' ').trim(); }
  function getJSON(url){ return fetch(url).then(function(r){ if (!r.ok) throw new Error('http '+r.status); return r.json(); }); }
  function fmt(n){ return Number(n||0).toLocaleString('fr-FR'); }
  function slug(s){ return norm(s).replace(/ /g,'-'); }

  /* Menu mobile */
  var burger = document.querySelector('.burger'), menu = document.querySelector('.menu');
  if (burger && menu) burger.addEventListener('click', function(){
    var open = menu.classList.toggle('open'); burger.setAttribute('aria-expanded', open);
  });

  /* Communes de Corse (chargées une fois) */
  var communesP = null;
  function loadCommunes(){
    if (!communesP) communesP = Promise.all(['2A','2B'].map(function(d){
      return getJSON(GEO+'/departements/'+d+'/communes?fields=nom,code,codesPostaux,population');
    })).then(function(l){ return { '2A':l[0], '2B':l[1] }; });
    return communesP;
  }
  function communeIndex(){ return Promise.resolve({}); }
  /* Communes de France : recherche à la volée (geo.api.gouv.fr) */
  var INSEE_RE = /^(?:\d{2}|2[AB])\d{3}$/;
  var comMap = {};
  function comLabel(c){ return c.nom + ' (' + c.codeDepartement + ')'; }
  function searchCommunes(q, limit){
    return getJSON(GEO+'/communes?nom='+encodeURIComponent(q)+'&fields=nom,code,codeDepartement,population&boost=population&limit='+(limit||8))
      .then(function(l){ (l||[]).forEach(function(c){ comMap[norm(comLabel(c))] = c.code; }); return l || []; });
  }
  function resolveCommune(val){
    var v = String(val||'').trim(); if (!v) return Promise.resolve(null);
    if (INSEE_RE.test(v.toUpperCase())) return Promise.resolve(v.toUpperCase());
    if (comMap[norm(v)]) return Promise.resolve(comMap[norm(v)]);
    var m = v.match(/^(.*?)\s*\(([0-9AB]{2,3})\)\s*$/i), name = m ? m[1] : v, dep = m ? m[2].toUpperCase() : null;
    return searchCommunes(name, 20).then(function(l){
      var ex = l.filter(function(c){ return norm(c.nom) === norm(name) && (!dep || c.codeDepartement === dep); });
      var c = ex[0] || (dep ? l.filter(function(c){ return c.codeDepartement === dep; })[0] : null) || (l.length === 1 ? l[0] : null);
      return c ? c.code : null;
    });
  }
  function bindCommuneInput(input, dl){
    if (!input || !dl) return; var t = null;
    input.addEventListener('input', function(){
      clearTimeout(t); var q = input.value.trim();
      if (q.length < 2 || /\(\w{2,3}\)$/.test(q)) return;
      t = setTimeout(function(){
        searchCommunes(q, 8).then(function(l){ dl.innerHTML = l.map(function(c){ return '<option value="'+esc(comLabel(c))+'">'; }).join(''); }).catch(function(){});
      }, 180);
    });
  }

  /* ---------- Formulaire de recherche ---------- */
  var form = $('recherche');
  if (form) initSearch();

  function initSearch(){
    var mode = 'cad', picked = null, idx = {};
    var errEl = $('err'), goBtn = $('go'), goLabel = goBtn.textContent;
    var inPlace = !!$('scope');

    function setMode(m){
      mode = m;
      $('tab-cad').setAttribute('aria-selected', m === 'cad');
      $('tab-adr').setAttribute('aria-selected', m === 'adr');
      $('pane-cad').hidden = m !== 'cad';
      $('pane-adr').hidden = m !== 'adr';
      errEl.textContent = '';
    }
    $('tab-cad').addEventListener('click', function(){ setMode('cad'); });
    $('tab-adr').addEventListener('click', function(){ setMode('adr'); });

    bindCommuneInput($('com'), $('communes'));

    /* Autocomplétion d'adresse */
    var adr = $('adr'), list = $('adr-list'), timer = null, items = [], active = -1;
    function closeList(){ list.hidden = true; active = -1; adr.removeAttribute('aria-activedescendant'); }
    function renderList(){
      if (!items.length){ closeList(); return; }
      list.innerHTML = items.map(function(f,i){ var p = f.properties;
        return '<li role="option" id="opt-'+i+'" aria-selected="'+(i===active)+'">'+esc(p.name)+' <small>'+esc(p.postcode+' '+p.city)+'</small></li>'; }).join('');
      list.hidden = false;
    }
    adr.addEventListener('input', function(){
      picked = null; clearTimeout(timer);
      var q = adr.value.trim();
      if (q.length < 4){ items = []; closeList(); return; }
      timer = setTimeout(function(){
        getJSON('https://api-adresse.data.gouv.fr/search/?q='+encodeURIComponent(q)+'&limit=6').then(function(j){
          items = (j.features||[]).slice(0,6);
          active = -1; renderList();
        }).catch(function(){});
      }, 220);
    });
    adr.addEventListener('keydown', function(e){
      if (list.hidden) return;
      if (e.key === 'ArrowDown'){ e.preventDefault(); active = Math.min(active+1, items.length-1); renderList(); adr.setAttribute('aria-activedescendant','opt-'+active); }
      else if (e.key === 'ArrowUp'){ e.preventDefault(); active = Math.max(active-1,0); renderList(); adr.setAttribute('aria-activedescendant','opt-'+active); }
      else if (e.key === 'Enter' && active >= 0){ e.preventDefault(); choose(active); }
      else if (e.key === 'Escape'){ closeList(); }
    });
    list.addEventListener('mousedown', function(e){ var li = e.target.closest('li'); if (!li) return; e.preventDefault(); choose(+li.id.split('-')[1]); });
    adr.addEventListener('blur', function(){ setTimeout(closeList, 120); });
    function choose(i){ picked = items[i]; adr.value = picked.properties.label; closeList(); }

    form.addEventListener('submit', function(e){
      e.preventDefault(); errEl.textContent = '';
      if (mode === 'adr'){
        if (!picked && items.length) picked = items[0];
        if (!picked){ errEl.textContent = 'Choisissez une adresse dans la liste.'; return; }
        var c = picked.geometry.coordinates;
        if (!inPlace){ location.href = '/?lon='+c[0]+'&lat='+c[1]+'&adresse='+encodeURIComponent(picked.properties.label)+'#recherche'; return; }
        gate('/?lon='+c[0]+'&lat='+c[1]+'&adresse='+encodeURIComponent(picked.properties.label), function(){
          analyse(CARTO+'/cadastre/parcelle?geom='+encodeURIComponent(JSON.stringify({ type:'Point', coordinates:c })), { lon:c[0], lat:c[1], label:picked.properties.label });
        });
      } else {
        var comVal = $('com').value;
        var sec = $('sec').value.trim().toUpperCase().replace(/[^0-9A-Z]/g,'');
        var num = $('num').value.trim().replace(/\D/g,'');
        if (!sec || !num){ errEl.textContent = 'Indiquez la section (une ou deux lettres) et le numéro de la parcelle.'; return; }
        resolveCommune(comVal).then(function(code){
        if (!code){ errEl.textContent = 'Commune introuvable. Choisissez la commune dans la liste proposée.'; return; }
        if (!inPlace){ location.href = '/?commune='+encodeURIComponent(comVal)+'&section='+sec+'&numero='+num+'#recherche'; return; }
        var back = '/?commune='+encodeURIComponent(comVal)+'&section='+sec+'&numero='+num;
        if (sec.length === 1) sec = '0'+sec;
        while (num.length < 4) num = '0'+num;
        gate(back, function(){ analyse(CARTO+'/cadastre/parcelle?code_insee='+code+'&section='+sec+'&numero='+num); });
        }).catch(function(){ errEl.textContent = 'Le service est momentanément indisponible. Réessayez dans un instant.'; });
      }
    });

    /* Paramètres d'URL : préremplissage et lancement automatique */
    var qs = new URLSearchParams(location.search);
    if (qs.get('commune')){
      setMode('cad'); $('com').value = qs.get('commune');
      if (qs.get('section')) $('sec').value = qs.get('section');
      if (qs.get('numero')) $('num').value = qs.get('numero');
      if (inPlace && qs.get('section') && qs.get('numero')) communeIndex().then(function(i){ idx = i; form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit')); });
    } else if (qs.get('lon') && qs.get('lat') && inPlace){
      setMode('adr'); adr.value = qs.get('adresse') || '';
      picked = { properties:{ label:adr.value }, geometry:{ coordinates:[+qs.get('lon'), +qs.get('lat')] } };
      setTimeout(function(){ form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit')); }, 50);
    }

    /* La recherche est libre : la connexion n'est demandée qu'au moment de l'achat */
    function gate(back, go){ go(); }
    function analyse(url, addr){
      openBig();
      goBtn.disabled = true; goBtn.textContent = 'Recherche en cours…';
      if (addr) pickAddress(addr);
      runAnalysis(url, !!addr).catch(function(e){
        if (addr) return; // adresse : l'utilisateur choisit sa parcelle sur la carte
        var msg = (e && e.user) || 'Le cadastre n\'a pas répondu. Réessayez dans quelques instants.';
        errEl.textContent = msg; panelMsg(msg);
        if (!(e && e.user)) console.error(e);
      }).then(function(){ goBtn.disabled = false; goBtn.textContent = goLabel; });
    }
  }

  /* ---------- Carte du héros ---------- */
  var map = null, layer = null, scope = $('scope');
  var small = function(){ return window.innerWidth <= 620; };
  if (scope && window.L){
    try {
      map = L.map('map', { zoomControl:false, scrollWheelZoom:false, dragging:true, tap:true, attributionControl:true, maxZoom:20 }).setView([41.5265, 9.2640], 15);
      L.tileLayer('https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/jpeg',
        { maxZoom:19, attribution:'Photographies aériennes © IGN' }).addTo(map);
      L.tileLayer.wms('https://data.geopf.fr/wms-r/wms', { layers:'CADASTRALPARCELS.PARCELLAIRE_EXPRESS', format:'image/png', transparent:true, version:'1.3.0', minZoom:16, maxZoom:20, opacity:.9 }).addTo(map);
      L.control.zoom({ position:'topright' }).addTo(map);
      var hint = scope.querySelector('.hint span');
      var setHint = function(){ if (hint) hint.textContent = map.getZoom() >= 16 ? 'Cliquez sur votre parcelle pour la sélectionner.' : 'Zoomez sur votre terrain, puis cliquez sur la parcelle.'; };
      map.on('zoomend', setHint); setHint();
      /* Sélection d'une parcelle directement sur la carte du héros */
      map.on('click', function(ev){
        if (map.getZoom() < 16){ map.setView(ev.latlng, Math.min(map.getZoom() + 3, 18)); return; }
        var c = [ +ev.latlng.lng.toFixed(6), +ev.latlng.lat.toFixed(6) ];
        if (hint) hint.textContent = 'Recherche de la parcelle…';
        openBig();
        if (big) big.setView(ev.latlng, 18);
        panelMsg('Recherche de la parcelle…', true);
        runAnalysis(CARTO+'/cadastre/parcelle?geom='+encodeURIComponent(JSON.stringify({ type:'Point', coordinates:c }))).catch(function(e){
          panelMsg((e && e.user) || 'Le cadastre n\'a pas répondu. Cliquez à nouveau dans un instant.');
        }).then(setHint);
      });
    } catch(e){}
  }

  /* ---------- Grande carte de sélection ---------- */
  var big = null, blayer = null, bmarker = null, rsec = $('resultat');
  function openBig(){
    if (!rsec) return;
    rsec.hidden = false;
    if (!big && window.L){
      big = L.map('bigmap', { zoomControl:false, scrollWheelZoom:true, maxZoom:20 }).setView([46.6, 2.4], 6);
      L.tileLayer('https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/jpeg', { maxZoom:20, maxNativeZoom:19, attribution:'Photographies aériennes et cadastre © IGN' }).addTo(big);
      L.tileLayer.wms('https://data.geopf.fr/wms-r/wms', { layers:'CADASTRALPARCELS.PARCELLAIRE_EXPRESS', format:'image/png', transparent:true, version:'1.3.0', minZoom:15, maxZoom:20, opacity:.9 }).addTo(big);
      L.control.zoom({ position:'topright' }).addTo(big);
      big.on('click', function(ev){
        var c = [ +ev.latlng.lng.toFixed(6), +ev.latlng.lat.toFixed(6) ];
        if (big.getZoom() < 16){ big.setView(ev.latlng, 18); panelMsg('Zoomez encore puis cliquez sur votre parcelle.'); return; }
        panelMsg('Recherche de la parcelle…', true);
        runAnalysis(CARTO+'/cadastre/parcelle?geom='+encodeURIComponent(JSON.stringify({ type:'Point', coordinates:c }))).catch(function(e){
          panelMsg((e && e.user) || 'Le cadastre n\'a pas répondu. Cliquez à nouveau dans un instant.');
          if (!(e && e.user)) console.error(e);
        });
      });
    }
    setTimeout(function(){ if (big) big.invalidateSize(); rsec.scrollIntoView({ behavior:'smooth', block:'start' }); }, 60);
  }
  function panelMsg(t, wait){
    var r = $('result'); if (!r) return;
    r.innerHTML = '<div class="v-title" style="font-size:18px">' + (wait ? '<span class="spin"></span>' : '') + esc(t) + '</div>';
  }
  function pickAddress(a){
    if (!big) return;
    big.setView([a.lat, a.lon], 19);
    if (bmarker) big.removeLayer(bmarker);
    bmarker = L.circleMarker([a.lat, a.lon], { radius:7, color:'#fff', weight:2, fillColor:'#A3462C', fillOpacity:1 }).addTo(big);
    var r = $('result');
    r.innerHTML = '<div class="v-ref">' + esc(a.label) + '</div><div class="v-title">Sélectionnez votre terrain</div><p class="v-why">Cliquez sur la parcelle qui vous intéresse, sur la carte. Les limites cadastrales sont affichées en surimpression.</p>';
    var tip = $('rs-tip'); if (tip) tip.hidden = false;
  }

  function roundGeom(g){
    function r(a){ return typeof a[0] === 'number' ? [ +a[0].toFixed(6), +a[1].toFixed(6) ] : a.map(r); }
    return { type:g.type, coordinates:r(g.coordinates) };
  }
  function runAnalysis(parcelUrl, fromAddress){
    return getJSON(parcelUrl).then(function(pj){
      var parcel = pj.features && pj.features[0];
      if (!parcel) throw { user: fromAddress ? 'Cliquez sur votre parcelle sur la carte.' : 'Aucune parcelle à cet endroit. Cliquez à l\'intérieur d\'une parcelle délimitée.' };
      var insee = parcel.properties.code_insee;
      var g = roundGeom(parcel.geometry), q = JSON.stringify(g);
      if (q.length > 6000 && window.turf){ g = roundGeom(turf.simplify(turf.feature(g), { tolerance:0.00002, highQuality:true }).geometry); q = JSON.stringify(g); }
      return getJSON(CARTO+'/gpu/municipality?insee='+insee).catch(function(){ return { features:[] }; })
        .then(function(res){ show(parcel, [], (res.features && res.features[0] || {}).properties || {}); });
    });
  }

  var V = {
    ok:   { cls:'v-ok',   word:'Constructible',     title:'Le PLU autorise la construction',       color:'#2E7D4F' },
    cond: { cls:'v-cond', word:'Sous conditions',   title:'Construction possible sous conditions', color:'#C27C12' },
    non:  { cls:'v-non',  word:'Non constructible', title:'Le PLU ne permet pas de construire',     color:'#B3402F' }
  };
  function classify(tz){
    tz = (tz||'').toUpperCase();
    if (tz === 'U') return { v:'ok', why:'zone urbaine' };
    if (tz === 'AUC') return { v:'cond', why:'zone à urbaniser ouverte' };
    if (tz === 'AUS') return { v:'non', why:'zone à urbaniser fermée' };
    if (tz.charAt(0) === 'A' && tz.indexOf('AU') !== 0) return { v:'non', why:'zone agricole' };
    if (tz.charAt(0) === 'N') return { v:'non', why:'zone naturelle' };
    return { v:'cond', why:'zone à préciser' };
  }
  var ICON = {
    info:'<svg viewBox="0 0 24 24" fill="none" stroke="#6E625A" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>',
    warn:'<svg viewBox="0 0 24 24" fill="none" stroke="#C27C12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/></svg>'
  };

  var LOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="#A3462C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>';
  var OKI = '<svg viewBox="0 0 24 24" fill="none" stroke="#2E7D4F" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';
  function show(parcel, zones, muni){
    var resultEl = $('result');
    var p = parcel.properties;
    var sec = String(p.section).replace(/^0/,''), num = String(p.numero).replace(/^0+/,'');
    var ref = (p.nom_com||'') + ' · section ' + sec + ' · n° ' + num;
    var found = [
      ['ok', 'Parcelle identifiée au cadastre', fmt(p.contenance) + ' m² · ' + (p.idu || '')],
      ['ok', 'Document d\'urbanisme', muni.is_rnu ? 'Règlement national d\'urbanisme' : 'Document local publié'],
      ['ok', 'Loi Littoral', muni.is_coastline ? 'Commune littorale' : 'Commune non littorale']
    ];
    var locked = ['Verdict : constructible ou non, et pourquoi', 'Zones du PLU, secteur exact et plan de zonage', 'Règlement de la zone : hauteur, reculs, aspect, avec extraits', 'Surface constructible estimée en m² et plan d\'implantation', (/^2[AB]/.test(String(parcel && parcel.properties && parcel.properties.code_insee || '')) ? 'PADDUC, distance au rivage, loi Montagne' : 'Loi Littoral, distance au rivage, loi Montagne'), 'Risques à la parcelle, arrêtés de catastrophe naturelle', 'Accès, pente, assainissement et fibre', 'Photos aériennes depuis 1950 et permis accordés autour', 'Ventes de maisons, appartements et terrains à 10 km', 'Démarches, délais et interlocuteurs'];
    var BTN = 'Obtenir le rapport complet · 12,90 €';
    resultEl.innerHTML =
      '<div class="v-ref">' + esc(ref) + '</div>' +
      '<span class="v-badge v-found"><i></i>Parcelle trouvée</span>' +
      '<div class="v-title">Votre rapport est prêt à être établi</div>' +
      '<p class="v-other">Ce n\'est pas la bonne parcelle ? Cliquez sur une autre parcelle de la carte.</p>' +
      '<p class="v-why">Nous avons trouvé cette parcelle et les sources officielles qui la concernent. Le rapport complet répond à la question : peut-on construire, et à quelles conditions ?</p>' +
      '<button type="button" class="v-cta v-cta-top buy">' + BTN + '</button><p class="v-buy-err" role="alert"></p>' +
      '<ul class="v-found-list">' + found.map(function(f){ return '<li>' + OKI + '<div><strong>' + esc(f[1]) + '</strong><span>' + esc(f[2]) + '</span></div></li>'; }).join('') + '</ul>' +
      '<ul class="v-locked">' + locked.map(function(t){ return '<li>' + LOCK + '<span>' + esc(t) + '</span><i class="blur" aria-hidden="true">████████</i></li>'; }).join('') + '</ul>' +
      '<button type="button" class="v-cta buy">' + BTN + '</button>' +
      '<p class="v-buy-note">Rapport PDF de 30 à 40 pages avec sommaire cliquable, envoyé par e-mail en quelques minutes · paiement sécurisé par Stripe<br><a href="/tarifs.html">Plusieurs terrains ? Abonnements dès 0,86 € le rapport</a> · <a href="/exemple.html">Voir un exemple</a></p><p class="v-buy-err" role="alert"></p>' +
      '<a class="v-owner" href="https://france-cadastre.fr/" target="_blank" rel="noopener">Connaître le propriétaire de cette parcelle <span>via France Cadastre ↗</span></a>';
    var parcelRef = { insee:p.code_insee, commune:p.nom_com, section:sec, numero:num };
    var buys = resultEl.querySelectorAll('.buy'), errs = resultEl.querySelectorAll('.v-buy-err'), A = window.TUAuth, credits = 0, label = BTN;
    function setAll(t, dis){ buys.forEach(function(x){ x.disabled = !!dis; x.textContent = t; }); }
    if (A && A.ready) A.account().then(function(c){
      credits = c ? c.total : 0;
      if (credits > 0){ label = 'Générer le rapport complet · 1 rapport (solde : ' + credits + ')'; setAll(label); }
    });
    buys.forEach(function(btn, k){ btn.addEventListener('click', function(){
      var err = errs[k] || errs[0];
      errs.forEach(function(e){ e.textContent = ''; });
      if (!A || !A.ready){ err.textContent = 'Le paiement n\'est pas encore activé.'; return; }
      setAll(credits > 0 ? 'Génération du rapport…' : 'Redirection vers le paiement…', true);
      A.user().then(function(u){
        if (!u){ location.href = A.loginUrl('/?commune=' + encodeURIComponent(p.nom_com) + '&section=' + encodeURIComponent(sec) + '&numero=' + encodeURIComponent(num)); return; }
        return credits > 0 ? A.generate(parcelRef) : A.checkout('unit', parcelRef);
      }).catch(function(e){
        err.textContent = e && e.code === 'solde' ? 'Votre solde de rapports est épuisé.' : 'L\'opération n\'a pas pu aboutir. Réessayez dans un instant.';
        if (e && e.code === 'solde') { credits = 0; label = BTN; }
        setAll(label, false);
      });
    }); });
    if (window.TUAuth) window.TUAuth.saveDiagnostic({ insee:p.code_insee, commune:p.nom_com, section:sec, numero:num, verdict:null, zone:null });
    var tip = $('rs-tip'); if (tip) tip.hidden = true;
    if (big){
      if (blayer) big.removeLayer(blayer);
      if (bmarker){ big.removeLayer(bmarker); bmarker = null; }
      blayer = L.geoJSON(parcel, { style:{ color:'#FFD27A', weight:3.5, fillColor:'#FFD27A', fillOpacity:.22 } }).addTo(big);
      big.fitBounds(blayer.getBounds(), { padding:[60,60], maxZoom:19 });
    }
  }
  window.TU = { show:show };

  /* ---------- Page : liste des communes ---------- */
  var listEl = $('communes-list');
  if (listEl){
    if (!listEl.querySelector('li')) loadCommunes().then(function(d){
      var html = '';
      [['2A','Corse-du-Sud'],['2B','Haute-Corse']].forEach(function(dep){
        var arr = d[dep[0]].slice().sort(function(a,b){ return a.nom.localeCompare(b.nom,'fr'); });
        html += '<section class="dept" data-dept="'+dep[0]+'"><h2>'+dep[1]+' ('+dep[0]+') · '+arr.length+' communes</h2><ul class="clist">'+
          arr.map(function(c){ return '<li data-n="'+esc(norm(c.nom))+'"><a href="/commune.html?insee='+c.code+'">'+esc(c.nom)+'</a></li>'; }).join('')+'</ul></section>';
      });
      listEl.innerHTML = html;
    }).catch(function(){ listEl.innerHTML = '<p>La liste des communes n\'a pas pu être chargée. Réessayez dans quelques instants.</p>'; });
    var f = $('filter');
    if (f) f.addEventListener('input', function(){
      var q = norm(f.value);
      listEl.querySelectorAll('li').forEach(function(li){ li.hidden = q && li.getAttribute('data-n').indexOf(q) === -1; });
    });
  }

  /* ---------- Page : fiche commune ---------- */
  var cp = $('commune-page');
  if (cp){
    var stat = cp.hasAttribute('data-static');
    if (stat && $('com')) $('com').value = cp.getAttribute('data-nom') || '';
    var insee = (cp.getAttribute('data-insee') || new URLSearchParams(location.search).get('insee') || '').toUpperCase();
    if (!INSEE_RE.test(insee)){ $('c-nom').textContent = 'Commune introuvable'; }
    else Promise.all([
      getJSON(GEO+'/communes/'+insee+'?fields=nom,code,codesPostaux,population,codeDepartement,departement,epci'),
      getJSON(CARTO+'/gpu/municipality?insee='+insee).catch(function(){ return { features:[] }; })
    ]).then(function(r){
      var c = r[0], m = (r[1].features && r[1].features[0] || {}).properties || {};
      var dep = (c.departement && c.departement.nom) || c.codeDepartement;
      if (!stat) { document.title = 'PLU de ' + c.nom + ' (' + c.codeDepartement + ') : terrain constructible ? | TerrenUrbanisme';
      $('c-nom').textContent = 'Urbanisme à ' + c.nom;
      $('c-crumb').textContent = c.nom;
      $('c-meta').textContent = (c.codesPostaux||[]).join(', ') + ' · ' + dep + (c.population ? ' · ' + fmt(c.population) + ' habitants' : '') + (c.epci ? ' · ' + c.epci.nom : ''); }
      $('c-doc').textContent = m.is_rnu ? 'Règlement national d\'urbanisme' : 'Document d\'urbanisme local';
      $('c-doc-p').textContent = m.is_rnu ? 'Pas de PLU : la construction n\'est possible, en principe, qu\'en continuité du village ou d\'un hameau.' : 'PLU ou carte communale : la règle dépend de la zone de votre parcelle.';
      $('c-lit').textContent = m.is_coastline ? 'Commune littorale' : 'Commune non littorale';
      $('c-lit-p').textContent = m.is_coastline ? 'La loi Littoral s\'applique en plus du document d\'urbanisme.' : 'La loi Littoral ne s\'applique pas. La loi Montagne peut s\'appliquer.';
      var com = $('com'); if (com) com.value = c.nom;
      if ($('c-prix')) getJSON('https://tabular-api.data.gouv.fr/api/resources/851d342f-9c96-41c1-924a-11a7a7aae8a6/data/?code_geo__exact=' + insee).then(function(j){
        var r = j && j.data && j.data[0]; if (!r) throw 0;
        var mai = r.med_prix_m2_whole_maison, app = r.med_prix_m2_whole_appartement;
        var F = function(v){ return fmt(v).replace(/\u202f/g, '\u00a0'); };
        $('c-prix').textContent = mai ? F(mai) + ' €/m² · maisons' : app ? F(app) + ' €/m² · appartements' : 'Non disponible';
        $('c-prix-p').textContent = [mai && app ? 'Appartements : ' + F(app) + ' €/m².' : '', 'Ventes des cinq dernières années (DVF).'].filter(Boolean).join(' ');
      }).catch(function(){ $('c-prix').textContent = 'Dans le rapport'; });
      var lnk = $('c-guide'); if (lnk) lnk.href = m.is_rnu ? '/guides/plu-carte-communale-rnu.html' : '/guides/zones-plu.html';
    }).catch(function(){ if (!stat) $('c-nom').textContent = 'Fiche indisponible pour le moment'; else { $('c-doc').textContent = 'À vérifier'; $('c-lit').textContent = 'À vérifier'; } });
  }

  /* ---------- Page : couverture ---------- */
  var cov = $('cov-form');
  if (cov) cov.addEventListener('submit', function(e){
    e.preventDefault();
    resolveCommune($('cov-com').value).then(function(code){
      if (code) location.href = '/commune.html?insee=' + code;
      else $('cov-err').textContent = 'Commune introuvable. Choisissez la commune dans la liste proposée.';
    }).catch(function(){ $('cov-err').textContent = 'Le service est momentanément indisponible. Réessayez dans un instant.'; });
  });
  bindCommuneInput($('cov-com'), $('cov-list'));
})();

/* ---------- Page Tarifs : formules et paiement ---------- */
(function(){
  var root = document.getElementById('plans'); if (!root) return;
  var billing = 'm';
  try { if (localStorage.getItem('tu_bill') === 'a') billing = 'a'; } catch (e) {}
  // Prix TTC : mensuel, et annuel ramené au mois (payé en une fois)
  var SUB = {
    essentiel: { name: 'Essentiel', m: 19,  a: 15,  n: 10 },
    pro:       { name: 'Agence',    m: 49,  a: 39,  n: 50 },
    cabinet:   { name: 'Réseau',    m: 129, a: 103, n: 150 }
  };
  var UNIT = { unit: ['12,90 €', 'Paiement unique', 'Choisir · 1 rapport'], pack3: ['34,90 €', '3 rapports · 11,63 € le rapport', 'Choisir · 3 rapports'], pack5: ['54,90 €', '5 rapports · 10,98 € le rapport', 'Choisir · 5 rapports'] };
  var eur = function(v){ return (Math.round(v * 100) / 100).toLocaleString('fr-FR', { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + ' €'; };
  var cards = [];
  root.querySelectorAll('.plan').forEach(function(card){
    var group = card.getAttribute('data-group'), amt = card.querySelector('.amt'), unit = card.querySelector('.unit'), save = card.querySelector('.save'), btn = card.querySelector('.go'), err = card.querySelector('.plan-err');
    var segs = card.querySelectorAll('.seg button');
    var cur = group === 'unit' ? 'unit' : group === 'cab' ? 'cabinet' : 'pro';
    function render(){
      segs.forEach(function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-k') === cur ? 'true' : 'false'); });
      if (group === 'unit') { var o = UNIT[cur]; amt.innerHTML = o[0]; unit.textContent = o[1]; btn.textContent = o[2] + ' →'; btn.setAttribute('data-kind', cur); return; }
      var P = SUB[cur], an = billing === 'a';
      amt.innerHTML = an ? '<s>' + eur(P.m) + '</s>' + eur(P.a) + ' <small>/ mois</small>' : eur(P.m) + ' <small>/ mois</small>';
      if (save) save.innerHTML = an ? 'Facturé ' + eur(P.a * 12) + ' par an · <b>économisez ' + eur((P.m - P.a) * 12) + '</b>' : '';
      unit.textContent = an ? (P.n * 12).toLocaleString('fr-FR') + ' rapports par an · ' + eur(P.a / P.n) + ' le rapport' : P.n + ' rapports par mois · ' + eur(P.m / P.n) + ' le rapport';
      var li = card.querySelector('.li-renew'); if (li) li.textContent = an ? 'Tous les rapports de l\'année disponibles dès le paiement' : 'Rapports renouvelés chaque mois';
      var lf = card.querySelector('.li-fact'); if (lf) lf.textContent = an ? 'Une facture annuelle automatique' : 'Factures mensuelles automatiques';
      btn.textContent = 'Démarrer ' + P.name + (an ? ' annuel' : '') + ' →'; btn.setAttribute('data-kind', cur + (an ? '_an' : ''));
    }
    segs.forEach(function(b){ b.addEventListener('click', function(){ cur = b.getAttribute('data-k'); render(); }); });
    btn.addEventListener('click', function(){
      var A = window.TUAuth, kind = btn.getAttribute('data-kind'), label = btn.textContent;
      err.textContent = '';
      if (!A || !A.ready){ err.textContent = 'Le paiement n\'est pas encore activé.'; return; }
      btn.disabled = true; btn.textContent = 'Redirection vers le paiement…';
      A.checkout(kind).catch(function(e){
        btn.disabled = false; btn.textContent = label;
        err.innerHTML = e && e.code === 'deja_abonne' ? 'Vous avez déjà un abonnement en cours. Pour changer de formule, résiliez-le depuis <a href="/espace.html">votre espace</a> ; des lots de rapports restent disponibles à tout moment.' : 'Le paiement n\'a pas pu être ouvert. Réessayez dans un instant.';
      });
    });
    cards.push(render); render();
  });
  var sw = document.querySelectorAll('#bill .bill-sw button');
  function setBill(v){ billing = v; sw.forEach(function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-b') === v ? 'true' : 'false'); }); cards.forEach(function(f){ f(); }); try { localStorage.setItem('tu_bill', v); } catch (e) {} }
  sw.forEach(function(b){ b.addEventListener('click', function(){ setBill(b.getAttribute('data-b')); }); });
  setBill(billing);
})();
