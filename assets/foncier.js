(function(){ function init(){
  var $ = function(i){ return document.getElementById(i); };
  var C = window.TU_CONFIG || {}, sel = null, last = null, map = null, layer = null, t = null;
  var COV = [];
  fetch(C.supabaseUrl + '/rest/v1/rpc/fon_couverture', { method: 'POST', headers: { apikey: C.supabaseKey, 'Content-Type': 'application/json' }, body: '{}' }).then(function(x){ return x.json(); }).then(function(l){
    if (!Array.isArray(l)) return; COV = l;
    $('fe-cov').textContent = l.length >= 100 ? 'Couverture : toute la France métropolitaine et les départements d\'outre-mer.' : 'Déjà disponible dans ' + l.length + ' départements. Couverture nationale en cours de déploiement.';
  }).catch(function(){});
  var inp = $('fe-com'), sug = $('fe-sug');
  inp.addEventListener('input', function(){
    sel = null; clearTimeout(t); var q = inp.value.trim();
    if (q.length < 2) { sug.hidden = true; return; }
    t = setTimeout(function(){
      fetch('https://geo.api.gouv.fr/communes?nom=' + encodeURIComponent(q) + '&fields=nom,code,centre,codesPostaux,codeDepartement&boost=population&limit=8').then(function(r){ return r.json(); }).then(function(l){
        sug.innerHTML = '';
        l.forEach(function(c){
          var li = document.createElement('li'); li.textContent = c.nom + ' (' + ((c.codesPostaux || [])[0] || c.code) + ')';
          li.addEventListener('mousedown', function(e){ e.preventDefault(); sel = c; inp.value = c.nom; sug.hidden = true; });
          sug.appendChild(li);
        });
        sug.hidden = !l.length;
      }).catch(function(){ sug.hidden = true; });
    }, 220);
  });
  inp.addEventListener('blur', function(){ setTimeout(function(){ sug.hidden = true; }, 150); });
  function num(i){ var v = parseInt($(i).value, 10); return isNaN(v) ? 0 : v; }
  $('fe-form').addEventListener('submit', function(e){
    e.preventDefault(); $('fe-err').textContent = '';
    if (!sel) {
      var q = inp.value.trim(); if (q.length < 2) { $('fe-err').textContent = 'Indiquez une commune.'; return; }
      fetch('https://geo.api.gouv.fr/communes?nom=' + encodeURIComponent(q) + '&fields=nom,code,centre,codesPostaux,codeDepartement&boost=population&limit=1').then(function(r){ return r.json(); }).then(function(l){
        if (!l.length) { $('fe-err').textContent = 'Commune introuvable : vérifiez l\'orthographe.'; return; }
        sel = l[0]; inp.value = sel.nom; $('fe-form').requestSubmit ? $('fe-form').requestSubmit() : $('fe-go').click();
      }).catch(function(){ $('fe-err').textContent = 'Recherche de la commune impossible pour le moment, réessayez.'; });
      return;
    }
    if (COV.length && COV.indexOf(sel.codeDepartement) < 0) { $('fe-err').textContent = 'Votre département est en cours d\'intégration : les résultats peuvent être incomplets. Laissez-nous vos coordonnées plus bas, nous vous transmettons l\'étude complète.'; }
    var b = $('fe-besoin').value, surf = num('fe-surf'), bati = b === 'batiment' ? Math.max(num('fe-bati'), 1) : num('fe-bati');
    $('fe-go').disabled = true; $('fe-go').textContent = 'Recherche en cours…';
    var lat = sel.centre.coordinates[1], lon = sel.centre.coordinates[0], r = parseInt($('fe-rayon').value, 10);
    fetch(C.supabaseUrl + '/rest/v1/rpc/fon_apercu', { method: 'POST', headers: { apikey: C.supabaseKey, 'Content-Type': 'application/json' }, body: JSON.stringify({ p_lat: lat, p_lon: lon, p_rayon_km: r, p_surf: surf, p_bati: bati }) })
      .then(function(x){ return x.json(); }).then(function(d){
        last = { commune: sel.nom, insee: sel.code, lat: lat, lon: lon, rayon_km: r, besoin: b, surface: surf || null, bati: num('fe-bati') || null, usage: $('fe-usage').value, puissance_kva: num('fe-kva') || null, apercu: d };
        var n = function(v){ return Number(v || 0).toLocaleString('fr-FR'); };
        var tot = b === 'terrain' ? d.terrains + d.friches : b === 'batiment' ? d.batiments : d.total;
        $('fe-titre').textContent = n(tot) + (tot > 1 ? ' sites correspondent' : ' site correspond') + ' à votre recherche autour de ' + sel.nom + ' (' + r + ' km)';
        var T = [[d.terrains, 'terrains constructibles sans bâtiment'], [d.zone_activite, 'en zone d\'activité du PLU'], [d.batiments, 'avec bâtiment d\'activité existant'], [d.societes, 'détenus par une société'], [d.difficulte, 'de sociétés en difficulté ou fermées'], [d.friches, 'friches recensées']];
        $('fe-tiles').innerHTML = T.map(function(x){ return '<div class="fe-tile"><b>' + n(x[0]) + '</b><span>' + x[1] + '</span></div>'; }).join('');
        $('fe-res').hidden = false;
        if (window.L) {
          if (!map) { map = L.map('fe-map', { scrollWheelZoom: false }); L.tileLayer('https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/png&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', { maxZoom: 16, attribution: 'IGN' }).addTo(map); }
          if (layer) layer.remove();
          layer = L.layerGroup().addTo(map);
          L.circle([lat, lon], { radius: r * 1000, color: '#A3462C', weight: 1.5, fill: false }).addTo(layer);
          (d.points || []).forEach(function(p){ L.circle([p[0], p[1]], { radius: 950, color: '#A3462C', weight: 0, fillOpacity: 0.3 }).addTo(layer); });
          map.fitBounds(L.latLng(lat, lon).toBounds(r * 2100));
          setTimeout(function(){ map.invalidateSize(); }, 50);
        }
        $('fe-res').scrollIntoView({ behavior: 'smooth', block: 'start' });
      }).catch(function(){ $('fe-err').textContent = 'La recherche n\'a pas abouti. Réessayez dans un instant.'; })
      .then(function(){ $('fe-go').disabled = false; $('fe-go').textContent = 'Voir les sites disponibles →'; });
  });
  $('fe-lead').addEventListener('submit', function(e){
    e.preventDefault(); var m = $('fe-lead-msg'); m.textContent = 'Envoi…';
    var row = Object.assign({}, last || {}, { societe: $('fe-soc').value.trim(), nom: $('fe-nom').value.trim(), email: $('fe-mail').value.trim(), telephone: $('fe-tel').value.trim() || null, message: $('fe-msg').value.trim() || null });
    fetch(C.supabaseUrl + '/rest/v1/fon_demandes', { method: 'POST', headers: { apikey: C.supabaseKey, 'Content-Type': 'application/json', Prefer: 'return=minimal' }, body: JSON.stringify(row) })
      .then(function(x){ if (!x.ok) throw 0; m.textContent = 'Demande enregistrée. Nous vous adressons le rapport détaillé très rapidement.'; $('fe-lead').reset(); })
      .catch(function(){ m.textContent = 'L\'envoi n\'a pas abouti. Écrivez-nous à contact@terrenurbanisme.com.'; });
  });
}
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
