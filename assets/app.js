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
        getJSON(CARTO+'/gpu/zone-urba?geom='+encodeURIComponent(q)).catch(function(){ return null; }),
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
        show(parcel, zones, muni, { sups: sups, mont: cd ? !!cd.mt : null });
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
  /* ---------- Offre communale : le rapport complet est offert par la commune ---------- */
  function villeOffre(resultEl, ref){
    var VL = window.TU_VILLE;
    ['.v-offer', '.buy', '.v-buy-note', '.v-owner', '.v-buy-err'].forEach(function(s){ resultEl.querySelectorAll(s).forEach(function(x){ x.remove(); }); });
    var why = resultEl.querySelector('.v-why'), box = document.createElement('div'); box.className = 'vl-box';
    if (VL.insee.indexOf(ref.insee) < 0){
      box.innerHTML = '<p class="vl-hors"><strong>Cette parcelle n\'est pas sur la commune de ' + esc(VL.nom) + '.</strong> Le service offert par ' + esc(VL.libelle) + ' couvre uniquement les parcelles de la commune. Pour une autre commune, rendez-vous sur <a href="/">terrenurbanisme.com</a>.</p>';
      why.after(box); return;
    }
    if (why) why.textContent = 'Le rapport complet répond à la question : peut-on construire, et à quelles conditions ? ' + VL.libelle.charAt(0).toUpperCase() + VL.libelle.slice(1) + ' vous l\'offre.';
    box.innerHTML = '<div class="vl-h">Recevez votre rapport complet, offert par ' + esc(VL.libelle) + '</div>' +
      '<p class="vl-s">PDF de 30 à 40 pages, envoyé par e-mail en quelques minutes.</p>' +
      '<form class="vl-f" novalidate>' +
      '<label class="field"><span>E-mail</span><input name="email" type="email" autocomplete="email" required placeholder="vous@exemple.fr"></label>' +
      '<div class="vl-2"><label class="field"><span>Nom et prénom</span><input name="nom" autocomplete="name"></label>' +
      '<label class="field"><span>Téléphone <small>(facultatif)</small></span><input name="tel" type="tel" autocomplete="tel"></label></div>' +

      '<label class="vl-ck"><input type="checkbox" name="consent"><span>J\'accepte que la mairie de ' + esc(VL.nom) + ' soit informée de ma demande et puisse me recontacter au sujet de mon projet. <small>Facultatif : le rapport vous est offert dans tous les cas.</small></span></label>' +
      '<button class="v-cta" type="submit">Recevoir mon rapport offert</button><p class="vl-err" role="alert"></p>' +
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
          if (x.ok && x.j.ok){ box.innerHTML = '<div class="vl-ok"><div class="vl-h">Votre rapport est en préparation</div><p>Il arrive par e-mail à <strong>' + esc(v.email) + '</strong> d\'ici quelques minutes. Pensez à vérifier vos courriers indésirables.</p><p class="vl-s">Rapport offert par ' + esc(VL.libelle) + '.</p></div>'; return; }
          var M = { demo: 'Démonstration : la remise du rapport sera activée à la mise en service.', hors_commune: 'Cette parcelle n\'est pas sur la commune.', limite_email: 'Vous avez déjà demandé 3 rapports aujourd\'hui. Réessayez demain.', limite: 'Trop de demandes depuis cette connexion aujourd\'hui. Réessayez demain.', limite_ville: 'Le service a atteint sa limite du jour. Réessayez demain.', inactive: 'Le service n\'est pas actif pour cette commune.', email: 'Indiquez une adresse e-mail valide.' };
          er.textContent = M[x.j.error] || 'La demande n\'a pas pu aboutir. Réessayez dans un instant.';
          bt.disabled = false; bt.textContent = 'Recevoir mon rapport offert';
        }).catch(function(){ er.textContent = 'La demande n\'a pas pu aboutir. Réessayez dans un instant.'; bt.disabled = false; bt.textContent = 'Recevoir mon rapport offert'; });
    });
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
      ['ok', 'Document d\'urbanisme', muni.is_rnu ? 'Règlement national d\'urbanisme' : noZone ? 'Document local non publié en ligne' : 'Document local publié'],
      ['ok', zl.length > 1 ? 'Zones du PLU' : 'Zone du PLU', zl.length ? zl.join(' · ') : muni.is_rnu ? 'Pas de zonage : règlement national' : 'Zonage non publié en ligne par la commune : à vérifier en mairie'],
      ['ok', 'Loi Littoral', muni.is_coastline ? 'Commune littorale : la loi s\'applique' : 'Commune non littorale']
    ];
    if (extra.mont != null) found.push(['ok', 'Loi Montagne', extra.mont ? 'Commune en zone de montagne : la loi s\'applique' : 'Commune hors zone de montagne']);
    if (sups) {
      found.push(['ok', 'Monuments historiques (ABF)', sups.some(function(x){ return x === 'ac1'; }) ? 'Dans les abords d\'un monument : avis de l\'architecte des Bâtiments de France' : 'Hors abords de monument historique recensés']);
      found.push(['ok', 'Plan de prévention des risques', sups.some(function(x){ return /^pm[1-3]/.test(x); }) ? 'Parcelle concernée par un PPR : règles détaillées dans le rapport' : 'Aucun PPR recensé sur la parcelle']);
    }
    var locked = ['Verdict : constructible ou non, et pourquoi', 'Plan de zonage et chapitre officiel du règlement en annexe', 'Règlement de la zone : hauteur, reculs, aspect, avec extraits', 'Surface constructible estimée en m² et plan d\'implantation', (/^2[AB]/.test(String(parcel && parcel.properties && parcel.properties.code_insee || '')) ? 'PADDUC, distance au rivage, loi Montagne' : 'Loi Littoral, distance au rivage, loi Montagne'), 'Risques à la parcelle, arrêtés de catastrophe naturelle', 'Accès, pente, assainissement et fibre', 'Photos aériennes depuis 1950 et permis accordés autour', 'Prix au m² de la commune et ventes de terrains alentour', 'État des risques (ERP) pré-rempli et rapport officiel Géorisques', 'Démarches, délais et interlocuteurs'];
    var OFF = { unit: { n: 1, u: '19,90 €', t: '19,90 €' }, pack2: { n: 2, u: '14,90 €', t: '29,80 €' }, pack3: { n: 3, u: '12,90 €', t: '38,70 €' } }, kind = 'pack3';
    var btnTxt = function(){ var o = OFF[kind]; return o.n > 1 ? 'Obtenir ' + o.n + ' rapports · ' + o.t : 'Obtenir le rapport complet · ' + o.t; };
    var BTN = btnTxt();
    var opt = function(k, lbl, off){ var o = OFF[k]; return '<label class="v-opt"><input type="radio" name="v-kind" value="' + k + '"' + (k === kind ? ' checked' : '') + '><span class="v-opt-l">' + lbl + '</span>' + (off ? '<em>' + off + '</em>' : '') + '<b>' + o.u + (o.n > 1 ? '<small>/ rapport</small>' : '') + '</b></label>'; };
    var OFFER = '<div class="v-offer" role="radiogroup" aria-label="Nombre de rapports"><div class="v-offer-top"><b class="v-offer-u">' + OFF[kind].u + '</b> <span>/ rapport</span><div class="v-offer-t">Prix total ' + OFF[kind].t + '</div></div>' +
      opt('unit', 'Cette parcelle') + '<div class="v-opt-sep">Plusieurs biens ? Payez moins par rapport</div>' + opt('pack2', '2 rapports', '−25 %') + opt('pack3', '3 rapports', '−35 %') +
      '<p class="v-opt-note">Le premier rapport porte sur cette parcelle. Les autres restent sur votre compte, à utiliser quand vous voulez, sans limite de durée.</p></div>';
    resultEl.innerHTML =
      '<div class="v-ref">' + esc(ref) + '</div>' +
      '<span class="v-badge v-found"><i></i>Parcelle trouvée</span>' +
      '<div class="v-title">Votre diagnostic gratuit</div>' +
      '<p class="v-other">Ce n\'est pas la bonne parcelle ? Cliquez sur une autre parcelle de la carte.</p>' +
      '<p class="v-why">Nous avons trouvé cette parcelle et les sources officielles qui la concernent. Le rapport complet répond à la question : peut-on construire, et à quelles conditions ?</p>' +
      '<div class="v-proj"><b>Quel est votre projet ?</b><span>Le rapport sera présenté pour lui.</span><div class="v-chips" role="group" aria-label="Votre projet">' + PROJ.map(function(x){ return '<button type="button" data-p="' + x[0] + '" aria-pressed="' + (x[0] === projet() ? 'true' : 'false') + '">' + x[1] + '</button>'; }).join('') + '</div></div>' +
      (noZone ? '<p class="v-disc" style="border-left:3px solid #A86A0C;padding-left:10px"><strong>Pourquoi la zone n\'apparaît pas :</strong> cette commune dispose d\'un document d\'urbanisme mais ne l\'a pas encore mis en ligne sur le Géoportail de l\'Urbanisme, la plateforme officielle de l\'État. Aucun service ne peut donc lire sa zone automatiquement : elle est à demander en mairie. Le rapport réunit toutes les autres données officielles de la parcelle : risques, servitudes, protections, lois Littoral et Montagne, accès, réseaux, prix du marché et démarches.</p>' : '') +
      OFFER + '<button type="button" class="v-cta v-cta-top buy">' + BTN + '</button><p class="v-buy-err" role="alert"></p>' +
      '<ul class="v-found-list">' + found.map(function(f){ return '<li>' + OKI + '<div><strong>' + esc(f[1]) + '</strong><span>' + esc(f[2]) + '</span></div></li>'; }).join('') + '</ul>' +
      '<ul class="v-locked">' + locked.map(function(t){ return '<li>' + LOCK + '<span>' + esc(t) + '</span><i class="blur" aria-hidden="true">████████</i></li>'; }).join('') + '</ul>' +
      '<button type="button" class="v-cta buy">' + BTN + '</button>' +
      '<p class="v-buy-note">Rapport PDF de 30 à 40 pages avec sommaire cliquable, envoyé par e-mail en quelques minutes · paiement sécurisé par Stripe<br><a href="/tarifs.html">Professionnels : abonnements dès 0,77 € le rapport</a> · <a href="/exemple.html">Voir un exemple</a></p><p class="v-buy-err" role="alert"></p>' +
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
    if (window.TU_VILLE){ villeOffre(resultEl, parcelRef); return; }
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
      if (credits > 0){ label = 'Générer le rapport complet · 1 rapport (solde : ' + credits + ')'; setAll(label); if (offerEl) offerEl.hidden = true; }
    });
    buys.forEach(function(btn, k){ btn.addEventListener('click', function(){
      var err = errs[k] || errs[0];
      if (A && A.track) A.track('clic_rapport', parcelRef);
      errs.forEach(function(e){ e.textContent = ''; });
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

/* ---------- Page Tarifs : formules et paiement ---------- */
(function(){
  var root = document.getElementById('plans'); if (!root) return;
  var billing = 'm';
  try { if (localStorage.getItem('tu_bill') === 'a') billing = 'a'; } catch (e) {}
  // Prix TTC : mensuel, et annuel ramené au mois (payé en une fois)
  var SUB = {
    essentiel: { name: 'Solo',      m: 29,  a: 290 / 12,  n: 15 },
    pro:       { name: 'Agence',    m: 55,  a: 550 / 12,  n: 50 },
    cabinet:   { name: 'Réseau',    m: 139, a: 1390 / 12, n: 150 }
  };
  var UNIT = { unit: ['19,90 €', 'Paiement unique', 'Choisir · 1 rapport'], pack2: ['14,90 € <small>/ rapport</small>', 'Lot de 2 · 29,80 € au total · −25 %', 'Choisir · 2 rapports'], pack3: ['12,90 € <small>/ rapport</small>', 'Lot de 3 · 38,70 € au total · −35 %', 'Choisir · 3 rapports'] };
  var eur = function(v){ return (Math.round(v * 100) / 100).toLocaleString('fr-FR', { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + ' €'; };
  var cards = [];
  root.querySelectorAll('.plan').forEach(function(card){
    var group = card.getAttribute('data-group'), amt = card.querySelector('.amt'), unit = card.querySelector('.unit'), save = card.querySelector('.save'), btn = card.querySelector('.go'), err = card.querySelector('.plan-err');
    var segs = card.querySelectorAll('.seg button');
    var cur = group === 'unit' ? 'pack3' : group === 'cab' ? 'cabinet' : 'pro';
    function render(){
      segs.forEach(function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-k') === cur ? 'true' : 'false'); });
      if (group === 'unit') { var o = UNIT[cur]; amt.innerHTML = o[0]; unit.textContent = o[1]; btn.textContent = o[2] + ' →'; btn.setAttribute('data-kind', cur); return; }
      var P = SUB[cur], an = billing === 'a';
      amt.innerHTML = an ? '<s>' + eur(P.m) + '</s>' + eur(P.a) + ' <small>/ mois</small>' : eur(P.m) + ' <small>/ mois</small>';
      if (save) save.innerHTML = an ? 'Facturé ' + eur(P.a * 12) + ' par an · <b>économisez ' + eur((P.m - P.a) * 12) + '</b>' : '';
      unit.textContent = an ? (P.n * 12).toLocaleString('fr-FR') + ' rapports par an · ' + eur(P.a / P.n) + ' le rapport' : P.n + ' rapports par mois · ' + eur(P.m / P.n) + ' le rapport';
      var li = card.querySelector('.li-renew'); if (li) li.textContent = an ? 'Tous les rapports de l\'année disponibles dès le paiement' : 'Rapports renouvelés chaque mois';
      var lg = card.querySelector('.li-logo'); if (lg) lg.hidden = cur === 'essentiel';
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
