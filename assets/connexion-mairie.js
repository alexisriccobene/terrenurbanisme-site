/* Page de connexion : identifiant de commune (sans @) dans le même formulaire que les clients */
(function () {
  var API = 'https://nmoigruxnhsidrhqtzid.supabase.co/functions/v1/stripe-webhook', ST = 'tu_mairie';
  window.TUMairieLogin = function (id, mdp) {
    return fetch(API + '?ville=_connexion', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ identifiant: id, mdp: mdp }) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); }, function () { throw 'Connexion impossible pour le moment. Réessayez dans un instant.'; })
      .then(function (x) {
        if (!x.ok || !x.j.ok) throw (x.j && x.j.error === 'trop_essais' ? 'Trop d’essais. Réessayez dans une heure.' : 'Identifiant ou mot de passe incorrect.');
        try { localStorage.setItem(ST, JSON.stringify({ slug: x.j.slug, k: x.j.k })); } catch (e2) {}
        location.href = '/mairie';
      });
  };
  if (/mairie/.test(location.hash) || new URLSearchParams(location.search).get('espace') === 'mairie') {
    var t = document.getElementById('lf-lede'); if (t) t.textContent = 'Mairies : connectez-vous avec l’identifiant et le mot de passe de votre commune.';
  }
})();
