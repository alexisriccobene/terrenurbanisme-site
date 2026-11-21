/* Configuration TerrenUrbanisme : projet Supabase (clé publique, sans risque côté navigateur). */
window.TU_CONFIG = {
  supabaseUrl: 'https://nmoigruxnhsidrhqtzid.supabase.co',
  supabaseKey: 'sb_publishable_pYravUAh97-CHrAUoyS4LQ_N_hw4Pb-',
  turnstile: '0x4AAAAAAFwdIo3aMESiuQOf', /* clé de site Cloudflare Turnstile (publique) : anti-robots sur la connexion par e-mail */
  google: false, /* activé tout seul dès que Google est allumé dans Supabase (voir plus bas) */
  ga: 'G-V1NDWY8ZXH',      /* identifiant Google Analytics 4 (G-XXXXXXX) : vide = aucune mesure d'audience */
  gads: '',      /* identifiant Google Ads (AW-XXXXXXXXX) : vide = aucune mesure publicitaire Google */
  gadsLabel: '', /* libellé de la conversion « Achat » dans Google Ads (ex. AbCdEfGhIj) */
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
