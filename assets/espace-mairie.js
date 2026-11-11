/* Espace mairie : connexion, demandes des habitants, intégration du bouton */
(function () {
  var API = 'https://nmoigruxnhsidrhqtzid.supabase.co/functions/v1/stripe-webhook';
  var $ = function (id) { return document.getElementById(id); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var slug = '', key = '', ST = 'tu_mairie';
  function getS() { var v = null; try { v = JSON.parse(sessionStorage.getItem(ST) || localStorage.getItem(ST) || 'null'); } catch (e) {} return v; }
  function setS(v, rester) { try { (rester ? localStorage : sessionStorage).setItem(ST, JSON.stringify(v)); } catch (e) {} }
  function delS() { try { sessionStorage.removeItem(ST); localStorage.removeItem(ST); } catch (e) {} }
  // Ancien lien personnel (#commune.clé) : accepté une fois, puis retiré de l'adresse
  var h = location.hash.replace(/^#/, ''), i = h.indexOf('.');
  if (i > 0) { setS({ slug: h.slice(0, i), k: h.slice(i + 1) }, false); history.replaceState(null, '', location.pathname); }
  function showLogin(msg) { $('em-app').hidden = true; $('em-out').hidden = true; $('em-login').hidden = false; $('em-ville').innerHTML = ''; document.querySelector('.em-lerr').textContent = msg || ''; }
  var lf = $('em-lf');
  lf.addEventListener('submit', function (e) {
    e.preventDefault(); var er = lf.querySelector('.em-lerr'), bt = lf.querySelector('button'); er.textContent = '';
    if (!lf.identifiant.value.trim() || !lf.mdp.value) { er.textContent = 'Indiquez votre identifiant et votre mot de passe.'; return; }
    bt.disabled = true; bt.textContent = 'Connexion…';
    fetch(API + '?ville=_connexion', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ identifiant: lf.identifiant.value.trim(), mdp: lf.mdp.value }) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (x) {
        bt.disabled = false; bt.textContent = 'Se connecter';
        if (!x.ok || !x.j.ok) { er.textContent = x.j && x.j.error === 'trop_essais' ? 'Trop d\'essais. Réessayez dans une heure.' : 'Identifiant ou mot de passe incorrect.'; return; }
        setS({ slug: x.j.slug, k: x.j.k }, lf.rester.checked); lf.mdp.value = ''; start();
      }).catch(function () { bt.disabled = false; bt.textContent = 'Se connecter'; er.textContent = 'Connexion impossible pour le moment. Réessayez dans un instant.'; });
  });
  $('em-out').addEventListener('click', function () { delS(); location.reload(); });
  var V = null, ALL = [], seen = {}, first = true;
  var VW = { ok: ['ok', 'Constructible'], cond: ['cond', 'Sous conditions'], non: ['non', 'Non constructible'] };
  var PL = { maison: 'Construire une maison', extension: 'Agrandir ou surélever', piscine: 'Piscine', annexe: 'Abri, garage ou annexe', division: 'Diviser le terrain', achat: 'Acheter ou vendre' };
  function pj(r) { return r.projet ? (PL[r.projet] || r.projet) : ''; }
  function fd(s) { var d = new Date(s); return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }) + ' ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }); }
  function per(r) {
    var p = $('em-per').value, d = new Date(r.date), n = new Date();
    if (p === 'm0') return d.getFullYear() === n.getFullYear() && d.getMonth() === n.getMonth();
    if (p === 'm1') { var m = new Date(n.getFullYear(), n.getMonth() - 1, 1); return d.getFullYear() === m.getFullYear() && d.getMonth() === m.getMonth(); }
    if (p === 'd90') return n - d < 90 * 864e5;
    return true;
  }
  function rows() {
    var q = $('em-q').value.trim().toLowerCase();
    return ALL.filter(per).filter(function (r) { return !q || [r.section + ' ' + r.numero, r.zone, r.nom, r.email, r.projet].join(' ').toLowerCase().indexOf(q) >= 0; });
  }
  function render() {
    var L = rows(), tb = $('em-rows');
    $('em-empty').hidden = !!L.length;
    tb.innerHTML = L.map(function (r) {
      var v = r.statut === 'error' ? ['wait', 'Incident'] : r.statut === 'pending' ? ['wait', 'En préparation'] : (VW[r.verdict] || ['wait', '–']);
      var id = r.date + r.section + r.numero, nw = !first && !seen[id]; seen[id] = 1;
      return '<tr' + (nw ? ' class="em-new"' : '') + '><td>' + fd(r.date) + '</td><td><b>' + esc(r.section + ' ' + r.numero) + '</b>' + (r.exemple ? '<span class="em-ex">exemple</span>' : '') + '</td><td>' + esc(r.zone || '–') + '</td><td><span class="em-v ' + v[0] + '">' + v[1] + '</span></td><td>' + esc(pj(r) || '–') + '</td>' +
        (r.consent ? '<td>' + esc(r.nom || '') + '</td><td>' + esc(r.email || '') + (r.tel ? '<br><span class="em-mu">' + esc(r.tel) + '</span>' : '') + '</td>' : '<td class="em-mu">Non communiqué</td><td class="em-mu">Consentement non donné</td>') +
        '<td>' + (r.lien ? '<a href="' + esc(r.lien) + '" target="_blank" rel="noopener">Ouvrir</a>' : '<span class="em-mu">–</span>') + '</td></tr>';
    }).join('');
    first = false;
    var done = L.filter(function (r) { return r.statut !== 'error'; });
    $('k-n').textContent = done.length.toLocaleString('fr-FR');
    $('k-c').textContent = L.filter(function (r) { return r.consent; }).length.toLocaleString('fr-FR');
    var zc = {}; done.forEach(function (r) { if (r.zone) zc[r.zone] = (zc[r.zone] || 0) + 1; });
    var top = Object.keys(zc).sort(function (a, b) { return zc[b] - zc[a]; })[0];
    $('k-z').textContent = top || '–';
    var vv = done.filter(function (r) { return r.verdict; });
    $('k-o').textContent = vv.length ? Math.round(100 * vv.filter(function (r) { return r.verdict === 'ok'; }).length / vv.length) + ' %' : '–';
    $('em-ex-note').hidden = !ALL.some(function (r) { return r.exemple; });
  }
  function load() {
    return fetch(API + '?ville=' + encodeURIComponent(slug), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ action: 'espace', k: key }) })
      .then(function (r) { if (!r.ok) throw r.status; return r.json(); })
      .then(function (j) { if (!V) setup(j.ville); ALL = j.demandes || []; render(); });
  }
  function setup(v) {
    V = v; $('em-app').hidden = false;
    var lib = v.libelle.charAt(0).toUpperCase() + v.libelle.slice(1);
    var dl = null; if (v.demo) { try { dl = localStorage.getItem('tu_vlogo_' + v.slug); } catch (x) {} }
    var lsrc = v.logo || (dl && /^data:image\//.test(dl) ? dl : null);
    $('em-ville').innerHTML = lsrc ? '<img src="' + esc(lsrc) + '" alt="' + esc(lib) + '">' : esc(lib);
    if (lsrc) { var nm = $('em-site-n'); setTimeout(function () { nm.innerHTML = '<img src="' + esc(lsrc) + '" alt="" style="height:34px;background:#fff;border-radius:6px;padding:3px 6px;vertical-align:middle;margin-right:10px">Mairie de ' + esc(v.nom); }, 0); }
    var mo = new Date().toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
    $('em-per-l').textContent = 'Service urbanisme · ' + mo;
    var url = 'https://terrenurbanisme.com/ville/' + v.slug;
    $('em-url').value = url; $('em-open').href = url;
    if (v.demo) {
      $('em-demo-note').hidden = false; $('em-demo-l').hidden = false;
      fetch(API + '?ville=' + encodeURIComponent(slug), { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ action: 'demo_lien', k: key }) })
        .then(function (r) { return r.ok ? r.json() : null; }).then(function (j) { if (j && j.k) { var d = url + '?k=' + j.k; $('em-durl').value = d; $('em-dopen').href = d; } else $('em-demo-l').hidden = true; }).catch(function () {});
    }
    var btn = '<a href="' + url + '" target="_blank" rel="noopener" style="display:inline-block;background:#A3462C;color:#ffffff;font-family:Arial,Helvetica,sans-serif;font-weight:700;font-size:16px;line-height:1.2;text-decoration:none;padding:14px 22px;border-radius:10px">Analyser mon terrain</a>';
    $('em-prev').innerHTML = btn; $('em-site-btn').innerHTML = btn.replace('font-size:16px', 'font-size:14px').replace('padding:14px 22px', 'padding:10px 16px');
    $('em-snip').textContent = '<!-- Bouton TerrenUrbanisme : rapport d\'urbanisme offert par ' + v.libelle + ' -->\n' + btn;
    $('em-site-n').textContent = 'Mairie de ' + v.nom;
    $('em-site-url').textContent = 'site-de-la-mairie.fr/services-en-ligne';
    $('em-abo').innerHTML = '<dt>Commune</dt><dd>' + esc(v.nom) + '</dd><dt>Formule</dt><dd>' + esc(v.formule || 'Offre communale') + '</dd><dt>Statut</dt><dd>' + (v.demo ? 'Démonstration' : v.actif ? 'Actif' : 'Inactif') + '</dd>' + (v.fin ? '<dt>Échéance</dt><dd>' + new Date(v.fin).toLocaleDateString('fr-FR') + '</dd>' : '') + '<dt>Parcelles couvertes</dt><dd>Toute la commune (INSEE ' + esc(v.insee.join(', ')) + ')</dd>';
    document.title = 'Espace mairie · ' + v.nom + ' | TerrenUrbanisme';
  }
  document.querySelectorAll('.em-tabs button').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.em-tabs button').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
      document.querySelectorAll('[data-p]').forEach(function (p) { p.hidden = p.getAttribute('data-p') !== b.getAttribute('data-t'); });
    });
  });
  $('em-per').addEventListener('change', render); $('em-q').addEventListener('input', render);
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-copy]'); if (!b) return;
    var el = $(b.getAttribute('data-copy')), t = el.value != null && el.tagName === 'INPUT' ? el.value : el.textContent;
    var done = function () { var o = b.textContent; b.textContent = 'Copié'; setTimeout(function () { b.textContent = o; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function () { if (el.select) el.select(); });
    else if (el.select) el.select();
  });
  $('em-exp').addEventListener('click', function () {
    var L = rows(), sep = ';', q = function (s) { s = String(s == null ? '' : s); return /[";\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
    var out = ['Date;Commune;Section;Numéro;Zone;Verdict;Projet;Nom;E-mail;Téléphone;Consentement;Lien du rapport'];
    L.forEach(function (r) { out.push([new Date(r.date).toLocaleString('fr-FR'), r.commune, r.section, r.numero, r.zone, (VW[r.verdict] || ['', ''])[1], pj(r), r.nom, r.email, r.tel, r.consent ? 'Oui' : 'Non', r.lien].map(q).join(sep)); });
    var blob = new Blob(['﻿' + out.join('\r\n')], { type: 'text/csv;charset=utf-8' }), a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'demandes-' + slug + '-' + new Date().toISOString().slice(0, 10) + '.csv'; document.body.appendChild(a); a.click(); a.remove();
  });
  var timer = null;
  function start() {
    var s = getS(); if (!s || !s.slug || !s.k) { showLogin(); return; }
    slug = s.slug; key = s.k;
    load().then(function () { $('em-login').hidden = true; $('em-out').hidden = false; if (!timer) timer = setInterval(function () { if (!document.hidden) load().catch(function () {}); }, 20000); })
      .catch(function (st) { if (st === 403) { delS(); showLogin('Votre session a expiré. Reconnectez-vous.'); } else showLogin('Connexion impossible pour le moment. Réessayez dans un instant.'); });
  }
  start();
})();
