/* Page de connexion : onglet Mairie (identifiant et mot de passe de la commune) */
(function () {
  var API = 'https://nmoigruxnhsidrhqtzid.supabase.co/functions/v1/stripe-webhook', ST = 'tu_mairie';
  var tabs = document.querySelectorAll('.auth-tabs button'), mf = document.getElementById('mairie-form'), cf = document.getElementById('login-form'), sent = document.getElementById('login-sent');
  function show(t) {
    tabs.forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-at') === t ? 'true' : 'false'); });
    mf.hidden = t !== 'mairie'; cf.hidden = t === 'mairie'; if (sent && t === 'mairie') sent.hidden = true;
  }
  tabs.forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-at')); }); });
  if (/mairie/.test(location.hash) || new URLSearchParams(location.search).get('espace') === 'mairie') show('mairie');
  mf.addEventListener('submit', function (e) {
    e.preventDefault();
    var er = mf.querySelector('.err'), bt = mf.querySelector('button[type=submit]'), id = mf.identifiant.value.trim(), mdp = mf.mdp.value;
    er.textContent = '';
    if (!id || !mdp) { er.textContent = 'Indiquez votre identifiant et votre mot de passe.'; return; }
    bt.disabled = true; bt.textContent = 'Connexion…';
    fetch(API + '?ville=_connexion', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ identifiant: id, mdp: mdp }) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (x) {
        if (!x.ok || !x.j.ok) { bt.disabled = false; bt.textContent = 'Se connecter'; er.textContent = x.j && x.j.error === 'trop_essais' ? 'Trop d’essais. Réessayez dans une heure.' : 'Identifiant ou mot de passe incorrect.'; return; }
        try { (mf.rester.checked ? localStorage : sessionStorage).setItem(ST, JSON.stringify({ slug: x.j.slug, k: x.j.k })); } catch (e2) {}
        location.href = '/mairie';
      }).catch(function () { bt.disabled = false; bt.textContent = 'Se connecter'; er.textContent = 'Connexion impossible pour le moment. Réessayez dans un instant.'; });
  });
})();
