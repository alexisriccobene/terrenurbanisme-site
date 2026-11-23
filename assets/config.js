/* Configuration TerrenUrbanisme : projet Supabase (clé publique, sans risque côté navigateur). */
window.TU_CONFIG = {
  supabaseUrl: 'https://nmoigruxnhsidrhqtzid.supabase.co',
  supabaseKey: 'sb_publishable_pYravUAh97-CHrAUoyS4LQ_N_hw4Pb-',
  turnstile: '0x4AAAAAAFwdIo3aMESiuQOf', /* clé de site Cloudflare Turnstile (publique) : anti-robots sur la connexion par e-mail */
  googleClientId: '545201290951-for61dl1ju9ggbh2a77seqe8hg1oh5mj.apps.googleusercontent.com', /* identifiant public (pas un secret) */
  google: false, /* activé tout seul dès que Google est allumé dans Supabase (voir plus bas) */
  ga: 'G-V1NDWY8ZXH',      /* identifiant Google Analytics 4 (G-XXXXXXX) : vide = aucune mesure d'audience */
  gads: 'AW-18591633187',      /* identifiant Google Ads (AW-XXXXXXXXX) : vide = aucune mesure publicitaire Google */
  gadsLabel: 'JRGCCK7Y9r0dEKOel6FF', /* libellé de la conversion « Achat » dans Google Ads (ex. AbCdEfGhIj) */
  metaPixel: '1425245439737900'/* identifiant du pixel Meta (Facebook, Instagram), 15 à 16 chiffres : vide = aucun pixel */
};

/* Connexion Google : le bouton n'apparaît que si le fournisseur Google est activé dans Supabase. */
(function (c) {
  try {
    fetch(c.supabaseUrl + '/auth/v1/settings', { headers: { apikey: c.supabaseKey } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j && j.external && j.external.google) { c.google = true; document.dispatchEvent(new Event('tu-google')); } })
      .catch(function () {});
  } catch (e) {}
})(window.TU_CONFIG);

/* Bouton Google officiel affiché sur notre propre domaine (Google affiche « terrenurbanisme.com »).
   TUGoogleBtn(conteneur, clientSupabase, fonctionApresConnexion) */
(function (c) {
  var gsi = null;
  function load() {
    if (gsi) return gsi;
    gsi = new Promise(function (ok, ko) {
      if (window.google && google.accounts && google.accounts.id) return ok();
      var s = document.createElement('script'); s.src = 'https://accounts.google.com/gsi/client'; s.async = true;
      s.onload = function () { ok(); }; s.onerror = ko; document.head.appendChild(s);
    });
    return gsi;
  }
  function hex(buf) { return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ('0' + b.toString(16)).slice(-2); }).join(''); }
  window.TUGoogleBtn = function (el, sb, done, fail) {
    if (!el || !c.googleClientId) return;
    var raw = hex(crypto.getRandomValues(new Uint8Array(24)).buffer);
    Promise.all([load(), crypto.subtle.digest('SHA-256', new TextEncoder().encode(raw))]).then(function (r) {
      google.accounts.id.initialize({
        client_id: c.googleClientId, nonce: hex(r[1]), ux_mode: 'popup', context: 'signin', itp_support: true,
        callback: function (resp) {
          sb.auth.signInWithIdToken({ provider: 'google', token: resp.credential, nonce: raw }).then(function (x) {
            if (x.error) { if (fail) fail(x.error); return; }
            if (done) done(x.data);
          });
        }
      });
      var w = Math.min(400, Math.max(220, Math.round(el.getBoundingClientRect().width || 320)));
      el.innerHTML = '';
      google.accounts.id.renderButton(el, { type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', shape: 'pill', logo_alignment: 'center', width: w, locale: 'fr' });
    }).catch(function () { if (fail) fail(new Error('gsi')); });
  };
})(window.TU_CONFIG);
