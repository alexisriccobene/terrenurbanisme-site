/* TerrenUrbanisme — scripts du site */
(function(){
  'use strict';
  var $ = function(id){ return document.getElementById(id); };
  var CARTO = 'https://apicarto.ign.fr/api';
  var GEO = 'https://geo.api.gouv.fr';
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]; }); }
  function norm(s){ return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[-']/g,' ').replace(/\s+/g,' ').trim(); }
  /* Appels aux services publics : délai maximal et nouvelles tentatives automatiques (le cadastre de l'IGN répond parfois lentement ou par erreur) */
  function getJSON(url, tries){
    tries = tries == null ? 3 : tries;
    var ctl = window.AbortController ? new AbortController() : null, tm = ctl ? setTimeout(function(){ ctl.abort(); }, 20000) : null;
    return fetch(url, ctl ? { signal: ctl.signal } : undefined).then(function(r){
      if (tm) clearTimeout(tm);
      if (!r.ok){ var e = new Error('http '+r.status); e.retry = r.status >= 500 || r.status === 429; throw e; }
      return r.json();
    }).catch(function(e){
      if (tm) clearTimeout(tm);
      if (tries > 1 && (e.retry !== false) && !(e && e.user)) return new Promise(function(res){ setTimeout(res, 900 * (4 - tries)); }).then(function(){ return getJSON(url, tries - 1); });
      throw e;
    });
  }
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
  /* Paris, Lyon, Marseille : section et numéro se répètent d'un arrondissement à l'autre ; on travaille avec le code de l'arrondissement (ex. 75104) */
  var PLM_PARENT = { '75':'75056', '69':'69123', '13':'13055' };
  function plmOf(code){ var m = String(code||'').match(/^(75)(1\d\d)$|^(69)(38\d)$|^(13)(2\d\d)$/); if (!m) return null; var d = m[1]||m[3]||m[5]; return { parent: PLM_PARENT[d], arr: m[2]||m[4]||m[6] }; }
  function inseeOf(p){ var d = String(p.code_insee||'').slice(0,2); return (p.code_arr && p.code_arr !== '000' && PLM_PARENT[d] === p.code_insee) ? d + p.code_arr : p.code_insee; }
  function arrLabel(p){ var d = String(p.code_insee||'').slice(0,2), a = parseInt(p.code_arr, 10) || 0, n = d === '69' ? a - 380 : a % 100; return ({ '75':'Paris', '69':'Lyon', '13':'Marseille' }[d] || p.nom_com) + ' ' + n + (n === 1 ? 'er' : 'e') + ' arrondissement'; }
  function inseeQuery(code){ var P = plmOf(code); return P ? 'code_insee=' + P.parent + '&code_arr=' + P.arr : 'code_insee=' + code; }
  var comMap = {};
  function comLabel(c){ return c.nom + ' (' + c.codeDepartement + ')'; }
  // Liste des communes publiée avec le site : secours si le service de l'État (geo.api.gouv.fr) ne répond pas
  var localCom = null;
  function localCommunes(q, limit){
    if (!localCom) localCom = getJSON('/data/communes-noms.json').catch(function(e){ localCom = null; throw e; });
    return localCom.then(function(all){
      var n = norm(q), ex = [], st = [], ct = [];
      all.forEach(function(r){ var k = norm(r[0]); if (k === n) ex.push(r); else if (k.indexOf(n) === 0) st.push(r); else if (n.length > 2 && k.indexOf(n) > 0) ct.push(r); });
      var by = function(a, b){ return b[3] - a[3]; };
      return ex.sort(by).concat(st.sort(by), ct.sort(by)).slice(0, limit || 8).map(function(r){ return { nom: r[0], code: r[1], codeDepartement: r[2], population: r[3] }; });
    });
  }
  function searchCommunes(q, limit){
    var ctl = window.AbortController ? new AbortController() : null, t = ctl ? setTimeout(function(){ ctl.abort(); }, 4000) : null;
    return fetch(GEO+'/communes?'+(/^\d{5}$/.test(q) ? 'codePostal='+q : 'nom='+encodeURIComponent(q))+'&fields=nom,code,codeDepartement,codesPostaux,population&boost=population&limit='+(limit||8), ctl ? { signal: ctl.signal } : {})
      .then(function(r){ if (!r.ok) throw new Error('http '+r.status); return r.json(); })
      .catch(function(){ return localCommunes(q, limit); })
      .then(function(l){ if (t) clearTimeout(t); (l||[]).forEach(function(c){ comMap[norm(comLabel(c))] = c.code; }); return l || []; });
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
  /* Liste déroulante des communes : propositions visibles dès les premières lettres, sur ordinateur comme sur mobile */
  function bindCommuneInput(input, dl){
    if (!input) return;
    input.removeAttribute('list'); if (dl && dl.parentNode) dl.parentNode.removeChild(dl);
    input.setAttribute('role', 'combobox'); input.setAttribute('aria-autocomplete', 'list'); input.setAttribute('aria-expanded', 'false');
    var ul = document.createElement('ul'), lid = input.id + '-ac';
    ul.className = 'suggest'; ul.id = lid; ul.setAttribute('role', 'listbox'); ul.hidden = true;
    input.setAttribute('aria-controls', lid);
    (input.closest('.field') || input.parentNode).appendChild(ul);
    var t = null, items = [], active = -1, seq = 0;
    function close(){ ul.hidden = true; active = -1; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); }
    function render(){
      if (!items.length){ ul.innerHTML = '<li class="vide" aria-disabled="true">Aucune commune trouvée</li>'; ul.hidden = false; input.setAttribute('aria-expanded', 'true'); return; }
      ul.innerHTML = items.map(function(c, i){
        return '<li role="option" id="'+lid+'-'+i+'" aria-selected="'+(i===active)+'">'+esc(c.nom)+' <small>'+esc(c.codeDepartement)+(c.codesPostaux && c.codesPostaux[0] ? ' · '+esc(c.codesPostaux[0]) : '')+'</small></li>';
      }).join('');
      ul.hidden = false; input.setAttribute('aria-expanded', 'true');
      if (active >= 0) input.setAttribute('aria-activedescendant', lid+'-'+active);
    }
    function choose(i){
      var c = items[i]; if (!c) return;
      input.value = comLabel(c); comMap[norm(comLabel(c))] = c.code; close();
      input.dispatchEvent(new Event('input', { bubbles:true })); input.dispatchEvent(new Event('change', { bubbles:true }));
      var nx = input.form && input.form.querySelector('#sec'); if (nx && !nx.value) nx.focus();
    }
    function chercher(){
      var q = input.value.trim();
      if (q.length < 2 || /\(\w{2,3}\)$/.test(q)){ items = []; close(); return; }
      var n = ++seq;
      searchCommunes(q, 8).then(function(l){ if (n !== seq) return; items = l; active = l.length ? 0 : -1; if (document.activeElement === input) render(); }).catch(function(){});
    }
    input.addEventListener('input', function(e){ if (!e.isTrusted) return; clearTimeout(t); t = setTimeout(chercher, 150); });
    input.addEventListener('focus', function(){ if (input.value.trim().length >= 2 && !/\(\w{2,3}\)$/.test(input.value.trim())) chercher(); });
    input.addEventListener('keydown', function(e){
      if (ul.hidden || !items.length) return;
      if (e.key === 'ArrowDown'){ e.preventDefault(); active = Math.min(active+1, items.length-1); render(); }
      else if (e.key === 'ArrowUp'){ e.preventDefault(); active = Math.max(active-1, 0); render(); }
      else if ((e.key === 'Enter' || e.key === 'Tab') && active >= 0){ if (e.key === 'Enter') e.preventDefault(); choose(active); }
      else if (e.key === 'Escape'){ close(); }
    });
    ul.addEventListener('mousedown', function(e){ e.preventDefault(); });
    ul.addEventListener('click', function(e){ var li = e.target.closest('li[role=option]'); if (li) choose(+li.id.split('-').pop()); });
    input.addEventListener('blur', function(){ setTimeout(close, 150); });
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
    /* Dès que la commune est choisie, la carte se centre dessus */
    var lastGeo = '';
    function geoCommune(){
      var v = $('com').value.trim(); if (!v || v === lastGeo) return;
      resolveCommune(v).then(function(code){
        if (!code || v === lastGeo) return; lastGeo = v;
        return getJSON(GEO+'/communes/'+code+'?fields=centre,contour').then(function(c){
          var m = map || big; if (!m || !window.L) return;
          try {
            if (c.contour){ m.fitBounds(L.geoJSON(c.contour).getBounds(), { padding:[20,20], maxZoom:15 }); if (big && m !== big) big.fitBounds(L.geoJSON(c.contour).getBounds(), { padding:[20,20], maxZoom:15 }); montrerCommune(c.contour); }
            else if (c.centre){ m.setView([c.centre.coordinates[1], c.centre.coordinates[0]], 14); if (big && m !== big) big.setView([c.centre.coordinates[1], c.centre.coordinates[0]], 14); }
          } catch(e){}
        });
      }).catch(function(){});
    }
    $('com').addEventListener('change', geoCommune);
    /* Centrage dès la saisie : choix dans la liste (« Sotta (2A) ») tout de suite, ou nom complet tapé sans choisir (« Sotta ») après une courte pause */
    var geoT = null;
    $('com').addEventListener('input', function(){
      clearTimeout(geoT); var v = $('com').value.trim();
      if (/\(\w{2,3}\)$/.test(v)) { geoCommune(); return; }
      if (v.length < 3) return;
      geoT = setTimeout(function(){
        if ($('com').value.trim() !== v) return;
        searchCommunes(v, 8).then(function(l){
          var ex = l.filter(function(c){ return norm(c.nom) === norm(v); });
          if (ex.length === 1 && $('com').value.trim() === v){ comMap[norm(v)] = ex[0].code; geoCommune(); }
        }).catch(function(){});
      }, 450);
    });
    $('com').addEventListener('keydown', function(e){ if (e.key === 'Enter' || e.key === 'Tab') geoCommune(); });

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
        getJSON('https://api-adresse.data.gouv.fr/search/?q='+encodeURIComponent(q)+'&limit=6'+(window.TU_VILLE ? '&citycode='+encodeURIComponent(window.TU_VILLE.insee[0]) : '')).then(function(j){
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
        if (!sec && !num && comVal.trim()){
          // pas de numéro de parcelle : on ouvre la carte de la commune, le visiteur clique sur son terrain
          resolveCommune(comVal).then(function(code){
            if (!code){ errEl.textContent = 'Commune introuvable. Choisissez la commune dans la liste proposée.'; return; }
            if (!inPlace){ location.href = '/?commune='+encodeURIComponent(comVal)+'#recherche'; return; }
            openBig();
            getJSON(GEO+'/communes/'+code+'?fields=contour,centre').then(function(c){
              if (big && c.contour){ big.fitBounds(L.geoJSON(c.contour).getBounds(), { padding:[20,20] }); montrerCommune(c.contour); }
              else if (big && c.centre) big.setView([c.centre.coordinates[1], c.centre.coordinates[0]], 14);
            }).catch(function(){});
            var r = $('result'); if (r) r.innerHTML = '<div class="v-title">Trouvez votre terrain sur la carte</div><p class="v-why">Zoomez sur votre terrain (le plan affiche les villages, routes et cours d\'eau ; passez en « Satellite » pour voir les constructions), puis cliquez sur la parcelle : sa référence s\'affiche et l\'analyse démarre.</p>';
          }).catch(function(){ errEl.textContent = 'Le service est momentanément indisponible. Réessayez dans un instant.'; });
          return;
        }
        if (!sec || !num){ errEl.textContent = 'Indiquez la section (une ou deux lettres) et le numéro de la parcelle, ou laissez les deux vides pour choisir votre terrain sur la carte.'; return; }
        resolveCommune(comVal).then(function(code){
        if (!code){ errEl.textContent = 'Commune introuvable. Choisissez la commune dans la liste proposée.'; return; }
        if (!inPlace){ location.href = '/?commune='+encodeURIComponent(comVal)+'&section='+sec+'&numero='+num+'#recherche'; return; }
        var back = '/?commune='+encodeURIComponent(comVal)+'&section='+sec+'&numero='+num;
        if (sec.length === 1) sec = '0'+sec;
        while (num.length < 4) num = '0'+num;
        gate(back, function(){ analyse(CARTO+'/cadastre/parcelle?'+inseeQuery(code)+'&section='+sec+'&numero='+num); });
        }).catch(function(){ errEl.textContent = 'Le service est momentanément indisponible. Réessayez dans un instant.'; });
      }
    });

    /* Paramètres d'URL : préremplissage et lancement automatique */
    var qs = new URLSearchParams(location.search);
    if (qs.get('commune')){
      setMode('cad'); $('com').value = qs.get('commune');
      if (qs.get('section')) $('sec').value = qs.get('section');
      if (qs.get('numero')) $('num').value = qs.get('numero');
      if (inPlace && ((qs.get('section') && qs.get('numero')) || (!qs.get('section') && !qs.get('numero')))) communeIndex().then(function(i){ idx = i; form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit')); });
    } else if (qs.get('lon') && qs.get('lat') && inPlace){
      setMode('adr'); adr.value = qs.get('adresse') || '';
      picked = { properties:{ label:adr.value }, geometry:{ coordinates:[+qs.get('lon'), +qs.get('lat')] } };
      setTimeout(function(){ form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit')); }, 50);
    }

    /* Page d'une commune abonnée : la recherche est limitée à la commune */
    if (window.TU_VILLE){
      var VL = window.TU_VILLE;
      setMode(qs.get('lon') ? 'adr' : 'cad');
      $('com').value = VL.nom + ' (' + VL.insee[0].slice(0, 2) + ')'; $('com').readOnly = true; $('com').setAttribute('aria-readonly', 'true');
      comMap[norm($('com').value)] = VL.insee[0]; comMap[norm(VL.nom)] = VL.insee[0];
      setTimeout(geoCommune, 400);
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

  /* ---------- Fonds de carte : plan IGN (villes, villages, routes, cours d'eau) et photo aérienne avec les noms ---------- */
  var WMTS = 'https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&LAYER=';
  function fonds(m, minCad, pos){
    var plan = L.tileLayer(WMTS+'GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&FORMAT=image/png', { maxZoom:20, maxNativeZoom:19, attribution:'Plan, photographies aériennes et cadastre © IGN' });
    var photo = L.layerGroup([
      L.tileLayer(WMTS+'ORTHOIMAGERY.ORTHOPHOTOS&FORMAT=image/jpeg', { maxZoom:20, maxNativeZoom:19, attribution:'Plan, photographies aériennes et cadastre © IGN' }),
      L.tileLayer(WMTS+'GEOGRAPHICALNAMES.NAMES&FORMAT=image/png', { maxZoom:20, maxNativeZoom:18, opacity:.95 })
    ]);
    var cad = L.tileLayer.wms('https://data.geopf.fr/wms-r/wms', { layers:'CADASTRALPARCELS.PARCELLAIRE_EXPRESS', format:'image/png', transparent:true, version:'1.3.0', minZoom:minCad, maxZoom:20, opacity:.9 });
    var manuel = false, courant = null;
    function poser(b){ if (courant === b) return; if (courant) m.removeLayer(courant); b.addTo(m); courant = b; cad.bringToFront(); maj(); }
    // plan pour se repérer, photo aérienne une fois près du terrain (tant que le visiteur n'a pas choisi lui-même)
    function auto(){ if (!manuel) poser(m.getZoom() >= 17 ? photo : plan); }
    var Ctl = L.Control.extend({ options:{ position:pos || 'topright' }, onAdd:function(){
      var d = L.DomUtil.create('div', 'fond-ctl');
      d.innerHTML = '<button type="button" data-f="plan">Plan</button><button type="button" data-f="photo">Satellite</button>';
      L.DomEvent.disableClickPropagation(d);
      d.addEventListener('click', function(e){ var b = e.target.closest('button'); if (!b) return; manuel = true; poser(b.getAttribute('data-f') === 'photo' ? photo : plan); });
      this._d = d; return d; } });
    var ctl = new Ctl(); ctl.addTo(m);
    function maj(){ var d = ctl._d; if (!d) return; [].forEach.call(d.querySelectorAll('button'), function(b){ b.classList.toggle('on', (b.getAttribute('data-f') === 'photo') === (courant === photo)); }); }
    auto(); cad.addTo(m); m.on('zoomend', auto);
  }
  /* contour de la commune choisie, sur les deux cartes */
  var contours = [], dernierContour = null;
  function montrerCommune(contour){
    dernierContour = contour;
    contours.forEach(function(l){ try { l._map && l._map.removeLayer(l); } catch(e){} }); contours = [];
    [map, big].forEach(function(m){ if (m && contour) contours.push(L.geoJSON(contour, { interactive:false, style:{ color:'#A3462C', weight:2.5, dashArray:'6 5', fill:false } }).addTo(m)); });
  }

  /* ---------- Carte du héros ---------- */
  var map = null, layer = null, scope = $('scope');
  var small = function(){ return window.innerWidth <= 620; };
  if (scope && window.L){
    try {
      map = L.map('map', { zoomControl:false, scrollWheelZoom:false, dragging:true, tap:true, attributionControl:true, minZoom:3, maxZoom:20, zoomSnap:0.25 });
      map.fitBounds([[41.3, -4.9], [51.1, 9.6]], { paddingTopLeft:[10, 10], paddingBottomRight:[10, 90] });   // France métropolitaine et Corse, entières
      fonds(map, 16);
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
      big = L.map('bigmap', { zoomControl:false, scrollWheelZoom:true, minZoom:3, maxZoom:20 });
      big.fitBounds([[41.3, -4.9], [51.1, 9.6]]);
      fonds(big, 15, 'bottomright');
      if (dernierContour) setTimeout(function(){ montrerCommune(dernierContour); }, 0);
      L.control.zoom({ position:'bottomright' }).addTo(big);   // le bandeau d'aide occupe le haut de la carte sur téléphone
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
    if (window.ResizeObserver && !window.__rsObs && document.getElementById('bigmap')){ window.__rsObs = new ResizeObserver(function(){ if (big) big.invalidateSize(); }); window.__rsObs.observe(document.getElementById('bigmap')); }
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
      var fs = pj.features || [];
      if (fs.length > 1 && !fromAddress && fs[0].properties && fs[0].properties.code_arr && fs[0].properties.code_arr !== '000') { chooseArr(fs); return; }
      var parcel = fs[0];
      if (!parcel) throw { user: fromAddress ? 'Cliquez sur votre parcelle sur la carte.' : 'Aucune parcelle à cet endroit. Cliquez à l\'intérieur d\'une parcelle délimitée.' };
      return analyseParcel(parcel);
    });
  }
  function chooseArr(fs){
    var r = $('result'); if (!r) return;
    r.innerHTML = '<div class="v-title" style="font-size:18px">Ce numéro de parcelle existe dans plusieurs arrondissements. Choisissez le vôtre :</div><div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:12px">' +
      fs.map(function(f, i){ var p = f.properties || {}; return '<button type="button" class="v-cta" data-i="' + i + '" style="margin:0">' + esc(arrLabel(p)) + (p.contenance ? ' · ' + esc(String(p.contenance)) + ' m²' : '') + '</button>'; }).join('') + '</div>';
    r.querySelectorAll('[data-i]').forEach(function(b){ b.addEventListener('click', function(){
      panelMsg('Analyse de la parcelle…', true);
      analyseParcel(fs[+b.getAttribute('data-i')]).catch(function(){ panelMsg('Le cadastre n\'a pas répondu. Réessayez dans quelques instants.'); });
    }); });
  }
  function analyseParcel(parcel){
    return Promise.resolve().then(function(){
      var insee = parcel.properties.code_insee;
      var g = roundGeom(parcel.geometry), q = JSON.stringify(g);
      if (q.length > 6000 && window.turf){ g = roundGeom(turf.simplify(turf.feature(g), { tolerance:0.00002, highQuality:true }).geometry); q = JSON.stringify(g); }
      // Diagnostic gratuit : commune, zones du PLU, servitudes (monuments historiques, PPR) et loi Montagne, en parallèle
      var dep = /^97/.test(insee) ? insee.slice(0, 3) : insee.slice(0, 2);
      var none = function(){ return { features:[] }; };
      return Promise.all([
        getJSON(CARTO+'/gpu/municipality?insee='+insee).catch(none),
        getJSON(CARTO+'/gpu/zone-urba?geom='+encodeURIComponent(q)).catch(function(){ return null; }).then(function(z){
          /* PLU absent du Géoportail : zonage relevé sur le plan de zonage officiel de la commune */
          if (z && (z.features || []).length) return z;
          var C = window.TU_CONFIG || {};
          if (!C.supabaseUrl) return z;
          return fetch(C.supabaseUrl + '/rest/v1/zonage_local?select=libelle,libelong,typezone,geom,bbox&insee=eq.' + encodeURIComponent(insee), { headers: { apikey: C.supabaseKey } })
            .then(function(r){ return r.ok ? r.json() : []; }).then(function(rows){
              if (!rows || !rows.length) return z;
              var pb = window.turf ? turf.bbox(parcel) : null;
              var hit = rows.filter(function(r){ return !pb || !(r.bbox[0] > pb[2] || r.bbox[2] < pb[0] || r.bbox[1] > pb[3] || r.bbox[3] < pb[1]); })
                .filter(function(r){ try { return !window.turf || !turf.intersect || !!turf.intersect(parcel, turf.feature(r.geom)); } catch(e){ return true; } });
              if (!hit.length) return z;
              return { local: true, features: hit.map(function(r){ return { type: 'Feature', geometry: r.geom, properties: { libelle: r.libelle, libelong: r.libelong, typezone: r.typezone } }; }) };
            }).catch(function(){ return z; });
        }),
        getJSON(CARTO+'/gpu/assiette-sup-s?geom='+encodeURIComponent(q)).catch(function(){ return null; }),
        getJSON('/data/communes/' + dep + '.json').catch(function(){ return null; })
      ]).then(function(r){
        var muni = (r[0].features && r[0].features[0] || {}).properties || {};
        var pf = parcel, tot = 0; try { tot = window.turf ? turf.area(pf) : 0; } catch(e){}
        var zones = r[1] ? (r[1].features || []).map(function(f){
          var sh = null; try { if (tot && turf.intersect) { var it = turf.intersect(pf, f); sh = it ? turf.area(it) / tot : 0; } } catch(e){}
          return { code: f.properties.libelle || f.properties.typezone, tz: f.properties.typezone, lib: f.properties.libelong || '', share: sh, part: f.properties.partition || '' };
        }).filter(function(z){ return z.share == null || z.share >= 0.02; }).sort(function(a, b){ return (b.share || 0) - (a.share || 0); }) : null;
        var sups = r[2] ? (r[2].features || []).map(function(f){ return String(f.properties.suptype || f.properties.typeass || '').toLowerCase(); }) : null;
        var cd = r[3] ? (r[3][insee] || {}) : null;
        /* Pas de PLU selon la base officielle SUDOCUH : règlement national d'urbanisme (si aucune zone n'est publiée) */
        if (cd && cd.rnu && !(zones && zones.length) && !muni.is_rnu) muni.is_rnu = true;
        show(parcel, zones, muni, { sups: sups, mont: cd ? !!cd.mt : null, local: !!(r[1] && r[1].local) });
      });
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
  var WARNI = '<svg viewBox="0 0 24 24" fill="none" stroke="#A86A0C" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18h.01"/></svg>';
  /* ---------- Offre communale : le rapport complet est offert par la commune ---------- */
  function villeOffre(resultEl, ref){
    var VL = window.TU_VILLE;
    ['.v-offer', '.buy', '.v-buy-note', '.v-owner', '.v-buy-err'].forEach(function(s){ resultEl.querySelectorAll(s).forEach(function(x){ x.remove(); }); });
    var why = resultEl.querySelector('.v-why'), box = document.createElement('div'); box.className = 'vl-box';
    if (VL.insee.indexOf(ref.insee) < 0){
      box.innerHTML = '<p class="vl-hors"><strong>Cette parcelle n\'est pas sur la commune de ' + esc(VL.nom) + '.</strong> Le service proposé par ' + esc(VL.libelle) + ' couvre uniquement les parcelles de la commune. Pour une autre commune, rendez-vous sur <a href="/">terrenurbanisme.com</a>.</p>';
      why.after(box); return;
    }
    if (why) why.textContent = 'Le rapport complet répond à la question : peut-on construire, et à quelles conditions ? ' + VL.libelle.charAt(0).toUpperCase() + VL.libelle.slice(1) + ' vous l\'offre.';
    box.innerHTML = '<div class="vl-h">Recevez votre rapport complet, proposé par ' + esc(VL.libelle) + '</div>' +
      '<p class="vl-s">PDF d\'environ 45 pages, envoyé par e-mail en quelques minutes.</p>' +
      '<form class="vl-f" novalidate>' +
      '<label class="field"><span>E-mail</span><input name="email" type="email" autocomplete="email" required placeholder="vous@exemple.fr"></label>' +
      '<div class="vl-2"><label class="field"><span>Nom et prénom</span><input name="nom" autocomplete="name"></label>' +
      '<label class="field"><span>Téléphone <small>(facultatif)</small></span><input name="tel" type="tel" autocomplete="tel"></label></div>' +

      '<label class="vl-ck"><input type="checkbox" name="consent"><span>J\'accepte que la mairie de ' + esc(VL.nom) + ' soit informée de ma demande et puisse me recontacter au sujet de mon projet. <small>Facultatif.</small></span></label>' +
      '<button class="v-cta" type="submit">Recevoir mon rapport</button><p class="vl-err" role="alert"></p>' +
      '<p class="vl-note">Vos coordonnées servent à vous envoyer le rapport. Elles ne sont transmises à la mairie qu\'avec votre accord. <a href="/confidentialite.html" target="_blank" rel="noopener">Confidentialité</a></p></form>';
    (resultEl.querySelector('.v-proj') || why).after(box);
    var f = box.querySelector('form'), er = box.querySelector('.vl-err'), bt = f.querySelector('button');
    f.addEventListener('submit', function(e){
      e.preventDefault(); er.textContent = '';
      var v = { email: f.email.value.trim(), nom: f.nom.value.trim(), tel: f.tel.value.trim(), projet: projet() || '', consent: f.consent.checked };
      if (!/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(v.email)){ er.textContent = 'Indiquez une adresse e-mail valide.'; f.email.focus(); return; }
      if (v.consent && !v.nom){ er.textContent = 'Indiquez votre nom pour que la mairie puisse vous recontacter.'; f.nom.focus(); return; }
      bt.disabled = true; bt.textContent = 'Envoi en cours…';
      var body = Object.assign({ action: 'rapport', k: VL.k || '' }, ref, v);
      fetch(VL.api + '?ville=' + encodeURIComponent(VL.slug), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) })
        .then(function(r){ return r.json().then(function(j){ return { ok: r.ok, j: j }; }); })
        .then(function(x){
          if (x.ok && x.j.ok){ villeSuivi(box, x.j.s, v.email); return; }
          var M = { demo: 'Démonstration : la remise du rapport sera activée à la mise en service.', credits_epuises: 'Le service de la mairie est momentanément indisponible : le stock de rapports est épuisé. Vous pouvez obtenir votre rapport directement sur terrenurbanisme.com.', hors_commune: 'Cette parcelle n\'est pas sur la commune.', limite_email: 'Vous avez déjà demandé 3 rapports aujourd\'hui. Réessayez demain.', limite: 'Trop de demandes depuis cette connexion aujourd\'hui. Réessayez demain.', limite_ville: 'Le service a atteint sa limite du jour. Réessayez demain.', inactive: 'Le service n\'est pas actif pour cette commune.', email: 'Indiquez une adresse e-mail valide.' };
          er.textContent = M[x.j.error] || 'La demande n\'a pas pu aboutir. Réessayez dans un instant.';
          bt.disabled = false; bt.textContent = 'Recevoir mon rapport';
        }).catch(function(){ er.textContent = 'La demande n\'a pas pu aboutir. Réessayez dans un instant.'; bt.disabled = false; bt.textContent = 'Recevoir mon rapport'; });
    });
  }

  /* Page de la commune : suivi de la préparation, puis lecture en ligne et téléchargement, comme sur le site */
  function villeSuivi(box, sid, email){
    var VL = window.TU_VILLE, t0 = Date.now(), tries = 0;
    var STEPS = ['Lecture du cadastre et du zonage', 'Lecture du règlement de la zone', 'Risques, réseaux et fibre', 'Marché immobilier et permis', 'Mise en page du rapport'];
    box.innerHTML = '<div class="vl-ok"><div class="vl-h">Votre rapport est en préparation</div><div class="gen-wait" id="vl-wait"></div><p class="vl-s">Il vous sera aussi envoyé par e-mail à <strong>' + esc(email) + '</strong>. Rapport proposé par ' + esc(VL.libelle) + '.</p></div>';
    var w = box.querySelector('#vl-wait');
    function tick(){ var sec = Math.round((Date.now() - t0) / 1000), k = Math.min(STEPS.length - 1, Math.floor(sec / 25)); w.innerHTML = '<span class="spin"></span><div><b>Préparation de votre rapport… ' + (sec < 60 ? sec + ' s' : Math.floor(sec / 60) + ' min ' + (sec % 60) + ' s') + '</b><span>' + STEPS[k] + '. Comptez 1 à 3 minutes : vous pouvez laisser cette page ouverte.</span></div>'; }
    tick(); var it = setInterval(tick, 1000);
    function done(j){
      clearInterval(it);
      box.innerHTML = '<div class="vl-ok"><div class="vl-h">Votre rapport est prêt</div><p>Consultez-le en ligne ou téléchargez le PDF. Il vient aussi de vous être envoyé par e-mail à <strong>' + esc(email) + '</strong>.</p>' +
        '<div class="vl-acts"><a class="v-cta" href="' + esc(j.lien) + '" target="_blank" rel="noopener">Voir le rapport en ligne</a><a class="btn ghost" href="' + esc(j.pdf) + '" download>Télécharger le PDF</a></div><p class="vl-s">Rapport proposé par ' + esc(VL.libelle) + '.</p></div>';
    }
    (function poll(){
      if (!sid){ clearInterval(it); w.innerHTML = '<div><b>Votre rapport arrive par e-mail d\'ici quelques minutes.</b><span>Pensez à vérifier vos courriers indésirables.</span></div>'; return; }
      fetch(VL.api + '?ville=' + encodeURIComponent(VL.slug), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ action: 'suivi', s: sid }) })
        .then(function(r){ return r.json(); }).then(function(j){
          if (j && j.status === 'ready' && j.lien) return done(j);
          if (j && j.status === 'error'){ clearInterval(it); w.innerHTML = '<div><b>La préparation a rencontré un incident.</b><span>Le rapport vous sera envoyé par e-mail dès qu\'il sera prêt.</span></div>'; return; }
          if (++tries < 75) setTimeout(poll, 4000); else { clearInterval(it); w.innerHTML = '<div><b>La préparation prend plus de temps que prévu.</b><span>Le rapport vous sera envoyé par e-mail dès qu\'il sera prêt.</span></div>'; }
        }).catch(function(){ if (++tries < 75) setTimeout(poll, 4000); });
    })();
  }

  /* Projet du client : choisi dans le diagnostic, transmis au rapport */
  // Profil du demandeur (facultatif) : statistique de clientèle, le rapport est le même pour tous
  var PROF = [['particulier', 'Particulier'], ['agent', 'Agent immobilier'], ['notaire', 'Notaire'], ['moe', 'Maître d\'œuvre ou architecte'], ['geometre', 'Géomètre']];
  var profilV = null;
  function profil(v){
    if (v !== undefined){ profilV = v || ''; try { if (v) localStorage.setItem('tu_profil', v); } catch (e) {} return profilV; }
    if (profilV === null){ profilV = ''; try { profilV = localStorage.getItem('tu_profil') || ''; } catch (e) {} if (!PROF.some(function(x){ return x[0] === profilV; })) profilV = ''; }
    return profilV;
  }
  var PROJ = [['maison', 'Construire une maison'], ['extension', 'Agrandir ou surélever'], ['piscine', 'Piscine'], ['annexe', 'Abri, garage ou annexe'], ['division', 'Diviser le terrain'], ['achat', 'Acheter ou vendre']];
  var projetV = null;
  function projet(v){
    if (v !== undefined){ projetV = v || ''; try { if (v) localStorage.setItem('tu_projet', v); else localStorage.removeItem('tu_projet'); } catch (e) {} return projetV; }
    if (projetV === null){ projetV = ''; try { projetV = localStorage.getItem('tu_projet') || ''; } catch (e) {} }
    return projetV;
  }

  function show(parcel, zones, muni, extra){
    extra = extra || {};
    var resultEl = $('result');
    var p = parcel.properties;
    var sec = String(p.section).replace(/^0/,''), num = String(p.numero).replace(/^0+/,'');
    var ref = (p.nom_com||'') + ' · section ' + sec + ' · n° ' + num;
    var TZ = { U:'urbaine', AUC:'à urbaniser', AUS:'à urbaniser (fermée)', A:'agricole', N:'naturelle' };
    var zl = (zones || []).slice(0, 3).map(function(z){ var t = TZ[(z.tz || '').toUpperCase()] || (z.tz && z.tz.charAt(0) === 'N' ? 'naturelle' : z.tz && z.tz.charAt(0) === 'A' && z.tz.indexOf('AU') ? 'agricole' : ''); return z.code + (t ? ' (zone ' + t + ')' : '') + (z.share != null && zones.length > 1 ? ' · ' + Math.round(z.share * 100) + ' %' : ''); });
    var sups = extra.sups;
    /* Commune sans zonage numérique publié (ni RNU) : on le dit avant l'achat, le rapport ne pourra pas donner la zone */
    var noZone = zones != null && !zl.length && !muni.is_rnu;
    /* Règlement que sa collectivité ne publie qu'en consultation sur son propre site (lecture automatique impossible) : on le dit avant l'achat */
    var REG_NON_LU = { DU_2A198: 'le fichier du règlement déposé par la commune d\'Ota sur le Géoportail de l\'Urbanisme est vide' };
    var regNonLu = !noZone && (zones || []).some(function(z){ return REG_NON_LU[z.part]; }) ? REG_NON_LU[(zones || []).filter(function(z){ return REG_NON_LU[z.part]; })[0].part] : '';
    var found = [
      ['ok', 'Parcelle identifiée au cadastre', fmt(p.contenance) + ' m² · ' + (p.idu || '')],
      [noZone ? 'warn' : 'ok', 'Document d\'urbanisme', muni.is_rnu ? 'Règlement national d\'urbanisme' : noZone ? 'Document local non publié en ligne' : extra.local ? 'PLU communal : zonage relevé sur le plan officiel de la commune' : 'Document local publié'],
      [noZone ? 'warn' : 'ok', zl.length > 1 ? 'Zones du PLU' : 'Zone du PLU', zl.length ? zl.join(' · ') : muni.is_rnu ? 'Pas de zonage : règlement national' : 'Zonage non publié en ligne par la commune : à vérifier en mairie'],
      ['ok', 'Loi Littoral', muni.is_coastline ? 'Commune littorale : la loi s\'applique' : 'Commune non littorale']
    ];
    if (extra.mont != null) found.push(['ok', 'Loi Montagne', extra.mont ? 'Commune en zone de montagne : la loi s\'applique' : 'Commune hors zone de montagne']);
    if (sups) {
      found.push(['ok', 'Monuments historiques (ABF)', sups.some(function(x){ return x === 'ac1'; }) ? 'Dans les abords d\'un monument : avis de l\'architecte des Bâtiments de France' : 'Hors abords de monument historique recensés']);
      found.push(['ok', 'Plan de prévention des risques', sups.some(function(x){ return /^pm[1-3]/.test(x); }) ? 'Parcelle concernée par un PPR : règles détaillées dans le rapport' : 'Aucun PPR recensé sur la parcelle']);
    }
    var locked = ['Verdict : constructible ou non, et pourquoi', 'Plan de zonage et chapitre officiel du règlement en annexe', 'Règlement de la zone : hauteur, reculs, aspect, avec extraits', 'Surface constructible estimée en m² et plan d\'implantation', (/^2[AB]/.test(String(parcel && parcel.properties && parcel.properties.code_insee || '')) ? 'PADDUC, distance au rivage, loi Montagne' : 'Loi Littoral, distance au rivage, loi Montagne'), 'Risques à la parcelle, arrêtés de catastrophe naturelle', 'Accès, pente, assainissement et fibre', 'Photos aériennes depuis 1950 et permis accordés autour', 'Prix au m² de la commune et ventes de terrains alentour', 'État des risques (ERP) pré-rempli et rapport officiel Géorisques', 'Démarches, délais et interlocuteurs'];
    var OFF = { unit: { n: 1, u: '19,90 €', t: '19,90 €' }, pack2: { n: 2, u: '14,90 €', t: '29,80 €' }, pack3: { n: 3, u: '12,90 €', t: '38,70 €' } }, kind = 'unit';
    var btnTxt = function(){ var o = OFF[kind]; return o.n > 1 ? 'Obtenir ' + o.n + ' rapports complets · ' + o.t : 'Obtenir le rapport complet · ' + o.t; };
    var BTN = btnTxt();
    var opt = function(k, lbl, off, sub){ var o = OFF[k]; return '<label class="v-opt"><input type="radio" name="v-kind" value="' + k + '"' + (k === kind ? ' checked' : '') + '><span class="v-opt-l">' + lbl + (sub ? '<small class="v-opt-s">' + sub + '</small>' : '') + '</span>' + (off ? '<em>' + off + '</em>' : '') + '<b>' + o.u + (o.n > 1 ? '<small>/ rapport</small>' : '') + '</b></label>'; };
    var OFFER = '<div class="v-offer" role="radiogroup" aria-label="Nombre de rapports"><div class="v-offer-top"><b class="v-offer-u">' + OFF[kind].u + '</b> <span>/ rapport</span><div class="v-offer-t"' + (OFF[kind].n > 1 ? '' : ' hidden') + '>Prix total ' + OFF[kind].t + '</div></div>' +
      opt('unit', 'Rapport complet', '', 'Environ 45 pages pour décider en toute sécurité') + '<div class="v-opt-sep">Plusieurs biens ? Rapports complets moins chers</div>' + opt('pack2', '2 rapports complets', '−25 %') + opt('pack3', '3 rapports complets', '−35 %') +
      '<p class="v-opt-note">Lots : le premier rapport porte sur cette parcelle, les autres restent sur votre compte, sans limite de durée.</p></div>';
    resultEl.innerHTML =
      '<div class="v-ref">' + esc(ref) + '</div>' +
      '<span class="v-badge v-found"><i></i>Parcelle trouvée</span>' +
      '<div class="v-title">Votre diagnostic</div>' +
      '<p class="v-other">Ce n\'est pas la bonne parcelle ? Cliquez sur une autre parcelle de la carte.</p>' +
      '<p class="v-why">Nous avons trouvé cette parcelle et les sources officielles qui la concernent. Le rapport complet répond à la question : peut-on construire, et à quelles conditions ?</p>' +
      (window.TU_VILLE ? '' : '<div class="v-proj v-prof"><b>Vous êtes <span class="v-fac">(facultatif)</span></b><div class="v-chips v-chips-prof" role="radiogroup" aria-label="Vous êtes">' + PROF.map(function(x){ return '<button type="button" role="radio" data-r="' + x[0] + '" aria-checked="' + (x[0] === profil() ? 'true' : 'false') + '" aria-pressed="' + (x[0] === profil() ? 'true' : 'false') + '">' + x[1] + '</button>'; }).join('') + '</div></div>') +
      '<div class="v-proj"><b>Quel est votre projet ?</b><span>Le rapport sera présenté pour lui.</span><div class="v-chips" role="group" aria-label="Votre projet">' + PROJ.map(function(x){ return '<button type="button" data-p="' + x[0] + '" aria-pressed="' + (x[0] === projet() ? 'true' : 'false') + '">' + x[1] + '</button>'; }).join('') + '</div></div>' +
      (regNonLu ? '<p class="v-disc" style="background:#FBF1E1;border:1.5px solid #E2B66B;border-radius:12px;padding:12px 14px;color:#5A3A06"><strong>À savoir avant de commander.</strong><br>La zone de cette parcelle est connue, mais ' + regNonLu + '. Le rapport donne la zone, les risques, les servitudes, les réseaux et le marché ; pour les règles de construction de la zone (hauteur, reculs, emprise), il renvoie au règlement officiel, sans en faire la lecture détaillée.</p>' : '') + (noZone ? '<p class="v-disc" style="background:#FBF1E1;border:1.5px solid #E2B66B;border-radius:12px;padding:12px 14px;color:#5A3A06"><strong>Attention : la zone de cette parcelle n\'est pas disponible.</strong><br> cette commune dispose d\'un document d\'urbanisme mais ne l\'a pas encore mis en ligne sur le Géoportail de l\'Urbanisme, la plateforme officielle de l\'État. Aucun service ne peut donc lire sa zone automatiquement : elle est à vérifier en mairie (plan de zonage) ou par un certificat d\'urbanisme. Le rapport réunit toutes les autres données officielles de la parcelle (risques, servitudes, PADDUC, lois Littoral et Montagne, accès, réseaux, prix du marché) mais <strong>n\'indiquera pas la zone ni son règlement</strong>.</p>' : '') +
      OFFER + '<button type="button" class="v-cta v-cta-top buy">' + BTN + '</button><p class="v-buy-err" role="alert"></p>' +
      '<ul class="v-found-list">' + found.map(function(f){ return '<li>' + (f[0] === 'warn' ? WARNI : OKI) + '<div><strong>' + esc(f[1]) + '</strong><span>' + esc(f[2]) + '</span></div></li>'; }).join('') + '</ul>' +
      '<ul class="v-locked">' + locked.map(function(t){ return '<li>' + LOCK + '<span>' + esc(t) + '</span><i class="blur" aria-hidden="true">████████</i></li>'; }).join('') + '</ul>' +
      '<button type="button" class="v-cta buy">' + BTN + '</button>' +
      '<p class="v-buy-note">Rapport complet d\'environ 45 pages, avec sommaire cliquable, envoyé par e-mail en quelques minutes · paiement sécurisé par Stripe<br><a href="/tarifs.html">Professionnels : dès 129 € par mois pour 10 rapports</a> · <a href="/exemple.html">Voir un exemple</a></p><p class="v-buy-err" role="alert"></p>' +
      '<p class="v-disc">Information indicative, établie à partir des sources publiques consultées à la date de la recherche. Elle ne vaut ni certificat d\'urbanisme, ni autorisation, ni avis juridique : seule la mairie peut confirmer la constructibilité de la parcelle.</p>' +
      '<a class="v-owner" href="https://france-cadastre.fr/" target="_blank" rel="noopener">Connaître le propriétaire de cette parcelle <span>via France Cadastre ↗</span></a>';
    var parcelRef = { insee:inseeOf(p), commune:(inseeOf(p) !== p.code_insee ? arrLabel(p) : p.nom_com), section:sec, numero:num };
    if (projet()) parcelRef.projet = projet();
    if (profil()) parcelRef.profil = profil();
    resultEl.querySelectorAll('.v-chips-prof button').forEach(function(b){ b.addEventListener('click', function(){
      var v = b.getAttribute('data-r');
      resultEl.querySelectorAll('.v-chips-prof button').forEach(function(x){ var on = x === b; x.setAttribute('aria-pressed', on ? 'true' : 'false'); x.setAttribute('aria-checked', on ? 'true' : 'false'); });
      profil(v); parcelRef.profil = v;
      var bx = resultEl.querySelector('.v-prof'); if (bx) bx.classList.remove('err');
      resultEl.querySelectorAll('.v-buy-err').forEach(function(e){ e.textContent = ''; });
      if (window.TUAuth && window.TUAuth.track) window.TUAuth.track('profil', { insee: parcelRef.insee, profil: v });
    }); });
    resultEl.querySelectorAll('.v-chips:not(.v-chips-prof) button').forEach(function(b){ b.addEventListener('click', function(){
      var on = b.getAttribute('aria-pressed') !== 'true', v = on ? b.getAttribute('data-p') : '';
      resultEl.querySelectorAll('.v-chips button').forEach(function(x){ x.setAttribute('aria-pressed', x === b && on ? 'true' : 'false'); });
      projet(v); if (v) parcelRef.projet = v; else delete parcelRef.projet;
      if (window.TUAuth && window.TUAuth.track && v) window.TUAuth.track('projet', { insee: parcelRef.insee, projet: v });
    }); });
    if (window.TU_VILLE){ villeOffre(resultEl, parcelRef); drawBig(parcel); return; }
    var buys = resultEl.querySelectorAll('.buy'), errs = resultEl.querySelectorAll('.v-buy-err'), A = window.TUAuth, credits = 0, label = BTN;
    function setAll(t, dis){ buys.forEach(function(x){ x.disabled = !!dis; x.textContent = t; }); }
    var offerEl = resultEl.querySelector('.v-offer');
    resultEl.querySelectorAll('input[name="v-kind"]').forEach(function(r){ r.addEventListener('change', function(){
      if (!r.checked) return; kind = r.value; offerEl.querySelector('.v-offer-u').textContent = OFF[kind].u; offerEl.querySelector('.v-offer-t').textContent = 'Prix total ' + OFF[kind].t; offerEl.querySelector('.v-offer-t').hidden = OFF[kind].n < 2;
      offerEl.querySelector('.v-offer-top span').textContent = '/ rapport'; BTN = btnTxt(); if (!credits){ label = BTN; setAll(label); }
    }); });
    var inclus = false;
    if (A && A.ready) Promise.all([A.account(), A.mairie ? A.mairie() : null]).then(function(v){
      var c = v[0], mr = v[1];
      credits = c ? c.total : 0;
      if (mr && mr.illimite){ inclus = true; label = 'Générer le rapport complet · compte de démonstration'; setAll(label); if (offerEl) offerEl.hidden = true; return; }
      if (mr && mr.insee && mr.insee.indexOf(parcelRef.insee) >= 0){ inclus = true; label = 'Générer le rapport complet · inclus dans l\'abonnement de ' + mr.mairie; setAll(label); if (offerEl) offerEl.hidden = true; return; }
      if (mr){ errs.forEach(function(e){ e.textContent = 'Votre abonnement couvre uniquement les parcelles de ' + mr.mairie + '. Cette parcelle est hors de la commune.'; }); }
      if (c && c.membre && !(c.total > 0)){ errs.forEach(function(e){ e.innerHTML = 'Les crédits de ' + esc(c.membre.agence) + ' sont épuisés. <a href="/espace.html" style="color:var(--t);font-weight:700">Demander des crédits à l\'agence</a>'; }); return; }
      if (c && c.membre){ window.__TU_MEMBRE = c.membre.nom; inclus = true; label = 'Générer le rapport complet · à votre nom, crédits de ' + c.membre.agence; setAll(label); if (offerEl) offerEl.hidden = true; return; }
      if (credits > 0){ label = 'Générer le rapport complet · 1 rapport (solde : ' + credits + ')'; setAll(label); if (offerEl) offerEl.hidden = true; }
    }).then(function(){
      // Agence : le collaborateur qui demande le rapport (repris dans le tableau de bord)
      if (!(credits > 0 || inclus) || !A.agents) return;
      return A.agents().then(function(L){
        if (!L.length) return;
        var last = ''; try { last = localStorage.getItem('tu_agent') || ''; } catch (e) {}
        if (window.__TU_MEMBRE) last = window.__TU_MEMBRE;
        var d = document.createElement('div'); d.className = 'v-proj v-agent';
        d.innerHTML = '<b>Collaborateur</b><span>Qui demande ce rapport ? Il apparaîtra à son nom dans le tableau de bord.</span><select style="display:block;width:100%;margin-top:8px;padding:11px;border:1.5px solid var(--ligne);border-radius:10px;font:inherit;background:#fff"><option value="">Choisir le collaborateur</option>' + L.map(function(a){ return '<option' + (a.nom === last ? ' selected' : '') + '>' + esc(a.nom) + '</option>'; }).join('') + '</select>';
        var pj = resultEl.querySelector('.v-proj'); pj.parentNode.insertBefore(d, pj.nextSibling);
        agentSel = d.querySelector('select');
        if (agentSel.value) parcelRef.agent = agentSel.value;
        agentSel.addEventListener('change', function(){ if (agentSel.value) { parcelRef.agent = agentSel.value; try { localStorage.setItem('tu_agent', agentSel.value); } catch (e) {} } else delete parcelRef.agent; agentSel.style.borderColor = ''; });
        // Client de l'agence (facultatif) : repris sur la couverture de la version client et dans l'e-mail d'envoi
        var cb = document.createElement('div'); cb.className = 'v-proj v-client';
        var fs = 'display:block;width:100%;padding:11px;border:1.5px solid var(--ligne);border-radius:10px;font:inherit;font-size:16px;background:#fff;box-sizing:border-box;min-width:0';
        cb.innerHTML = '<b>Votre client</b><span>Facultatif. Son nom figurera sur la version client du rapport, et son e-mail servira à la lui envoyer.</span>' +
          '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-top:8px"><select data-c="civ" style="' + fs + '"><option value="">Civilité</option><option>M.</option><option>Mme</option><option>M. et Mme</option></select>' +
          '<input data-c="prenom" placeholder="Prénom" autocomplete="off" style="' + fs + '"><input data-c="nom" placeholder="Nom" autocomplete="off" style="' + fs + '"></div>' +
          '<input data-c="email" type="email" placeholder="E-mail du client" autocomplete="off" style="' + fs + ';margin-top:8px">';
        d.parentNode.insertBefore(cb, d.nextSibling);
        cb.querySelectorAll('[data-c]').forEach(function(el){ el.addEventListener('input', function(){
          var c = {}; cb.querySelectorAll('[data-c]').forEach(function(x){ if (x.value.trim()) c[x.getAttribute('data-c')] = x.value.trim(); });
          try { if (Object.keys(c).length) sessionStorage.setItem('tu_client', JSON.stringify(c)); else sessionStorage.removeItem('tu_client'); } catch (e) {}
        }); });
        try { sessionStorage.removeItem('tu_client'); } catch (e) {}
      });
    }).catch(function(){});
    var agentSel = null;
    buys.forEach(function(btn, k){ btn.addEventListener('click', function(){
      var err = errs[k] || errs[0];
      if (A && A.track) A.track('clic_rapport', parcelRef);
      errs.forEach(function(e){ e.textContent = ''; });
      if (agentSel && !agentSel.value){ err.textContent = 'Choisissez le collaborateur qui demande ce rapport.'; agentSel.style.borderColor = 'var(--non,#B3402F)'; agentSel.scrollIntoView({ block: 'center', behavior: 'smooth' }); agentSel.focus(); return; }
      if (!A || !A.ready){ err.textContent = 'Le paiement n\'est pas encore activé.'; return; }
      setAll(credits > 0 || inclus ? 'Génération du rapport…' : 'Redirection vers le paiement…', true);
      A.user().then(function(u){
        if (!u) return window.TUFunnel ? window.TUFunnel.email(kind, parcelRef).then(function(v){ if (v === 'ferme') setAll(label, false); }) : A.checkout(kind, parcelRef);
        if (!u){ location.href = A.loginUrl('/?commune=' + encodeURIComponent(inseeOf(p) !== p.code_insee ? inseeOf(p) : p.nom_com) + '&section=' + encodeURIComponent(sec) + '&numero=' + encodeURIComponent(num)); return; }
        return credits > 0 || inclus ? A.generate(parcelRef) : A.checkout(kind, parcelRef);
      }).catch(function(e){
        err.textContent = e && e.code === 'hors_commune' ? 'Cette parcelle est hors de votre commune : elle n\'est pas couverte par l\'abonnement.' : e && e.code === 'solde' ? 'Votre solde de rapports est épuisé.' : 'L\'opération n\'a pas pu aboutir. Réessayez dans un instant.';
        if (e && e.code === 'solde') { credits = 0; label = BTN; if (offerEl) offerEl.hidden = false; }
        setAll(label, false);
      });
    }); });
    if (window.TUAuth && window.TUAuth.track) window.TUAuth.track('diagnostic', parcelRef);
    if (window.TUFunnel) window.TUFunnel.afterDiag(parcelRef);
    if (window.TUAuth) window.TUAuth.saveDiagnostic({ insee:inseeOf(p), commune:parcelRef.commune, section:sec, numero:num, verdict:null, zone:null });
    var tip = $('rs-tip'); if (tip) tip.hidden = true;
    drawBig(parcel);
  }
  function drawBig(parcel){
    if (!big) return;
    if (blayer) big.removeLayer(blayer);
    if (bmarker){ big.removeLayer(bmarker); bmarker = null; }
    blayer = L.geoJSON(parcel, { style:{ color:'#FFD27A', weight:3.5, fillColor:'#FFD27A', fillOpacity:.22 } }).addTo(big);
    big.invalidateSize();
    big.fitBounds(blayer.getBounds(), { padding:[60,60], maxZoom:19 });
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
      getJSON(CARTO+'/gpu/municipality?insee='+insee).catch(function(){ return { features:[] }; }),
      getJSON('/data/communes/' + (/^97/.test(insee) ? insee.slice(0, 3) : insee.slice(0, 2)) + '.json').catch(function(){ return null; })
    ]).then(function(r){
      var c = r[0], m = (r[1].features && r[1].features[0] || {}).properties || {};
      if (r[2] && r[2][insee] && r[2][insee].rnu) m.is_rnu = true;   // SUDOCUH : pas de PLU
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
      // Prix DVF et loi Montagne : données publiées avec le site (data/communes), une seule requête par département
      var dep = /^97/.test(insee) ? insee.slice(0, 3) : insee.slice(0, 2);
      getJSON('/data/communes/' + dep + '.json').then(function(all){
        var r = (all && all[insee]) || {}, p = r.p || [];
        if (!m.is_coastline) $('c-lit-p').textContent = 'La loi Littoral ne s\'applique pas.' + (r.mt ? ' La commune est en zone de montagne : la loi Montagne s\'applique.' : ' La commune n\'est pas en zone de montagne.');
        else if (r.mt) $('c-lit-p').textContent = 'La loi Littoral et la loi Montagne s\'appliquent en plus du document d\'urbanisme.';
        if (!$('c-prix')) return;
        var mai = p[0], app = p[3];
        var F = function(v){ return fmt(v).replace(/\u202f/g, '\u00a0'); };
        $('c-prix').textContent = mai ? F(mai) + ' €/m² · maisons' : app ? F(app) + ' €/m² · appartements' : 'Dans le rapport';
        $('c-prix-p').textContent = [mai && app ? 'Appartements : ' + F(app) + ' €/m².' : '', mai || app ? 'Prix médian des ventes des cinq dernières années (DVF).' : ''].filter(Boolean).join(' ');
      }).catch(function(){ if ($('c-prix')) $('c-prix').textContent = 'Dans le rapport'; });
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

/* ---------- Tarifs : Particuliers / Professionnels, paiement, offre personnalisée ---------- */
(function(){
  var eur = function(v){ return (Math.round(v * 100) / 100).toLocaleString('fr-FR', { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }).replace(/[\u202f\u00a0]/g, '\u00a0') + '\u00a0€'; };
  var LIM = ['<strong>Votre logo et vos coordonnées sur chaque rapport</strong>', 'Rapports renouvelés chaque mois, au meilleur prix', 'Rapports non utilisés reportés sur le mois suivant', 'Sans engagement, résiliable en un clic'];
  var LIY = ['<strong>Votre logo et vos coordonnées sur chaque rapport</strong>', 'Tous les rapports de l\'année disponibles dès le paiement', '10 mois payés pour 12, le prix le plus bas', 'Rappel par e-mail avant le renouvellement'];
  var aud = document.querySelector('.aud');
  if (aud) {
    var pans = document.querySelectorAll('.tu-pan');
    var setAud = function(a){
      aud.querySelectorAll('button').forEach(function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-a') === a ? 'true' : 'false'); });
      pans.forEach(function(p){ p.hidden = p.getAttribute('data-pan') !== a; });
    };
    aud.querySelectorAll('button').forEach(function(b){ b.addEventListener('click', function(){ setAud(b.getAttribute('data-a')); }); });
    if (/^#(pro|professionnels|offre|demo)$/.test(location.hash)) setAud('pro');
    window.addEventListener('hashchange', function(){ if (/^#(pro|professionnels)$/.test(location.hash)) setAud('pro'); });
    var AB = { '10': [129, 10], '30': [297, 30] }, mode = 'credits', bill = document.querySelector('.tu-pan .billing');
    var render = function(){
      document.querySelectorAll('.plans-pro .plan, .sur-mesure').forEach(function(c){ var m = c.getAttribute('data-m'); c.hidden = mode === 'credits' ? m !== 'credits' : m !== 'abo'; });
      document.querySelectorAll('.plans-pro .plan[data-ab]').forEach(function(c){
        var n = c.getAttribute('data-ab'), A = AB[n], amt = c.querySelector('.amt'), u = c.querySelector('.unit'), btn = c.querySelector('.go'), nom = c.querySelector('h3').textContent, ulx = c.querySelector('ul');
        if (ulx) ulx.innerHTML = LIM.map(function(t){ return '<li>' + t + '</li>'; }).join('');
        btn.textContent = 'S\'abonner · ' + nom + ' →';
        if (mode === 'an') { amt.innerHTML = eur(A[0] * 10) + ' <small>/ an</small>'; u.textContent = (A[1] * 12) + ' rapports pour l\'année · ' + eur(A[0] * 10 / (A[1] * 12)) + ' le rapport'; btn.setAttribute('data-kind', 'ab' + n + '_an'); }
        else { amt.innerHTML = eur(A[0]) + ' <small>/ mois</small>'; u.innerHTML = eur(A[0] / A[1]) + ' le rapport <s class="old">19,90\u00a0€</s>'; btn.setAttribute('data-kind', 'ab' + n); }
      });
    };
    if (bill) bill.querySelectorAll('button').forEach(function(b){ b.addEventListener('click', function(){
      mode = b.getAttribute('data-m');
      bill.querySelectorAll('button').forEach(function(x){ x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      render();
    }); });
    document.querySelectorAll('.tu-pan .plan .go').forEach(function(btn){
      var err = btn.parentNode.querySelector('.plan-err');
      btn.addEventListener('click', function(){
        var A = window.TUAuth, kind = btn.getAttribute('data-kind'), label = btn.textContent;
        if (err) err.textContent = '';
        if (!A || !A.ready){ if (err) err.textContent = 'Le paiement n\'est pas encore activé.'; return; }
        btn.disabled = true; btn.textContent = 'Redirection vers le paiement…';
        var guestOk = /^(unit|pack2|pack3|pro10|pro30|pro100)$/.test(kind);
        A.user().then(function(u){ if (!u && guestOk && window.TUFunnel) return window.TUFunnel.email(kind, {}).then(function(){ btn.disabled = false; btn.textContent = label; }); return A.checkout(kind); }).catch(function(e){
          btn.disabled = false; btn.textContent = label;
          if (err) err.textContent = e && e.code === 'deja_abonne' ? 'Vous avez déjà un abonnement actif. Modifiez-le depuis votre espace, rubrique « Gérer mon abonnement ».' : 'Le paiement n\'a pas pu démarrer. Réessayez dans un instant.';
        });
      });
    });
    render();
  }
  var f = document.getElementById('devis');
  if (f) {
    var type = f.getAttribute('data-type') || 'offre', fixed = !!f.getAttribute('data-type'), demoL = f.querySelector('.devis-demo'), msg = f.querySelector('.devis-msg'), sb = f.querySelector('button[type="submit"]');
    var setT = function(t){ type = t; f.querySelectorAll('.devis-type button').forEach(function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-t') === t ? 'true' : 'false'); }); if (demoL) demoL.hidden = t !== 'demo'; sb.textContent = fixed ? (f.getAttribute('data-label') || 'Envoyer ma demande') : t === 'demo' ? 'Demander ma démonstration' : 'Envoyer ma demande'; };
    f.querySelectorAll('.devis-type button').forEach(function(b){ b.addEventListener('click', function(){ setT(b.getAttribute('data-t')); }); });
    var fromHash = function(){ if (fixed) return; if (location.hash === '#demo') setT('demo'); else if (location.hash === '#offre') setT('offre'); };
    fromHash(); window.addEventListener('hashchange', fromHash);
    f.addEventListener('submit', function(ev){
      ev.preventDefault(); msg.className = 'devis-msg'; msg.textContent = '';
      var d = { type: type, page: location.pathname };
      ['nom', 'societe', 'email', 'telephone', 'profession', 'volume', 'creneau', 'message', 'site_web'].forEach(function(k){ var el = f.elements[k]; d[k] = el ? el.value.trim() : ''; });
      if (!d.nom || !/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(d.email)) { msg.className = 'devis-msg ko'; msg.textContent = 'Indiquez votre nom et une adresse e-mail valide.'; return; }
      var C = window.TU_CONFIG || {}; sb.disabled = true; var lab = sb.textContent; sb.textContent = 'Envoi en cours…';
      fetch((C.supabaseUrl || 'https://nmoigruxnhsidrhqtzid.supabase.co') + '/functions/v1/stripe-webhook?demande=pro', { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=UTF-8' }, body: JSON.stringify(d) })
        .then(function(r){ return r.json().then(function(j){ return { ok: r.ok && j.ok, j: j }; }); })
        .then(function(x){
          sb.disabled = false; sb.textContent = lab;
          if (x.ok) { f.reset(); setT(type); msg.className = 'devis-msg ok'; msg.textContent = type === 'demo' ? 'Merci, votre demande de démonstration est bien reçue. Nous vous contactons sous 24 heures ouvrées pour fixer le rendez-vous.' : type === 'partenaire' ? 'Merci, votre candidature est bien reçue. Nous revenons vers vous sous 48 heures ouvrées.' : type === 'integration' ? 'Merci, votre demande est bien reçue. Nous revenons vers vous sous 24 heures ouvrées.' : 'Merci, votre demande est bien reçue. Nous revenons vers vous sous 24 heures ouvrées avec une offre adaptée.'; }
          else { msg.className = 'devis-msg ko'; msg.textContent = x.j && x.j.error === 'limite' ? 'Trop de demandes en peu de temps. Réessayez dans une heure ou écrivez à contact@terrenurbanisme.com.' : 'La demande n\'a pas pu être envoyée. Vérifiez les champs ou écrivez à contact@terrenurbanisme.com.'; }
        }).catch(function(){ sb.disabled = false; sb.textContent = lab; msg.className = 'devis-msg ko'; msg.textContent = 'La demande n\'a pas pu être envoyée. Réessayez ou écrivez à contact@terrenurbanisme.com.'; });
    });
  }
})();

/* ---------- Assistant virtuel (réponses issues de la FAQ, sans service externe) ---------- */
(function(){
  if (/^\/(espace|connexion|espace-pro|espace-mairie|merci|tiktok)/.test(location.pathname) || document.getElementById('tu-bot')) return;
  var KB = [
    { q: 'Mon terrain est-il constructible ?', k: ['constructible', 'construire', 'zone', 'plu', 'terrain', 'parcelle', 'batir'], a: 'Saisissez l\'adresse ou la référence cadastrale dans la recherche : la parcelle s\'affiche avec sa zone et ses principales contraintes avant tout paiement. Le rapport complet détaille ensuite ce que vous pouvez construire.', l: [['Vérifier mon terrain', '/#recherche']] },
    { q: 'Que contient le rapport ?', k: ['contient', 'contenu', 'rapport', 'pages', 'quoi', 'exemple', 'detail'], a: 'Environ 45 pages : verdict, plan de zonage, règlement de la zone lu pour vous avec les extraits officiels, surface constructible estimée, risques, servitudes, lois Littoral et Montagne, réseaux et fibre, taxe d\'aménagement, prix du marché, photos aériennes depuis 1950 et état des risques pré-rempli.', l: [['Voir un exemple', '/exemple.html']] },
    { q: 'Combien ça coûte ?', k: ['prix', 'tarif', 'cout', 'coute', 'combien', 'euros', 'payer', 'lot'], a: 'Particuliers : 19,90 € le rapport complet, 14,90 € le rapport par lot de 2, 12,90 € par lot de 3. Professionnels : crédits sans limite de durée, 10 rapports pour 149 €, 30 pour 357 €, 100 pour 790 €, ou abonnement de 10 rapports par mois pour 129 € ou 30 pour 297 €, sans engagement.', l: [['Voir les tarifs', '/tarifs.html']] },
    { q: 'En combien de temps je le reçois ?', k: ['delai', 'temps', 'recevoir', 'quand', 'minutes', 'rapidement', 'vite'], a: 'Le rapport vous est envoyé par e-mail en quelques minutes après le paiement. Il reste disponible dans votre espace.', l: [] },
    { q: 'Le rapport a-t-il une valeur officielle ?', k: ['officiel', 'officielle', 'certificat', 'valeur', 'juridique', 'mairie', 'garantie'], a: 'Non. C\'est un document d\'information établi à partir des sources publiques officielles. Seul le certificat d\'urbanisme, délivré par la mairie, engage l\'administration : le rapport vous aide à décider avant de le demander.', l: [['Le certificat d\'urbanisme', '/guides/certificat-urbanisme.html']] },
    { q: 'Je n\'ai pas reçu mon rapport', k: ['recu', 'reçu', 'pas recu', 'mail', 'email', 'spam', 'introuvable', 'probleme'], a: 'Vérifiez vos courriers indésirables. Votre rapport est aussi disponible depuis votre espace, avec le bouton « Se connecter ». Sinon, écrivez-nous en indiquant la référence de la parcelle : contact@terrenurbanisme.com.', l: [['Se connecter', '/connexion.html']] },
    { q: 'Je suis professionnel', k: ['pro', 'professionnel', 'agence', 'agent', 'notaire', 'geometre', 'architecte', 'logo', 'credits', 'abonnement', 'diagnostiqueur'], a: 'Votre logo et vos coordonnées sur chaque rapport, un back-office pour vos collaborateurs, des crédits sans limite de durée ou un abonnement sans engagement. Au-delà de 100 rapports, nous établissons une offre personnalisée.', l: [['Tarifs professionnels', '/tarifs.html#pro'], ['Réserver une démonstration', '/tarifs.html#demo']] },
    { q: 'Quelles communes sont couvertes ?', k: ['commune', 'couvert', 'couverture', 'france', 'corse', 'outre', 'region', 'ville'], a: 'Toute la France : métropole, Corse et outre-mer, soit près de 35 000 communes.', l: [] },
    { q: 'Puis-je avoir une facture ?', k: ['facture', 'tva', 'societe', 'entreprise', 'comptable'], a: 'Oui. Une facture est envoyée automatiquement à chaque paiement, au nom de votre société si vous l\'indiquez lors du paiement.', l: [] },
    { q: 'Et si une information manque ?', k: ['manque', 'manquant', 'source', 'erreur', 'incomplet', 'regenerer'], a: 'Si une source publique ne répond pas, le rapport le signale clairement. Écrivez-nous dans les 30 jours : nous le régénérons sans frais dès que la source est de nouveau disponible.', l: [] },
    { q: 'Comment résilier mon abonnement ?', k: ['resilier', 'resiliation', 'annuler', 'engagement', 'arreter'], a: 'L\'abonnement est sans engagement : il se résilie en un clic depuis votre espace, rubrique « Gérer mon abonnement ».', l: [['Mon espace', '/connexion.html']] },
    { q: 'Je représente une mairie', k: ['mairie', 'commune', 'maire', 'collectivite', 'intercommunalite', 'habitants'], a: 'Les communes peuvent mettre le rapport complet à la disposition de leurs habitants, depuis le site de la mairie.', l: [['L\'offre pour les communes', '/mairies.html']] },
    { q: 'Parler à quelqu\'un', k: ['contact', 'parler', 'humain', 'telephone', 'appeler', 'joindre', 'conseiller'], a: 'Écrivez-nous à contact@terrenurbanisme.com : nous répondons sous 24 heures ouvrées. Les professionnels peuvent aussi réserver une démonstration en visio.', l: [['Réserver une démonstration', '/tarifs.html#demo']] }
  ];
  var QUICK = [0, 2, 1, 6, 4, 12];
  var norm = function(t){ return String(t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9 ]+/g, ' '); };
  var find = function(t){
    var n = ' ' + norm(t) + ' ', best = -1, bs = 0;
    KB.forEach(function(e, i){ var sc = 0; e.k.forEach(function(k){ if (n.indexOf(' ' + norm(k)) >= 0) sc++; }); if (sc > bs) { bs = sc; best = i; } });
    return best;
  };
  var el = function(tag, cls, txt){ var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  var root = el('div', 'tu-bot'); root.id = 'tu-bot';
  var btn = el('button', 'tu-bot-btn'); btn.type = 'button'; btn.setAttribute('aria-label', 'Ouvrir l\'assistant'); btn.setAttribute('aria-expanded', 'false');
  btn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H8l-4 4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg><span>Une question ?</span>';
  var pan = el('div', 'tu-bot-pan'); pan.hidden = true; pan.setAttribute('role', 'dialog'); pan.setAttribute('aria-label', 'Assistant TerrenUrbanisme');
  var head = el('div', 'tu-bot-head'); head.appendChild(el('b', '', 'Assistant TerrenUrbanisme')); var cl = el('button', 'tu-bot-x', '×'); cl.type = 'button'; cl.setAttribute('aria-label', 'Fermer'); head.appendChild(cl);
  var log = el('div', 'tu-bot-log'); log.setAttribute('aria-live', 'polite');
  var qk = el('div', 'tu-bot-q');
  var fm = el('form', 'tu-bot-f'); var inp = el('input'); inp.placeholder = 'Posez votre question'; inp.maxLength = 200; inp.setAttribute('aria-label', 'Votre question'); var go = el('button', '', 'Envoyer'); go.type = 'submit'; fm.appendChild(inp); fm.appendChild(go);
  pan.appendChild(head); pan.appendChild(log); pan.appendChild(qk); pan.appendChild(fm); root.appendChild(pan); root.appendChild(btn);
  var hist = [];
  var LBL = { '/#recherche': 'Vérifier un terrain', '/exemple.html': 'Exemple de rapport', '/tarifs.html': 'Tarifs', '/tarifs.html#offre': 'Demander une offre', '/tarifs.html#demo': 'Réserver une démo', '/tarifs.html#pro': 'Tarifs professionnels', '/fonctionnalites.html': 'Fonctionnalités', '/sources.html': 'Nos sources', '/faq.html': 'Questions fréquentes', '/blog/': 'Blog', '/mairies.html': 'Offre mairies', '/partenaires.html': 'Programme partenaires', '/integration.html': 'Intégration', '/qui-sommes-nous.html': 'Qui sommes-nous', '/pourquoi-terrenurbanisme.html': 'Pourquoi TerrenUrbanisme', '/connexion.html': 'Se connecter', '/presse.html': 'Espace presse', '/couverture.html': 'Couverture', '/comment-ca-marche.html': 'Comment ça marche' };
  var linkify = function(p, txt){
    txt = txt.replace(/\*\*([^*]+)\*\*/g, '$1');
    var re = /\[([^\]]{1,60})\]\(([^)\s]+)\)|(contact@terrenurbanisme\.com|https?:\/\/terrenurbanisme\.com[^\s,;)]*|\/(?:#recherche|[a-z0-9-]+(?:\/[a-z0-9-]+)*(?:\.html)?\/?(?:#[a-z]+)?))/g, last = 0, mt;
    while ((mt = re.exec(txt))) {
      var lab = mt[1] || null, u = (mt[2] || mt[3]).replace(/[.]+$/, ''), full = mt[1] ? mt[0] : u;
      u = u.replace(/^https?:\/\/terrenurbanisme\.com/, '') || '/';
      if (u.charAt(0) === '/' && !/^\/(#recherche|exemple|tarifs|fonctionnalites|sources|faq|blog|mairies|partenaires|integration|outils|guides|qui-sommes-nous|pourquoi|connexion|presse|couverture|comment|agences|notaires|geometres|architectes|diagnostiqueurs|$)/.test(u)) continue;
      p.appendChild(document.createTextNode(txt.slice(last, mt.index)));
      var a = document.createElement('a'); a.textContent = lab || LBL[u] || (u.indexOf('@') > 0 ? u : (u === '/' ? 'terrenurbanisme.com' : u)); a.href = u.indexOf('@') > 0 ? 'mailto:' + u : u; a.className = 'tu-bot-inl'; p.appendChild(a); last = mt.index + full.length;
    }
    p.appendChild(document.createTextNode(txt.slice(last)));
  };
  var say = function(who, txt, links){
    if (who === 'me') qk.hidden = true;
    var m = el('div', 'tu-bot-m ' + who); var pp = el('p'); if (who === 'bot') linkify(pp, txt); else pp.textContent = txt; m.appendChild(pp);
    hist.push({ role: who === 'me' ? 'user' : 'assistant', content: txt });
    (links || []).forEach(function(x){ var a = el('a', '', x[0] + ' →'); a.href = x[1]; m.appendChild(a); });
    log.appendChild(m); log.scrollTop = log.scrollHeight;
  };
  var answer = function(i){ var e = KB[i]; say('bot', e.a, e.l); };
  QUICK.forEach(function(i){ var b = el('button', '', KB[i].q); b.type = 'button'; b.addEventListener('click', function(){ say('me', KB[i].q); answer(i); }); qk.appendChild(b); });
  var started = false;
  var open = function(o){
    pan.hidden = !o; btn.setAttribute('aria-expanded', o ? 'true' : 'false'); root.classList.toggle('on', o);
    if (o && !started) { started = true; say('bot', 'Bonjour, je réponds à vos questions sur le rapport, les tarifs et votre terrain. Choisissez une question ou écrivez la vôtre.'); }
    if (o) setTimeout(function(){ inp.focus(); }, 50);
  };
  btn.addEventListener('click', function(){ open(pan.hidden); });
  cl.addEventListener('click', function(){ open(false); });
  /* Conseil de formule selon le nombre de rapports (prix fixes, calcul exact) */
  var PK = [['unit', 1, 19.9, 'rapport à l\'unité'], ['pack2', 2, 29.8, 'lot de 2'], ['pack3', 3, 38.7, 'lot de 3'], ['pro10', 10, 149, '10 crédits'], ['pro30', 30, 357, '30 crédits'], ['pro100', 100, 790, '100 crédits']];
  var eu = function(v){ var r = Math.round(v * 100) / 100, e = Math.floor(r), c = Math.round((r - e) * 100); return String(e).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0') + (c ? ',' + String(c).padStart(2, '0') : '') + '\u00a0€'; };
  var conseilVolume = function(n){
    var M = n + 100, best = [0], how = [[]];
    for (var q = 1; q <= M; q++) { best[q] = Infinity; PK.forEach(function(k){ var r = Math.max(0, q - k[1]); if (best[r] + k[2] < best[q]) { best[q] = best[r] + k[2]; how[q] = how[r].concat([k]); } }); }
    var qty = function(L){ return L.reduce(function(a, k){ return a + k[1]; }, 0); };
    var desc = function(L){ var c = {}, o = []; L.forEach(function(k){ if (!c[k[3]]) o.push(k[3]); c[k[3]] = (c[k[3]] || 0) + 1; }); return o.map(function(x){ return (c[x] > 1 ? c[x] + ' × ' : '') + x; }).join(' + '); };
    if (n <= 3) return [n === 1 ? 'Pour 1 rapport : le rapport complet coûte 19,90 €.' : n === 2 ? 'Pour 2 rapports : le lot de 2 coûte 29,80 €, soit 14,90 € le rapport.' : 'Pour 3 rapports : le lot de 3 coûte 38,70 €, soit 12,90 € le rapport.', [['Vérifier un terrain', '/#recherche']]];
    var L = how[n], Q = qty(L), P = best[n];
    var combo = (L.length === 1 ? 'le pack de ' + desc(L) + ' à ' + eu(P) : desc(L) + ', soit ' + eu(P)) + (Q > n ? ' pour ' + Q + ' rapports' : '') + ' (' + eu(P / Q) + ' le rapport)';
    var up = PK.filter(function(k){ return k[1] >= 10 && k[1] >= n; })[0];
    var t, liens = [['Voir les tarifs', '/tarifs.html#pro']];
    if (n > 100) {
      t = 'Pour ' + n + ' rapports, nous établissons une offre personnalisée, plus avantageuse que nos formules : faites votre demande, nous répondons sous 24 heures ouvrées. À titre indicatif, le pack de 100 crédits est à 790 €, soit 7,90 € le rapport, sans limite de durée.';
      liens = [['Demander une offre', '/tarifs.html#offre']];
    } else if (up && up[2] <= P * 1.3 && up[3] !== desc(L)) {
      t = 'Notre conseil pour ' + n + ' rapports : le pack de ' + up[3] + ' à ' + eu(up[2]) + ', soit ' + eu(up[2] / up[1]) + ' le rapport' + (up[1] > n ? ' ; les ' + (up[1] - n) + ' rapports en plus restent sur votre compte, sans limite de durée' : '') + '. Au plus juste : ' + combo + '.';
    } else {
      t = 'Notre conseil pour ' + n + ' rapports : ' + combo + (Q > n ? ' ; le rapport en plus reste sur votre compte, sans limite de durée' : '') + '.';
      if (up && up[2] / up[1] < P / Q - 0.5) t += ' Si vous prévoyez d\'autres terrains : ' + up[3] + ' à ' + eu(up[2]) + ', soit ' + eu(up[2] / up[1]) + ' le rapport, sans limite de durée.';
    }
    if (n <= 100) {
      var ab = n <= 10 ? [10, 129] : n <= 30 ? [30, 297] : null;
      if (ab) t += ' Besoin chaque mois ? L\'abonnement de ' + ab[0] + ' rapports par mois revient à ' + eu(ab[1] / ab[0]) + ' le rapport (' + eu(ab[1]) + ' par mois, sans engagement).';
      else { t += ' Pour un besoin régulier de plus de 30 rapports par mois, nous établissons une offre personnalisée.'; liens.push(['Demander une offre', '/tarifs.html#offre']); }
    }
    return [t, liens];
  };
  var busy = false;
  fm.addEventListener('submit', function(ev){
    ev.preventDefault(); var t = inp.value.trim(); if (!t || busy) return; inp.value = ''; say('me', t);
    var nv = (norm(t).match(/(\d{1,4}) ?(rapports?|credits?|parcelles?|terrains?|dossiers?|biens?|analyses?)/) || [])[1];
    if (nv && +nv > 0) { var cv = conseilVolume(+nv); say('bot', cv[0], cv[1]); return; }
    var fallback = function(){ var i = find(t); if (i >= 0) answer(i); else say('bot', 'Je n\'ai pas de réponse précise à cette question. Écrivez-nous à contact@terrenurbanisme.com : nous répondons sous 24 heures ouvrées.', [['Voir la FAQ', '/faq.html']]); };
    var dots = el('div', 'tu-bot-m bot tu-bot-typing'); dots.innerHTML = '<span></span><span></span><span></span>'; log.appendChild(dots); log.scrollTop = log.scrollHeight; busy = true; go.disabled = true;
    var C = window.TU_CONFIG || {};
    fetch((C.supabaseUrl || 'https://nmoigruxnhsidrhqtzid.supabase.co') + '/functions/v1/stripe-webhook?assistant=1', { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=UTF-8' }, body: JSON.stringify({ page: location.pathname, messages: hist.slice(-8) }) })
      .then(function(r){ return r.json(); })
      .then(function(j){ dots.remove(); if (j && j.reply) say('bot', j.reply); else fallback(); })
      .catch(function(){ dots.remove(); fallback(); })
      .then(function(){ busy = false; go.disabled = false; });
  });
  document.body.appendChild(root);
})();

/* ---------- Blog : articles programmés (un par jour à 17 h) et filtre par thématique ---------- */
(function(){
  var grid = document.getElementById('bgrid'); if (!grid) return;
  var esc = function(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var tabs = document.querySelectorAll('.btabs [data-f]'), cur = 'tous';
  var apply = function(f){ cur = f; tabs.forEach(function(t){ var on = t.getAttribute('data-f') === f; t.classList.toggle('on', on); t.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    grid.classList.toggle('f', f !== 'tous'); var n = 0; grid.querySelectorAll('.bc').forEach(function(c){ var ok = f === 'tous' || c.getAttribute('data-cat') === f; c.hidden = !ok; if (ok) n++; });
    var e = document.getElementById('bempty'); if (e) e.hidden = n > 0; };
  tabs.forEach(function(t){ t.addEventListener('click', function(){ var f = t.getAttribute('data-f'); apply(f); try { history.replaceState(null, '', f === 'tous' ? location.pathname : '#' + f); } catch (e) {} }); });
  var h = (location.hash || '').slice(1); if (h && document.querySelector('.btabs [data-f="' + h + '"]')) apply(h);
  fetch('/blog/a-paraitre.json', { cache: 'no-store' }).then(function(r){ return r.ok ? r.json() : []; }).then(function(L){
    var now = Date.now();
    L.filter(function(a){ return Date.parse(a.pub) <= now; }).forEach(function(a){
      if (document.querySelector('a.bc[href="/blog/' + a.slug + '.html"]')) return;
      grid.insertAdjacentHTML('afterbegin', '<a class="bc" data-cat="' + esc(a.cat) + '" href="/blog/' + esc(a.slug) + '.html"><span class="bc-img"><img src="/assets/blog/' + esc(a.slug) + '-m.webp" width="800" height="450" loading="lazy" alt="' + esc(a.title) + '"></span><span class="bc-t"><span class="blog-tag">' + esc(a.catn) + '</span><strong>' + esc(a.title) + '</strong><span class="blog-ex">' + esc(a.desc) + '</span><span class="bc-m"><span>' + esc(a.date) + ' · ' + a.min + ' min</span><span class="bc-go">Lire l\'article →</span></span></span></a>');
    });
    apply(cur);
  }).catch(function(){});
})();

/* ---------- Menu déroulant : mobile (accordéon), clavier, page courante, en-tête au défilement ---------- */
(function(){
  document.querySelectorAll('.dd').forEach(function(d){
    var b = d.querySelector('.dd-t');
    b.addEventListener('click', function(){
      if (window.matchMedia('(min-width:1181px)').matches) return;
      var o = d.classList.toggle('open'); b.setAttribute('aria-expanded', o ? 'true' : 'false');
    });
  });
  var here = location.pathname.replace(/index\.html$/, '');
  document.querySelectorAll('.menu a[href]').forEach(function(a){ var hr = a.getAttribute('href'), h = hr.split('#')[0]; if (hr.indexOf('#') < 0 && h && h !== '/' && h === here) { a.setAttribute('aria-current', 'page'); var dd = a.closest('.dd'); if (dd) dd.querySelector('.dd-t').classList.add('cur'); } });
  var top = document.querySelector('.top'); if (!top) return;
  var tick = false; var onS = function(){ if (tick) return; tick = true; requestAnimationFrame(function(){ top.classList.toggle('scrolled', window.scrollY > 8); tick = false; }); };
  window.addEventListener('scroll', onS, { passive: true }); onS();
})();

/* ---------- Avis clients (accueil) : affichés seulement quand de vrais avis existent dans /avis.json ---------- */
(function(){
  var sec = document.getElementById('avis'), g = document.getElementById('avis-g'); if (!sec || !g) return;
  var esc = function(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  fetch('/avis.json', { cache: 'no-store' }).then(function(r){ return r.ok ? r.json() : []; }).then(function(L){
    if (!L || !L.length) return;
    g.innerHTML = L.slice(0, 6).map(function(a){ var n = Math.max(1, Math.min(5, a.note || 5)); return '<figure class="avis-c"><div class="avis-n" aria-label="' + n + ' sur 5">' + '★★★★★'.slice(0, n) + '<span>' + '★★★★★'.slice(n) + '</span></div><blockquote>' + esc(a.texte) + '</blockquote><figcaption><b>' + esc(a.nom) + '</b>' + (a.ville ? ' · ' + esc(a.ville) : '') + (a.date ? '<span>' + esc(a.date) + '</span>' : '') + '</figcaption></figure>'; }).join('');
    sec.hidden = false;
  }).catch(function(){});
})();

/* ---------- Rapport d'exemple : chapitre courant dans le sommaire ---------- */
(function(){
  var nav = document.querySelector('.rp-nav'); if (!nav || !('IntersectionObserver' in window)) return;
  var links = {}; nav.querySelectorAll('a').forEach(function(a){ links[a.getAttribute('href').slice(1)] = a; });
  var io = new IntersectionObserver(function(es){ es.forEach(function(e){ if (e.isIntersecting && links[e.target.id]) { nav.querySelectorAll('a.on').forEach(function(x){ x.classList.remove('on'); }); var a = links[e.target.id]; a.classList.add('on'); if (nav.scrollWidth > nav.clientWidth) nav.scrollLeft = a.offsetLeft - 20; } }); }, { rootMargin: '-40% 0px -55% 0px' });
  document.querySelectorAll('.rp-ch').forEach(function(c){ io.observe(c); });
})();

/* ---------- Article : sommaire actif, copie du lien ---------- */
(function(){
  document.querySelectorAll('.bs-cp').forEach(function(b){ b.addEventListener('click', function(){
    var u = b.getAttribute('data-url'), done = function(){ b.classList.add('ok'); setTimeout(function(){ b.classList.remove('ok'); }, 1600); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(done, function(){});
    else { var t = document.createElement('textarea'); t.value = u; document.body.appendChild(t); t.select(); try { document.execCommand('copy'); done(); } catch (e) {} t.remove(); }
  }); });
  var toc = document.querySelector('.ba-toc'); if (!toc || !('IntersectionObserver' in window)) return;
  var map = {}; toc.querySelectorAll('a').forEach(function(a){ map[a.getAttribute('href').slice(1)] = a; });
  var io = new IntersectionObserver(function(es){ es.forEach(function(e){ if (e.isIntersecting && map[e.target.id]) { toc.querySelectorAll('a.on').forEach(function(x){ x.classList.remove('on'); }); map[e.target.id].classList.add('on'); } }); }, { rootMargin: '-20% 0px -70% 0px' });
  document.querySelectorAll('.ba-c h2[id]').forEach(function(h){ io.observe(h); });
})();

/* ---------- Copier une adresse e-mail ---------- */
(function(){
  document.querySelectorAll('[data-copy]').forEach(function(b){ b.addEventListener('click', function(){
    var t = b.getAttribute('data-copy'), old = b.textContent, ok = function(){ b.textContent = 'Adresse copiée'; setTimeout(function(){ b.textContent = old; }, 1600); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, function(){});
  }); });
})();

/* ---------- Parcours d'achat : motif, remise de bienvenue, e-mail avant paiement, page de remise ---------- */
(function(){
  var cfg = window.TU_CONFIG || {}, A = function(){ return window.TUAuth; };
  var FN = (cfg.supabaseUrl || '') + '/functions/v1/stripe-webhook';
  var esc = function(t){ return String(t == null ? '' : t).replace(/[&<>"]/g, function(c){ return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var ls = { get: function(k){ try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function(k, v){ try { localStorage.setItem(k, v); } catch (e) {} } };
  var ss = { get: function(k){ try { return sessionStorage.getItem(k); } catch (e) { return null; } }, set: function(k, v){ try { if (v == null) sessionStorage.removeItem(k); else sessionStorage.setItem(k, v); } catch (e) {} } };
  var post = function(q, body){ return fetch(FN + '?' + q, { method: 'POST', headers: { 'Content-Type': 'application/json', apikey: cfg.supabaseKey || '', Authorization: 'Bearer ' + (cfg.supabaseKey || '') }, body: JSON.stringify(body) }).then(function(r){ return r.json().catch(function(){ return {}; }).then(function(j){ j.status = r.status; return j; }); }); };
  var EMAIL = /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i;
  var ICO = {
    key: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3M14 9l2 2"/></svg>',
    pct: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 5L5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/></svg>',
    map: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/></svg>',
    ok: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    g: '<svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.5l6.8-6.8C35.6 2.4 30.2 0 24 0 14.6 0 6.6 5.4 2.6 13.3l7.9 6.1C12.4 13.7 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.1 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.4c-.5 2.9-2.2 5.3-4.6 6.9l7.4 5.8c4.3-4 6.9-9.9 6.9-17.2z"/><path fill="#FBBC05" d="M10.5 28.6c-.5-1.4-.8-2.9-.8-4.6s.3-3.2.8-4.6l-7.9-6.1C1 16.6 0 20.2 0 24s1 7.4 2.6 10.7l7.9-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.4-5.8c-2.1 1.4-4.8 2.3-8.5 2.3-6.3 0-11.6-4.2-13.5-10l-7.9 6.1C6.6 42.6 14.6 48 24 48z"/></svg>',
    ap: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.5 2-3.7 2.1-3.8-1.2-1.7-3-1.9-3.6-2-1.5-.2-3 .9-3.8.9-.8 0-2-.9-3.3-.9-1.7 0-3.3 1-4.2 2.6-1.8 3.1-.5 7.7 1.3 10.2.9 1.2 1.9 2.6 3.2 2.6 1.3-.1 1.8-.8 3.3-.8 1.6 0 2 .8 3.4.8 1.4 0 2.3-1.3 3.1-2.5 1-1.4 1.4-2.8 1.4-2.9 0 0-2.9-1.1-2.9-4.2zM13.9 5.2c.7-.8 1.2-2 1-3.2-1 .1-2.2.7-2.9 1.5-.7.7-1.3 1.9-1.1 3.1 1.1.1 2.3-.6 3-1.4z"/></svg>'
  };
  function modal(cls, html){
    var w = document.createElement('div'); w.className = 'fm ' + (cls || ''); w.setAttribute('role', 'dialog'); w.setAttribute('aria-modal', 'true');
    w.innerHTML = '<div class="fm-bg" data-close></div><div class="fm-box"><button type="button" class="fm-x" aria-label="Fermer" data-close>&#10005;</button>' + html + '</div>';
    document.body.appendChild(w); document.documentElement.classList.add('fm-open');
    requestAnimationFrame(function(){ w.classList.add('on'); });
    var done = [], close = function(v){ w.classList.remove('on'); document.documentElement.classList.remove('fm-open'); setTimeout(function(){ w.remove(); }, 200); document.removeEventListener('keydown', kd); done.forEach(function(f){ f(v); }); };
    var kd = function(e){ if (e.key === 'Escape') close('ferme'); };
    document.addEventListener('keydown', kd);
    w.querySelectorAll('[data-close]').forEach(function(b){ b.addEventListener('click', function(){ close('ferme'); }); });
    return { el: w, close: close, onClose: function(f){ done.push(f); } };
  }

  /* 1. Après le diagnostic : pourquoi vérifiez-vous ce terrain ? */
  var MOT = [['achat', 'J\'achète un terrain', 'achat'], ['vente', 'Je vends un terrain', 'achat'], ['construire', 'Je veux construire', 'maison'], ['pro', 'Je suis un professionnel', '']];
  function motif(parcel){
    if (ss.get('tu_motif_vu')) return Promise.resolve(ls.get('tu_motif'));
    return new Promise(function(res){
      var m = modal('fm-mot', '<div class="fm-ic">' + ICO.map + '</div><h2>Pourquoi vérifiez-vous ce terrain ?</h2><p>Aidez-nous à préparer votre rapport : cela ne prend qu\'un instant.</p>' +
        '<div class="fm-opts" role="radiogroup">' + MOT.map(function(x){ return '<button type="button" role="radio" aria-checked="false" data-m="' + x[0] + '">' + x[1] + '</button>'; }).join('') + '</div>' +
        '<button type="button" class="btn fm-go" disabled>Continuer <span aria-hidden="true">→</span></button>');
      var sel = '';
      m.el.querySelectorAll('[data-m]').forEach(function(b){ b.addEventListener('click', function(){ sel = b.getAttribute('data-m'); m.el.querySelectorAll('[data-m]').forEach(function(x){ x.setAttribute('aria-checked', x === b ? 'true' : 'false'); }); m.el.querySelector('.fm-go').disabled = false; }); });
      m.el.querySelector('.fm-go').addEventListener('click', function(){ m.close(sel); });
      m.onClose(function(v){
        ss.set('tu_motif_vu', '1');
        if (v && v !== 'ferme'){
          ls.set('tu_motif', v);
          var map = MOT.filter(function(x){ return x[0] === v; })[0];
          var chip = map && map[2] && document.querySelector('.v-chips button[data-p="' + map[2] + '"]');
          if (chip && chip.getAttribute('aria-pressed') !== 'true') chip.click();
          if (A() && A().track) A().track('motif', { insee: parcel && parcel.insee, motif: v });
          if (v === 'pro'){ var r = document.getElementById('result'); if (r && !r.querySelector('.v-pro-hint')){ var d = document.createElement('p'); d.className = 'v-pro-hint'; d.innerHTML = 'Professionnel : <a href="/tarifs.html#pro">dès 7,90 € le rapport, à votre marque</a>'; var o = r.querySelector('.v-offer'); if (o) o.parentNode.insertBefore(d, o); } }
        }
        var off = document.querySelector('#result .v-offer'); if (off) off.scrollIntoView({ behavior: 'smooth', block: 'center' });
        res(v);
      });
    });
  }

  /* 2. Remise de bienvenue de 15 %, envoyée par e-mail */
  var remTimer = null, remParcel = null;
  function remise(parcel){
    if (ls.get('tu_rem_vu')) return;
    ls.set('tu_rem_vu', String(Date.now()));
    var m = modal('fm-rem', '<div class="fm-ic fm-ic-big">' + ICO.pct + '</div><div class="fm-s1"><h2>Souhaitez-vous recevoir 15 % de remise ?</h2><p>Sur le rapport complet de votre terrain, ou sur un lot de 2 ou 3 rapports.</p><div class="fm-2"><button type="button" class="btn" data-s="oui">Oui</button><button type="button" class="btn ghost" data-s="tard">La garder pour plus tard</button></div><button type="button" class="fm-no" data-close>Non merci, je préfère payer le plein tarif</button></div>' +
      '<form class="fm-s2" hidden novalidate><h2>−15 % dès maintenant</h2><p>Indiquez votre e-mail : nous vous envoyons votre remise, valable 14 jours.</p><label class="fm-in">' + ICO.mail + '<input type="email" name="email" placeholder="nom@exemple.fr" autocomplete="email" required></label><input type="text" name="site_web" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true"><button type="submit" class="btn">Obtenir −15 %</button><p class="fm-err" role="alert"></p><p class="fm-legal">En validant, vous acceptez de recevoir nos e-mails : remise, conseils et offres. Désinscription en un clic. <a href="/confidentialite.html" target="_blank">Confidentialité</a></p></form>' +
      '<div class="fm-s3" hidden><div class="fm-ic fm-ic-ok">' + ICO.ok + '</div><h2>C\'est envoyé !</h2><p>Votre remise de 15 % vient d\'être envoyée à <b class="fm-to"></b>. Ouvrez l\'e-mail et cliquez sur « Activer ma remise ».</p><button type="button" class="btn" data-close>Fermer</button></div>');
    var s1 = m.el.querySelector('.fm-s1'), s2 = m.el.querySelector('.fm-s2'), s3 = m.el.querySelector('.fm-s3');
    m.el.querySelectorAll('[data-s]').forEach(function(b){ b.addEventListener('click', function(){ s1.hidden = true; s2.hidden = false; s2.email.focus(); }); });
    s2.addEventListener('submit', function(e){
      e.preventDefault(); var em = s2.email.value.trim(), er = s2.querySelector('.fm-err'), bt = s2.querySelector('button');
      if (!EMAIL.test(em)){ er.textContent = 'Indiquez une adresse e-mail valide.'; return; }
      er.textContent = ''; bt.disabled = true; bt.textContent = 'Envoi…';
      lead(em, 'remise', null, parcel || remParcel, false);
      var p = parcel || remParcel || {};
      post('remise=1', { email: em, site_web: s2.site_web.value, insee: p.insee, section: p.section, numero: p.numero, commune: p.commune, motif: ls.get('tu_motif') || '' }).then(function(j){
        if (j.ok){ ls.set('tu_email', em); s2.hidden = true; s3.hidden = false; s3.querySelector('.fm-to').textContent = em; if (A() && A().track) A().track('remise', { insee: p.insee }); return; }
        er.textContent = j.error === 'limite' ? 'Trop de demandes depuis cette connexion. Réessayez dans une heure.' : 'L\'envoi n\'a pas abouti. Vérifiez votre adresse et réessayez.';
        bt.disabled = false; bt.textContent = 'Obtenir −15 %';
      }).catch(function(){ er.textContent = 'L\'envoi n\'a pas abouti. Réessayez dans un instant.'; bt.disabled = false; bt.textContent = 'Obtenir −15 %'; });
    });
  }
  function armRemise(parcel){
    remParcel = parcel;
    if (ls.get('tu_rem_vu') || !A() || !A().ready) return;
    A().user().then(function(u){
      if (u) return;
      clearTimeout(remTimer);
      remTimer = setTimeout(function(){ if (!document.querySelector('.fm')) remise(parcel); }, 25000);
      var exit = function(e){ if (e.clientY <= 0 && !document.querySelector('.fm')){ document.removeEventListener('mouseout', exit); clearTimeout(remTimer); remise(parcel); } };
      if (window.matchMedia('(pointer:fine)').matches) document.addEventListener('mouseout', exit);
    }).catch(function(){});
  }

  /* E-mails saisis dans le tunnel : enregistrés pour le suivi et le mailing (offres seulement si la case est cochée) */
  function lead(em, src, kind, parcel, offres){
    try { var c = A() && A().client; if (!c) return;
      c.rpc('enregistrer_lead', { p_email: em, p_source: src, p_kind: kind || null, p_parcelle: parcel ? { insee: parcel.insee, section: parcel.section, numero: parcel.numero, commune: parcel.commune } : null, p_offres: !!offres }).then(function(){}, function(){});
    } catch (e) {}
  }
  /* 3. Avant le paiement : où envoyer le rapport ? (e-mail, Google) */
  function emailStep(kind, parcel, rem){
    return new Promise(function(res){
      var soc = cfg.google && window.TUGoogleBtn ? '<div class="fm-gsi off"><div class="gsi-box"></div></div>' : '';
      var back = location.pathname + location.search;
      var m = modal('fm-mail', '<form novalidate><h2>Où devons-nous envoyer votre rapport ?</h2><p class="fm-acc">Vous avez déjà un compte ? <a href="/connexion.html?redirect=' + encodeURIComponent(back) + '">Se connecter</a></p>' +
        '<label class="fm-in">' + ICO.mail + '<input type="email" name="email" placeholder="nom@exemple.fr" autocomplete="email" required value="' + esc((rem && rem.email) || ls.get('tu_email') || '') + '"></label>' +
        '<label class="fm-ck"><input type="checkbox" name="offres"><span>Recevoir nos conseils et offres par e-mail (désinscription en un clic).</span></label>' +
        '<label class="fm-ck"><input type="checkbox" name="cgv" required><span>J\'accepte les <a href="/cgv.html" target="_blank">conditions générales de vente</a> et j\'ai lu la <a href="/confidentialite.html" target="_blank">politique de confidentialité</a>.</span></label>' +
        '<button type="submit" class="btn fm-dark">Continuer</button><p class="fm-err" role="alert"></p>' +
        (soc ? '<div class="fm-or"><span>ou continuer avec</span></div>' + soc : '') + '<p class="fm-legal">Paiement sécurisé par Stripe. Rapport envoyé par e-mail en quelques minutes.</p></form>');
      var f = m.el.querySelector('form'), er = m.el.querySelector('.fm-err'), bt = f.querySelector('button[type=submit]');
      var body = Object.assign({}, parcel || {}); if (rem && rem.token) body.remise = rem.token;
      m.el.querySelectorAll('.fm-mot2 [data-m]').forEach(function(b){ b.addEventListener('click', function(){
        var v = b.getAttribute('data-m'); ls.set('tu_motif', v);
        m.el.querySelectorAll('.fm-mot2 [data-m]').forEach(function(x){ x.setAttribute('aria-checked', x === b ? 'true' : 'false'); });
        if (A() && A().track) A().track('motif', { insee: parcel && parcel.insee, motif: v });
      }); });
      f.addEventListener('submit', function(e){
        e.preventDefault(); var em = f.email.value.trim();
        if (!EMAIL.test(em)){ er.textContent = 'Indiquez une adresse e-mail valide.'; f.email.focus(); return; }
        if (!f.cgv.checked){ er.textContent = 'Merci d\'accepter les conditions générales de vente pour continuer.'; return; }
        er.textContent = ''; bt.disabled = true; bt.textContent = 'Redirection vers le paiement…'; ls.set('tu_email', em); body.email = em;
        lead(em, 'paiement', kind, parcel, f.offres.checked);
        A().checkout(kind, body).catch(function(){ er.textContent = 'Le paiement n\'a pas pu s\'ouvrir. Réessayez dans un instant.'; bt.disabled = false; bt.textContent = 'Continuer'; });
      });
      var gw = m.el.querySelector('.fm-gsi');
      if (gw){
        var sync = function(){ gw.classList.toggle('off', !f.cgv.checked); };
        f.cgv.addEventListener('change', sync);
        gw.addEventListener('click', function(){ if (!f.cgv.checked) er.textContent = 'Merci d\'accepter les conditions générales de vente pour continuer.'; }, true);
        window.TUGoogleBtn(gw.querySelector('.gsi-box'), A().client, function(d){
          if (d && d.user && d.user.email) lead(d.user.email, 'google', kind, parcel, f.offres.checked);
          er.textContent = ''; bt.disabled = true; bt.textContent = 'Redirection vers le paiement…';
          A().checkout(kind, body).catch(function(){ er.textContent = 'Le paiement n\'a pas pu s\'ouvrir. Réessayez dans un instant.'; bt.disabled = false; bt.textContent = 'Continuer'; });
        }, function(){ er.textContent = 'La connexion Google a échoué. Réessayez, ou indiquez votre e-mail.'; });
      }
      m.onClose(function(v){ res(v); });
    });
  }
  // Retour de Google ou d'Apple : le paiement reprend tout seul
  (function(){
    var p = ss.get('tu_pending'); if (!p) return;
    try { p = JSON.parse(p); } catch (e) { ss.set('tu_pending', null); return; }
    ss.set('tu_pending', null);
    if (!p || Date.now() - p.t > 900000) return;
    var go = function(){ if (!A() || !A().ready) return; A().user().then(function(u){ if (u) A().checkout(p.kind, p.body); }); };
    if (document.readyState === 'complete') setTimeout(go, 600); else window.addEventListener('load', function(){ setTimeout(go, 600); });
  })();

  window.TUFunnel = {
    afterDiag: function(parcel){ armRemise(parcel); },
    email: emailStep, remise: remise
  };

  /* 4. Page de la remise (lien reçu par e-mail) */
  var app = document.getElementById('offre-app'); if (!app) return;
  var tk = (new URLSearchParams(location.search).get('r') || '').replace(/[^a-f0-9]/gi, '');
  var OFF = [{ k: 'pack3', n: 3, a: 3870, tag: 'Le plus populaire' }, { k: 'pack2', n: 2, a: 2980 }, { k: 'unit', n: 1, a: 1990 }];
  var eur = function(c){ return (c / 100).toFixed(2).replace('.', ',') + ' €'; };
  var info = null, kind = 'pack3';
  function render(){
    var ok = info && info.ok;
    var ban = document.getElementById('offre-ban');
    if (ok){ ban.hidden = false; ban.className = 'of-ban'; ban.innerHTML = '<span class="of-bi">' + ICO.ok + '</span><span>Votre <b>remise de ' + (info.taux || 15) + ' %</b> est appliquée, jusqu\'au ' + new Date(info.expire_le).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' }) + '.</span>'; }
    else if (tk){ ban.hidden = false; ban.className = 'of-ban of-ban-off'; ban.innerHTML = '<span>' + (info && info.utilise ? 'Cette remise a déjà été utilisée.' : 'Ce lien de remise a expiré ou n\'est plus valable.') + ' Les tarifs ci-dessous sont les tarifs habituels.</span>'; }
    if (info && info.insee){ var pb = document.getElementById('offre-parc'); pb.hidden = false; pb.querySelector('span').textContent = info.commune + ' · section ' + info.section + ' · parcelle ' + info.numero; }
    document.getElementById('offre-cards').innerHTML = OFF.map(function(o){
      var full = 1990 * o.n, tot = ok ? Math.round(o.a * (100 - (info.taux || 15)) / 100) : o.a, pr = Math.round(tot / o.n), pct = Math.round((1 - tot / full) * 100);
      return '<label class="of-c' + (o.k === kind ? ' on' : '') + '">' + (o.tag ? '<span class="of-tag">' + o.tag + '</span>' : '') + '<input type="radio" name="of-k" value="' + o.k + '"' + (o.k === kind ? ' checked' : '') + '>' +
        '<span class="of-h"><i class="of-box">' + ICO.ok + '</i><span><b>Vérifier ' + o.n + ' terrain' + (o.n > 1 ? 's' : '') + '</b><small>Un rapport complet d\'environ 45 pages pour chaque terrain</small></span></span>' +
        '<span class="of-p"><b>' + eur(pr) + '</b> / rapport</span><span class="of-t">Prix total <b>' + eur(tot) + '</b>' + (tot < full ? ' <s>' + eur(full) + '</s>' : '') + '</span>' +
        (ok ? '<span class="of-ok">' + ICO.ok + ' Remise appliquée</span>' : '') + (pct > 0 ? '<span class="of-pct">Remise totale ' + pct + ' %</span>' : '') +
        '<span class="of-li">' + ICO.ok + ' Vous obtiendrez ' + o.n + ' rapport' + (o.n > 1 ? 's' : '') + (o.n > 1 ? ', sans limite de durée' : '') + '</span><span class="of-li">' + ICO.ok + ' Régénéré sans frais pendant 30 jours si une source manque</span></label>';
    }).join('');
    app.querySelectorAll('input[name="of-k"]').forEach(function(r){ r.addEventListener('change', function(){ kind = r.value; app.querySelectorAll('.of-c').forEach(function(c){ c.classList.toggle('on', c.querySelector('input').checked); }); }); });
  }
  var go = function(){
    var parcel = info && info.insee ? { insee: info.insee, section: info.section, numero: info.numero, commune: info.commune } : {};
    var rem = info && info.ok ? { token: tk, email: info.email } : null;
    if (!A() || !A().ready) return;
    A().user().then(function(u){ if (u) return A().checkout(kind, Object.assign({}, parcel, rem ? { remise: rem.token } : {})); return emailStep(kind, parcel, rem); });
  };
  document.querySelectorAll('[data-of-go]').forEach(function(b){ b.addEventListener('click', go); });
  render();
  if (tk) post('remise=info', { r: tk }).then(function(j){ info = j; render(); }).catch(function(){ info = { ok: false }; render(); });
})();

/* ---------- Désinscription des e-mails ---------- */
(function(){
  var t = document.getElementById('des-t'); if (!t) return;
  var cfg = window.TU_CONFIG || {}, p = document.getElementById('des-p'), tk = (new URLSearchParams(location.search).get('r') || '').replace(/[^a-f0-9]/gi, '');
  if (!tk){ p.textContent = 'Ce lien de désinscription n\'est pas valable.'; return; }
  fetch(cfg.supabaseUrl + '/functions/v1/stripe-webhook?remise=info', { method: 'POST', headers: { 'Content-Type': 'application/json', apikey: cfg.supabaseKey, Authorization: 'Bearer ' + cfg.supabaseKey }, body: JSON.stringify({ r: tk, desinscription: true }) }).then(function(r){ return r.json(); }).then(function(j){
    p.textContent = j && j.desinscrit ? 'C\'est fait : vous ne recevrez plus nos e-mails d\'information. Les e-mails liés à vos commandes (rapports, factures) restent envoyés.' : 'Ce lien de désinscription n\'est pas valable. Écrivez-nous à contact@terrenurbanisme.com.';
  }).catch(function(){ p.textContent = 'La désinscription n\'a pas abouti. Réessayez ou écrivez-nous à contact@terrenurbanisme.com.'; });
})();
