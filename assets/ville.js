/* Page d'une commune abonnée : configuration de la commune, puis chargement de la recherche */
(function () {
  var API = 'https://nmoigruxnhsidrhqtzid.supabase.co/functions/v1/stripe-webhook';
  var m = location.pathname.match(/\/ville\/([a-z0-9-]+)/), qs = new URLSearchParams(location.search);
  var slug = (m && m[1]) || qs.get('c') || '';
  var k = qs.get('k') || '';
  if (k) { try { sessionStorage.setItem('tu_vk_' + slug, k); } catch (e) {} } else { try { k = sessionStorage.getItem('tu_vk_' + slug) || ''; } catch (e) {} }
  function load(src) { return new Promise(function (ok, ko) { var s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = ko; document.body.appendChild(s); }); }
  function txt(id, v) { var e = document.getElementById(id); if (e) e.textContent = v; }
  fetch(API + '?ville=' + encodeURIComponent(slug)).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (V) {
    V.api = API; V.k = k; window.TU_VILLE = V;
    var Lib = V.libelle.charAt(0).toUpperCase() + V.libelle.slice(1);
    document.title = 'Votre terrain est-il constructible ? | Service offert par ' + V.libelle;
    txt('vl-lib', Lib); txt('vl-eb', Lib + ' · service gratuit pour les habitants');
    txt('vl-lede', 'Zone du PLU, règles de construction, risques, réseaux : ' + V.libelle + ' vous offre le rapport d’urbanisme complet de votre parcelle.');
    if (V.logo) { var lg = document.getElementById('vl-logo'); lg.src = V.logo; lg.alt = Lib; lg.hidden = false; document.getElementById('vl-lib').hidden = true; }
    if (V.demo) { document.getElementById('vl-demo').hidden = false; txt('vl-demo-n', V.libelle); }
    if (!V.actif) { var e = document.getElementById('err'); if (e) e.textContent = 'Ce service n’est pas actif pour le moment.'; }
    var hint = document.querySelector('.scope .hint span'); if (hint) hint.textContent = 'Zoomez sur votre terrain à ' + V.nom + ', puis cliquez sur la parcelle.';
    return load('/assets/leaflet.js?v=v78').then(function () { return load('/assets/turf.min.js?v=v78'); }).then(function () { return load('/assets/app.js?v=v78'); });
  }).catch(function () {
    document.querySelector('main').innerHTML = '<section class="sec"><div class="wrap"><h1>Page introuvable</h1><p class="lede">Ce service communal n’existe pas ou n’est plus disponible. Retrouvez TerrenUrbanisme sur <a href="/">terrenurbanisme.com</a>.</p></div></section>';
  });
})();
