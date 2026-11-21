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
    return fetch(GEO+'/communes?nom='+encodeURIComponent(q)+'&fields=nom,code,codeDepartement,population&boost=population&limit='+(limit||8), ctl ? { signal: ctl.signal } : {})
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
    /* Dès que la commune est choisie, la carte se centre dessus */
    var lastGeo = '';
    function geoCommune(){
      var v = $('com').value.trim(); if (!v || v === lastGeo) return;
      resolveCommune(v).then(function(code){
        if (!code || v === lastGeo) return; lastGeo = v;
        return getJSON(GEO+'/communes/'+code+'?fields=centre,contour').then(function(c){
          var m = map || big; if (!m || !window.L) return;
          try {
            if (c.contour){ m.fitBounds(L.geoJSON(c.contour).getBounds(), { padding:[20,20], maxZoom:15 }); }
            else if (c.centre){ m.setView([c.centre.coordinates[1], c.centre.coordinates[0]], 14); }
            if (big && m !== big && c.centre) big.setView([c.centre.coordinates[1], c.centre.coordinates[0]], 14);
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
        if (!sec || !num){ errEl.textContent = 'Indiquez la section (une ou deux lettres) et le numéro de la parcelle.'; return; }
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
      if (inPlace && qs.get('section') && qs.get('numero')) communeIndex().then(function(i){ idx = i; form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit')); });
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

  /* ---------- Carte du héros ---------- */
  var map = null, layer = null, scope = $('scope');
  var small = function(){ return window.innerWidth <= 620; };
  if (scope && window.L){
    try {
      map = L.map('map', { zoomControl:false, scrollWheelZoom:false, dragging:true, tap:true, attributionControl:true, maxZoom:20 }).setView([46.6, 2.4], 6);
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
          return { code: f.properties.libelle || f.properties.typezone, tz: f.properties.typezone, lib: f.properties.libelong || '', share: sh };
        }).filter(function(z){ return z.share == null || z.share >= 0.02; }).sort(function(a, b){ return (b.share || 0) - (a.share || 0); }) : null;
        var sups = r[2] ? (r[2].features || []).map(function(f){ return String(f.properties.suptype || f.properties.typeass || '').toLowerCase(); }) : null;
        var cd = r[3] ? (r[3][insee] || {}) : null;
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
    var OFFER = '<div class="v-offer" role="radiogroup" aria-label="Nombre de rapports"><div class="v-offer-top"><b class="v-offer-u">' + OFF[kind].u + '</b> <span>/ rapport</span><div class="v-offer-t">Prix total ' + OFF[kind].t + '</div></div>' +
      opt('unit', 'Rapport complet', '', '<span class="v-opt-tag">Recommandé pour acheter, vendre ou construire</span>Environ 45 pages, tout pour décider :<span class="v-opt-ul"><span>Ce que vous pouvez construire : surface, hauteur, emprise, implantation d\'une maison</span><span>Le règlement du PLU lu pour vous, avec les extraits officiels</span><span>Risques, servitudes, loi Littoral, patrimoine et architecte des Bâtiments de France</span><span>Eau, électricité, assainissement : coûts et démarches de raccordement</span><span>Ventes réelles autour du terrain et photos aériennes depuis 1950</span><span>Démarches, délais, taxe d\'aménagement et état des risques pour la vente</span></span>') + '<div class="v-opt-sep">Plusieurs biens ? Rapports complets moins chers</div>' + opt('pack2', '2 rapports complets', '−25 %') + opt('pack3', '3 rapports complets', '−35 %') +
      '<p class="v-opt-note">Lots : le premier rapport porte sur cette parcelle, les autres restent sur votre compte, sans limite de durée.</p></div>';
    resultEl.innerHTML =
      '<div class="v-ref">' + esc(ref) + '</div>' +
      '<span class="v-badge v-found"><i></i>Parcelle trouvée</span>' +
      '<div class="v-title">Votre diagnostic</div>' +
      '<p class="v-other">Ce n\'est pas la bonne parcelle ? Cliquez sur une autre parcelle de la carte.</p>' +
      '<p class="v-why">Nous avons trouvé cette parcelle et les sources officielles qui la concernent. Le rapport complet répond à la question : peut-on construire, et à quelles conditions ?</p>' +
      '<div class="v-proj"><b>Quel est votre projet ?</b><span>Le rapport sera présenté pour lui.</span><div class="v-chips" role="group" aria-label="Votre projet">' + PROJ.map(function(x){ return '<button type="button" data-p="' + x[0] + '" aria-pressed="' + (x[0] === projet() ? 'true' : 'false') + '">' + x[1] + '</button>'; }).join('') + '</div></div>' +
      (noZone ? '<p class="v-disc" style="background:#FBF1E1;border:1.5px solid #E2B66B;border-radius:12px;padding:12px 14px;color:#5A3A06"><strong>Attention : la zone de cette parcelle n\'est pas disponible.</strong><br> cette commune dispose d\'un document d\'urbanisme mais ne l\'a pas encore mis en ligne sur le Géoportail de l\'Urbanisme, la plateforme officielle de l\'État. Aucun service ne peut donc lire sa zone automatiquement : elle est à vérifier en mairie (plan de zonage) ou par un certificat d\'urbanisme. Le rapport réunit toutes les autres données officielles de la parcelle (risques, servitudes, PADDUC, lois Littoral et Montagne, accès, réseaux, prix du marché) mais <strong>n\'indiquera pas la zone ni son règlement</strong>.</p>' : '') +
      OFFER + '<button type="button" class="v-cta v-cta-top buy">' + BTN + '</button><p class="v-buy-err" role="alert"></p>' +
      '<ul class="v-found-list">' + found.map(function(f){ return '<li>' + (f[0] === 'warn' ? WARNI : OKI) + '<div><strong>' + esc(f[1]) + '</strong><span>' + esc(f[2]) + '</span></div></li>'; }).join('') + '</ul>' +
      '<ul class="v-locked">' + locked.map(function(t){ return '<li>' + LOCK + '<span>' + esc(t) + '</span><i class="blur" aria-hidden="true">████████</i></li>'; }).join('') + '</ul>' +
      '<button type="button" class="v-cta buy">' + BTN + '</button>' +
      '<p class="v-buy-note">Rapport complet d\'environ 45 pages, avec sommaire cliquable, envoyé par e-mail en quelques minutes · paiement sécurisé par Stripe<br><a href="/tarifs.html">Professionnels : dès 39 € par mois pour 10 rapports</a> · <a href="/exemple.html">Voir un exemple</a></p><p class="v-buy-err" role="alert"></p>' +
      '<p class="v-disc">Information indicative, établie à partir des sources publiques consultées à la date de la recherche. Elle ne vaut ni certificat d\'urbanisme, ni autorisation, ni avis juridique : seule la mairie peut confirmer la constructibilité de la parcelle.</p>' +
      '<a class="v-owner" href="https://france-cadastre.fr/" target="_blank" rel="noopener">Connaître le propriétaire de cette parcelle <span>via France Cadastre ↗</span></a>';
    var parcelRef = { insee:inseeOf(p), commune:(inseeOf(p) !== p.code_insee ? arrLabel(p) : p.nom_com), section:sec, numero:num };
    if (projet()) parcelRef.projet = projet();
    resultEl.querySelectorAll('.v-chips button').forEach(function(b){ b.addEventListener('click', function(){
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
      if (!r.checked) return; kind = r.value; offerEl.querySelector('.v-offer-u').textContent = OFF[kind].u; offerEl.querySelector('.v-offer-t').textContent = 'Prix total ' + OFF[kind].t;
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
        if (!u) return A.checkout(kind, parcelRef); // paiement sans compte : l'e-mail est demandé sur la page de paiement
        if (!u){ location.href = A.loginUrl('/?commune=' + encodeURIComponent(inseeOf(p) !== p.code_insee ? inseeOf(p) : p.nom_com) + '&section=' + encodeURIComponent(sec) + '&numero=' + encodeURIComponent(num)); return; }
        return credits > 0 || inclus ? A.generate(parcelRef) : A.checkout(kind, parcelRef);
      }).catch(function(e){
        err.textContent = e && e.code === 'hors_commune' ? 'Cette parcelle est hors de votre commune : elle n\'est pas couverte par l\'abonnement.' : e && e.code === 'solde' ? 'Votre solde de rapports est épuisé.' : 'L\'opération n\'a pas pu aboutir. Réessayez dans un instant.';
        if (e && e.code === 'solde') { credits = 0; label = BTN; if (offerEl) offerEl.hidden = false; }
        setAll(label, false);
      });
    }); });
    if (window.TUAuth && window.TUAuth.track) window.TUAuth.track('diagnostic', parcelRef);
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
    var AB = { '10': [39, 10], '50': [175, 50] }, mode = 'credits', bill = document.querySelector('.tu-pan .billing');
    var render = function(){
      document.querySelectorAll('.plans-pro .plan, .sur-mesure').forEach(function(c){ var m = c.getAttribute('data-m'); c.hidden = mode === 'credits' ? m !== 'credits' : m !== 'abo'; });
      document.querySelectorAll('.plans-pro .plan[data-ab]').forEach(function(c){
        var n = c.getAttribute('data-ab'), A = AB[n], amt = c.querySelector('.amt'), u = c.querySelector('.unit'), btn = c.querySelector('.go'), nom = c.querySelector('h3').textContent, ulx = c.querySelector('ul');
        if (ulx) ulx.innerHTML = LIM.map(function(t){ return '<li>' + t + '</li>'; }).join('');
        btn.textContent = 'S\'abonner · ' + nom + ' →';
        if (mode === 'an') { amt.innerHTML = eur(A[0] * 10) + ' <small>/ an</small>'; u.textContent = (A[1] * 12) + ' rapports pour l\'année · ' + eur(A[0] * 10 / (A[1] * 12)) + ' le rapport'; btn.setAttribute('data-kind', 'ab' + n + '_an'); }
        else { amt.innerHTML = eur(A[0]) + ' <small>/ mois</small>'; u.textContent = eur(A[0] / A[1]) + ' le rapport'; btn.setAttribute('data-kind', 'ab' + n); }
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
        A.checkout(kind).catch(function(e){
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
    { q: 'Combien ça coûte ?', k: ['prix', 'tarif', 'cout', 'coute', 'combien', 'euros', 'payer', 'lot'], a: 'Particuliers : 19,90 € le rapport complet, 14,90 € le rapport par lot de 2, 12,90 € par lot de 3. Professionnels : 5 € le rapport en crédits (pack de 50), 3,50 € en abonnement Pro.', l: [['Voir les tarifs', '/tarifs.html']] },
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
  var busy = false;
  fm.addEventListener('submit', function(ev){
    ev.preventDefault(); var t = inp.value.trim(); if (!t || busy) return; inp.value = ''; say('me', t);
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
