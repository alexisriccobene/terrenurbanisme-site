/* TerrenUrbanisme — gestion du consentement aux cookies
   Aucun traceur soumis à consentement n'est chargé avant l'accord explicite de l'utilisateur.
   La mesure d'audience (Google Analytics 4) n'est activée que si un identifiant est renseigné dans config.js (ga). */
(function(){
  'use strict';
  var cfg = window.TU_CONFIG || {}, KEY = 'tu_consent', MAX_AGE = 182 * 24 * 3600 * 1000;
  var hasAnalytics = !!cfg.ga, hasAds = !!(cfg.gads || cfg.metaPixel), hasAny = hasAnalytics || hasAds;
  function read(){ try { var c = JSON.parse(localStorage.getItem(KEY) || 'null'); if (c && c.date && (Date.now() - Date.parse(c.date)) < MAX_AGE) return c; } catch (e) {} return null; }
  function write(analytics, ads){ if (ads === undefined) ads = analytics; var c = { v: 2, analytics: !!analytics, ads: !!ads, date: new Date().toISOString() }; try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {} apply(c); return c; }
  function clearGa(){
    document.cookie.split(';').forEach(function(x){ var n = x.split('=')[0].trim(); if (/^_ga|^_gid|^_gcl/.test(n)) { var d = location.hostname.split('.'); for (var i = 0; i < d.length; i++) { var dom = d.slice(i).join('.'); document.cookie = n + '=; Max-Age=0; path=/; domain=.' + dom; document.cookie = n + '=; Max-Age=0; path=/; domain=' + dom; } document.cookie = n + '=; Max-Age=0; path=/'; } });
  }
  var loaded = false, gtagReady = false, adsLoaded = false, current = null;
  var PRIV = /^\/(r\/|rapport\.html|essai\.html)/.test(location.pathname);
  function pageLoc(){ var q = new URLSearchParams(location.search); ['session_id', 'code', 'r'].forEach(function(k){ q.delete(k); }); var s = q.toString(); return location.origin + location.pathname.replace(/^\/r\/.+/, '/r/rapport') + (s ? '?' + s : ''); }
  function gtagInit(id){
    window.dataLayer = window.dataLayer || [];
    if (!window.gtag) window.gtag = function(){ window.dataLayer.push(arguments); };
    if (!gtagReady){ gtagReady = true; window.gtag('js', new Date()); var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id); document.head.appendChild(s); }
  }
  function apply(c){
    current = c;
    if (hasAnalytics){
      if (c && c.analytics && !loaded){
        loaded = true; gtagInit(cfg.ga);
        window.gtag('config', cfg.ga, { anonymize_ip: true, allow_google_signals: false, allow_ad_personalization_signals: false, page_location: pageLoc() });
      } else if (c && !c.analytics){
        if (loaded) { window['ga-disable-' + cfg.ga] = true; }
        clearGa();
      }
    }
    if (hasAds && c && c.ads && !adsLoaded){
      adsLoaded = true;
      if (cfg.gads){ gtagInit(cfg.gads); window.gtag('config', cfg.gads); }
      if (cfg.metaPixel && !PRIV){
        !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
        window.fbq('init', cfg.metaPixel); window.fbq('track', 'PageView');
      }
    }
  }
  /* Conversion (page de confirmation de paiement) : envoyée uniquement avec le consentement correspondant */
  window.TU_conversion = function(value, id){
    var c = current || read(); if (!c) return;
    if (c.analytics && loaded && window.gtag) window.gtag('event', 'purchase', { currency: 'EUR', value: value || undefined, transaction_id: id || undefined });
    if (c.ads && adsLoaded){
      if (cfg.gads && cfg.gadsLabel && window.gtag) window.gtag('event', 'conversion', { send_to: cfg.gads + '/' + cfg.gadsLabel, currency: 'EUR', value: value || undefined, transaction_id: id || undefined });
      if (cfg.metaPixel && window.fbq) window.fbq('track', 'Purchase', { currency: 'EUR', value: value || 0 });
    }
  };
  function el(html){ var d = document.createElement('div'); d.innerHTML = html.trim(); return d.firstChild; }
  var banner = null, modal = null;
  function closeBanner(){ if (banner){ banner.remove(); banner = null; } }
  function showBanner(){
    if (banner) return;
    banner = el('<div class="ck-banner" role="dialog" aria-live="polite" aria-label="Cookies"><div class="ck-in"><p><strong>Votre vie privée</strong> Avec votre accord, nous mesurons l\'audience du site pour l\'améliorer' + (hasAds ? ' et l\'efficacité de nos publicités (Google, Meta)' : ' (Google Analytics, sans publicité ciblée)') + '. Vous pouvez accepter, refuser ou choisir, et changer d\'avis à tout moment via « Gérer les cookies » en bas de page. <a href="/confidentialite.html#cookies">En savoir plus</a></p><div class="ck-btns"><button type="button" class="btn ghost" data-ck="refuse">Tout refuser</button><button type="button" class="btn ghost" data-ck="custom">Personnaliser</button><button type="button" class="btn" data-ck="accept">Tout accepter</button></div></div></div>');
    banner.addEventListener('click', function(e){ var a = e.target.getAttribute('data-ck'); if (!a) return; if (a === 'custom'){ closeBanner(); openModal(); return; } write(a === 'accept'); closeBanner(); });
    document.body.appendChild(banner);
  }
  function openModal(){
    if (modal) modal.remove();
    var c = read();
    modal = el('<div class="ck-modal" role="dialog" aria-modal="true" aria-labelledby="ck-t"><div class="ck-box">' +
      '<h2 id="ck-t">Gérer les cookies</h2>' +
      '<p>Choisissez les traceurs que vous acceptez. Votre choix est conservé six mois sur cet appareil.</p>' +
      '<div class="ck-cat"><div><strong>Nécessaires au fonctionnement</strong><span>Connexion à votre espace (session sécurisée) et mémorisation de votre choix sur les cookies. Ils ne peuvent pas être désactivés et ne requièrent pas de consentement.</span></div><span class="ck-on">Toujours actifs</span></div>' +
      '<div class="ck-cat"><div><strong>Mesure d\'audience</strong><span>' + (hasAnalytics ? 'Google Analytics 4 : pages consultées, provenance et type d\'appareil, de façon statistique, sans publicité ciblée. Cookies _ga, durée maximale de 13 mois.' : 'Aucun outil de mesure d\'audience n\'est utilisé actuellement sur ce site.') + '</span></div>' +
      (hasAnalytics ? '<label class="ck-sw"><input type="checkbox" id="ck-an"' + (c && c.analytics ? ' checked' : '') + '><i></i><span class="sr">Autoriser la mesure d\'audience</span></label>' : '<span class="ck-off">Non utilisé</span>') + '</div>' +
      (hasAds ? '<div class="ck-cat"><div><strong>Mesure publicitaire</strong><span>Google Ads et Meta (Facebook, Instagram) : mesurer les achats issus de nos publicités et les proposer aux personnes susceptibles d\'être intéressées. Cookies _gcl, _fbp, durée maximale de 13 mois.</span></div><label class="ck-sw"><input type="checkbox" id="ck-ads"' + (c && c.ads ? ' checked' : '') + '><i></i><span class="sr">Autoriser la mesure publicitaire</span></label></div>' : '') +
      '<div class="ck-btns">' + (hasAny ? '<button type="button" class="btn ghost" data-ck="refuse">Tout refuser</button><button type="button" class="btn ghost" data-ck="save">Enregistrer mes choix</button><button type="button" class="btn" data-ck="accept">Tout accepter</button>' : '<button type="button" class="btn" data-ck="close">Fermer</button>') + '</div>' +
      '<p class="ck-more"><a href="/confidentialite.html#cookies">Liste détaillée des cookies</a></p></div></div>');
    modal.addEventListener('click', function(e){
      var a = e.target.getAttribute('data-ck');
      if (e.target === modal || a === 'close'){ modal.remove(); modal = null; return; }
      if (!a) return;
      if (a === 'save'){ var an = document.getElementById('ck-an'), ad = document.getElementById('ck-ads'); write(!!(an && an.checked), !!(ad && ad.checked)); } else write(a === 'accept');
      modal.remove(); modal = null; closeBanner();
    });
    document.addEventListener('keydown', function esc(ev){ if (ev.key === 'Escape' && modal){ modal.remove(); modal = null; document.removeEventListener('keydown', esc); } });
    document.body.appendChild(modal);
    var f = modal.querySelector('button'); if (f) f.focus();
  }
  window.TUConsent = { open: openModal };
  document.addEventListener('click', function(e){ var t = e.target.closest && e.target.closest('[data-cookies]'); if (t){ e.preventDefault(); openModal(); } });
  var choice = read();
  if (choice && (choice.v === 2 || !hasAds)) apply(choice); else if (hasAny) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', showBanner); else showBanner(); }
})();
