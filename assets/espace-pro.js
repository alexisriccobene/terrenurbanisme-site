/* Tableau de bord des professionnels : volumes, communes et zones les plus demandées, détail des rapports */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var MOIS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];
  var VER = { ok: ['ok', 'Constructible'], cond: ['cond', 'Sous conditions'], non: ['non', 'Non constructible'] };
  var ALL = [];
  // Démonstration sans connexion : uniquement sur les versions de test (jamais sur terrenurbanisme.com)
  var DEMO = /(^|[?&])demo=1/.test(location.search) && !/terrenurbanisme\.com$/.test(location.hostname);
  function demoRows() {
    var j = function (d, h) { return new Date(Date.now() - d * 86400000 - (h || 0) * 3600000).toISOString(); };
    return [
      { id: 'demo-0001-aaaa', created_at: j(0, 2), commune: 'Sotta', section: 'B', numero: '842', zone: 'UC', verdict: 'ok', status: 'ready', download_slug: 'demo', agent: 'Cédric MULLER', perso: { status: 'pret', client: { prenom: 'Maxime', nom: 'DUPONT', email: 'maxime.dupont@gmail.com' } }, envois: [{ date: j(0, 1), email: 'maxime.dupont@gmail.com' }], vu_le: j(0, 0.3), vu_dernier: j(0, 0.3), vu_nb: 1 },
      { id: 'demo-0002-bbbb', created_at: j(1, 5), commune: 'Porto-Vecchio', section: 'D', numero: '1204', zone: 'UB', verdict: 'cond', status: 'ready', download_slug: 'demo', agent: 'Julie ROSSI', perso: { status: 'pret', client: { prenom: 'Sophie', nom: 'MARTIN', email: 'sophie.martin@orange.fr' } }, envois: [{ date: j(1, 3), email: 'sophie.martin@orange.fr' }], vu_le: j(1, 1), vu_dernier: j(0, 5), vu_nb: 3 },
      { id: 'demo-0003-cccc', created_at: j(2, 4), commune: 'Bonifacio', section: 'A', numero: '317', zone: 'AU', verdict: 'cond', status: 'ready', download_slug: 'demo', agent: 'Cédric MULLER', perso: { status: 'pret', client: { prenom: 'Paul', nom: 'GIRAUD', email: 'p.giraud@gmail.com' } }, envois: [{ date: j(2, 2), email: 'p.giraud@gmail.com' }], vu_nb: 0 },
      { id: 'demo-0004-dddd', created_at: j(3, 6), commune: 'Figari', section: 'C', numero: '95', zone: 'N', verdict: 'non', status: 'ready', download_slug: 'demo', agent: 'Julie ROSSI', perso: { status: 'pret', client: { prenom: 'Laura', nom: 'BIANCHI' } }, envois: [], vu_nb: 0 },
      { id: 'demo-0005-eeee', created_at: j(5, 1), commune: 'Lecci', section: 'B', numero: '460', zone: 'UC', verdict: 'ok', status: 'ready', download_slug: 'demo', agent: 'Cédric MULLER', perso: null, envois: [], vu_nb: 0 }
    ];
  }
  function nb(n) { return Number(n || 0).toLocaleString('fr-FR'); }
  function top(list, key) {
    var m = {}; list.forEach(function (d) { var k = key(d); if (k) m[k] = (m[k] || 0) + 1; });
    return Object.keys(m).map(function (k) { return [k, m[k]]; }).sort(function (a, b) { return b[1] - a[1]; });
  }
  function zoneOf(d) { return String(d.zone || '').trim() || null; }
  function periode(list) {
    var v = $('bo-per').value, now = new Date(), y = now.getFullYear(), mo = now.getMonth();
    var from = null, to = null;
    if (v === 'm0') from = new Date(y, mo, 1);
    else if (v === 'm1') { from = new Date(y, mo - 1, 1); to = new Date(y, mo, 1); }
    else if (v === 'd90') from = new Date(Date.now() - 90 * 864e5);
    else if (v === 'y') from = new Date(y, mo - 11, 1);
    var q = $('bo-q').value.trim().toLowerCase();
    return list.filter(function (d) {
      var t = new Date(d.created_at);
      if (from && t < from) return false; if (to && t >= to) return false;
      if (q && (d.commune + ' ' + d.section + ' ' + d.numero + ' ' + (d.zone || '') + ' ' + (d.order_ref || '') + ' ' + (d.agent || '')).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
  }
  // Tableau détaillé : filtres (agent, commune, suivi client) et tri
  function remplirFiltres() {
    var fa = $('bo-fa'), fc = $('bo-fc'); if (!fa || !fc) return;
    var opt = function (sel, vals, lab) { var cur = sel.value; sel.innerHTML = '<option value="">' + lab + '</option>' + vals.map(function (v) { return '<option>' + esc(v) + '</option>'; }).join(''); if (vals.indexOf(cur) >= 0) sel.value = cur; };
    var uniq = function (f) { var o = {}; ALL.forEach(function (d) { var v = f(d); if (v) o[v] = 1; }); return Object.keys(o).sort(function (a, b) { return a.localeCompare(b, 'fr'); }); };
    opt(fa, uniq(function (d) { return d.agent; }), 'Tous les agents');
    opt(fc, uniq(function (d) { return d.commune; }), 'Toutes les communes');
  }
  function tableau(L) {
    var fa = $('bo-fa'), fc = $('bo-fc'), fs = $('bo-fs'), tri = $('bo-tri');
    var cli = function (d) { var c = (d.perso && d.perso.client) || {}; return [c.nom, c.prenom].filter(Boolean).join(' '); };
    var R = L.filter(function (d) {
      if (fa && fa.value && d.agent !== fa.value) return false;
      if (fc && fc.value && d.commune !== fc.value) return false;
      var env = (d.envois || []).length > 0, pret = d.perso && d.perso.status === 'pret';
      if (fs && fs.value === 'ouvert' && !(d.vu_nb > 0)) return false;
      if (fs && fs.value === 'nonouvert' && !(env && !(d.vu_nb > 0))) return false;
      if (fs && fs.value === 'envoye' && !env) return false;
      if (fs && fs.value === 'pret' && !(pret && !env)) return false;
      return true;
    });
    var t = tri ? tri.value : 'recent', cmp = function (a, b) { return String(a || '').localeCompare(String(b || ''), 'fr'); };
    R = R.slice().sort(function (a, b) {
      if (t === 'ancien') return a.created_at < b.created_at ? -1 : 1;
      if (t === 'commune') return cmp(a.commune, b.commune) || (a.created_at < b.created_at ? 1 : -1);
      if (t === 'agent') return cmp(a.agent, b.agent) || (a.created_at < b.created_at ? 1 : -1);
      if (t === 'client') return (cli(a) ? 0 : 1) - (cli(b) ? 0 : 1) || cmp(cli(a), cli(b));
      if (t === 'ouvert') return (b.vu_nb || 0) - (a.vu_nb || 0) || String(b.vu_dernier || '').localeCompare(String(a.vu_dernier || ''));
      return a.created_at < b.created_at ? 1 : -1;
    });
    var cnt = $('bo-fn'); if (cnt) cnt.textContent = R.length + ' rapport' + (R.length > 1 ? 's' : '');
    return R;
  }
  function render() {
    remplirFiltres();
    var L = periode(ALL), now = new Date();
    $('k-n').textContent = nb(L.length);
    $('k-n2').textContent = $('bo-per').selectedOptions[0].textContent.toLowerCase();
    var m0 = ALL.filter(function (d) { var t = new Date(d.created_at); return t.getFullYear() === now.getFullYear() && t.getMonth() === now.getMonth(); }).length;
    var m1 = ALL.filter(function (d) { var t = new Date(d.created_at), p = new Date(now.getFullYear(), now.getMonth() - 1, 1); return t.getFullYear() === p.getFullYear() && t.getMonth() === p.getMonth(); }).length;
    $('k-m').textContent = nb(m0);
    $('k-m2').textContent = nb(m1) + ' le mois précédent';
    var tz = top(L, zoneOf), tc = top(L, function (d) { return d.commune; });
    $('k-z').textContent = tz.length ? tz[0][0] : '–'; $('k-z2').textContent = tz.length ? tz[0][1] + ' rapport' + (tz[0][1] > 1 ? 's' : '') : '';
    $('k-c').textContent = tc.length ? tc[0][0] : '–'; $('k-c2').textContent = tc.length ? tc[0][1] + ' rapport' + (tc[0][1] > 1 ? 's' : '') : '';
    // Rapports par mois (12 derniers mois)
    var bars = [], max = 1;
    for (var i = 11; i >= 0; i--) {
      var dm = new Date(now.getFullYear(), now.getMonth() - i, 1);
      var n = ALL.filter(function (d) { var t = new Date(d.created_at); return t.getFullYear() === dm.getFullYear() && t.getMonth() === dm.getMonth(); }).length;
      bars.push([dm, n]); if (n > max) max = n;
    }
    $('bo-bars').innerHTML = bars.map(function (b, k) { return '<div' + (k === 11 ? ' class="cur"' : '') + ' title="' + nb(b[1]) + ' rapports"><b>' + (b[1] || '') + '</b><i style="height:' + Math.max(2, Math.round(b[1] / max * 100)) + '%"></i><span>' + MOIS[b[0].getMonth()] + '</span></div>'; }).join('');
    // Constructibilité
    var tot = L.length || 1;
    $('bo-ver').innerHTML = ['ok', 'cond', 'non'].map(function (k) { var n = L.filter(function (d) { return d.verdict === k; }).length; return '<div class="bo-row"><span>' + VER[k][1] + '</span><b>' + nb(n) + '</b><div class="bar ' + k + '"><i style="width:' + Math.round(n / tot * 100) + '%"></i></div></div>'; }).join('');
    $('bo-com').innerHTML = tc.length ? tc.slice(0, 6).map(function (c) { return '<div class="bo-row"><span>' + esc(c[0]) + '</span><b>' + nb(c[1]) + '</b><div class="bar"><i style="width:' + Math.round(c[1] / tc[0][1] * 100) + '%"></i></div></div>'; }).join('') : '<p class="em-mu" style="color:var(--muet)">–</p>';
    var ta = top(L, function (d) { return d.agent; });
    $('bo-ag-card').hidden = !ta.length;
    $('bo-ag').innerHTML = ta.slice(0, 8).map(function (c, i) { return '<div class="bo-row"><span>' + (i === 0 ? '<b>' + esc(c[0]) + '</b> · le plus actif' : esc(c[0])) + '</span><b>' + nb(c[1]) + '</b><div class="bar"><i style="width:' + Math.round(c[1] / ta[0][1] * 100) + '%"></i></div></div>'; }).join('');
    // Détail
    var LIM = window.__boLim || 50;
    $('bo-rows').innerHTML = tableau(L).slice(0, LIM).map(function (d) {
      var v = VER[d.verdict], dt = new Date(d.created_at);
      var P = d.perso || {}, cl = P.client || {}, nomC = [cl.prenom, cl.nom].filter(Boolean).join(' ');
      var pret = P.status === 'pret', court = '/r/c-' + String(d.id || '').replace(/-/g, '').slice(0, 12);
      var env = (d.envois || []).slice(-1)[0];
      var act = d.ex ? '<span style="color:var(--muet)">Exemple</span>' : d.status === 'ready' && d.download_slug
        ? '<div class="bo-act"><a href="/r/' + encodeURIComponent(d.download_slug) + '" target="_blank" rel="noopener">Rapport</a>'
          + (pret ? '<a class="pr" href="' + court + '?a=1" target="_blank" rel="noopener">Version client</a><a href="/personnaliser.html?id=' + encodeURIComponent(d.id) + '">Modifier · renvoyer</a>'
                  : '<a class="pr" href="/personnaliser.html?id=' + encodeURIComponent(d.id) + '">Préparer pour le client</a>') + '</div>'
        : '<span style="color:var(--muet)">' + (d.status === 'ready' ? 'Disponible' : 'En préparation') + '</span>';
      var client = d.ex ? '–' : (nomC ? '<b>' + esc(nomC) + '</b>' : '<span style="color:var(--muet)">–</span>') + (cl.email ? '<br><small style="color:var(--muet)">' + esc(cl.email) + '</small>' : '');
      var envoi = env ? '<span class="bo-v ok">Envoyé</span><br><small style="color:var(--muet)">' + new Date(env.date).toLocaleDateString('fr-FR') + ' à ' + new Date(env.date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) + (env.email ? '<br>' + esc(env.email) : '') + '</small>' : (pret ? '<span class="bo-v cond">Prête, non envoyée</span>' : '<span style="color:var(--muet)">–</span>');
      if (d.vu_nb > 0) envoi += '<br><span class="bo-v ok" style="background:#E3EEF9;color:#1F4E79">Ouvert par le client</span><br><small style="color:var(--muet)">' + (d.vu_nb > 1 ? d.vu_nb + ' fois · dernière le ' + new Date(d.vu_dernier).toLocaleDateString('fr-FR') : 'le ' + new Date(d.vu_le).toLocaleDateString('fr-FR') + ' à ' + new Date(d.vu_le).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })) + '</small>';
      else if (env) envoi += '<br><small style="color:var(--muet)">Pas encore ouvert</small>';
      return '<tr><td>' + dt.toLocaleDateString('fr-FR') + '<br><small style="color:var(--muet)">' + dt.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) + '</small></td><td><b>' + esc(d.commune) + '</b><br><small style="color:var(--muet)">' + esc(d.section) + ' ' + esc(d.numero) + (d.zone ? ' · zone ' + esc(d.zone) : '') + '</small></td><td>' + esc(d.agent || '–') + '</td><td>' + (v ? '<span class="bo-v ' + v[0] + '">' + v[1] + '</span>' : '–') + '</td><td>' + client + '</td><td>' + envoi + '</td><td>' + act + '</td></tr>';
    }).join('');
    $('bo-empty').hidden = tableau(L).length > 0;
    var TN = tableau(L).length, more = $('bo-more'); more.hidden = TN <= LIM; more.textContent = 'Afficher plus (' + nb(TN - LIM) + ' rapports restants)';
  }

  // Compte de démonstration : historique d'illustration réaliste (12 mois), ajouté aux vrais rapports
  function exemples(noms) {
    var seed = 7; function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
    var C = [['Porto-Vecchio', 26], ['Bonifacio', 9], ['Sotta', 7], ['Lecci', 6], ['Figari', 6], ['Zonza', 5], ['Sainte-Lucie-de-Porto-Vecchio', 4], ['Propriano', 4], ['Sartène', 3], ['Ajaccio', 6], ['Grosseto-Prugna', 3], ['Pianottoli-Caldarello', 2]];
    var Z = [['UC', 'ok', 30], ['UD', 'ok', 22], ['UB', 'ok', 10], ['1AU', 'cond', 12], ['AU2a', 'cond', 6], ['A', 'non', 9], ['N', 'non', 8], ['Nr', 'non', 3]];
    var W = [30, 24, 20, 15, 12, 9, 7, 5], A = (noms && noms.length ? noms : ['Agence']).map(function (n, i) { return [n, W[i % W.length]]; });
    var P = [['maison', 45], ['division', 15], ['extension', 14], ['piscine', 8], ['achat', 18]];
    var pick = function (L) { var t = 0, i; for (i = 0; i < L.length; i++) t += L[i][L[i].length - 1]; var r = rnd() * t; for (i = 0; i < L.length; i++) { r -= L[i][L[i].length - 1]; if (r <= 0) return L[i]; } return L[0]; };
    var out = [], now = new Date();
    for (var m = 11; m >= 0; m--) {
      var base = new Date(now.getFullYear(), now.getMonth() - m, 1), saison = [0.7, 0.75, 0.9, 1.05, 1.2, 1.3, 1.15, 0.95, 1.1, 1.05, 0.9, 0.8][base.getMonth()];
      var n = Math.round((14 + (11 - m) * 2.4) * saison + rnd() * 5), jours = m === 0 ? Math.max(1, now.getDate() - 1) : new Date(base.getFullYear(), base.getMonth() + 1, 0).getDate();
      if (m === 0) n = Math.round(n * jours / 30);
      for (var k = 0; k < n; k++) {
        var c = pick(C), z = pick(Z), pr = pick(P), sec = 'ABCDEFGHK'.charAt(Math.floor(rnd() * 9)) + (rnd() < 0.3 ? 'B' : '');
        var t = new Date(base.getFullYear(), base.getMonth(), 1 + Math.floor(rnd() * jours), 8 + Math.floor(rnd() * 11), Math.floor(rnd() * 60));
        out.push({ created_at: t.toISOString(), commune: c[0], section: sec, numero: String(10 + Math.floor(rnd() * 2400)), zone: z[0], verdict: z[1], projet: pr[0], agent: pick(A)[0], status: 'ready', order_ref: 'TU-' + t.toISOString().slice(0, 10).replace(/-/g, '') + '-' + Math.floor(rnd() * 16777215).toString(16).toUpperCase().padStart(6, '0'), ex: true });
      }
    }
    return out;
  }
  function exporter() {
    var L = periode(ALL), sep = ';';
    var rows = [['Date', 'Agent', 'Client', 'E-mail client', 'Envoyé le', 'Ouvert le', 'Ouvertures', 'Commune', 'Section', 'Numéro', 'Zone', 'Verdict', 'Projet', 'Référence', 'Lien']].concat(L.map(function (d) {
      var cl = (d.perso && d.perso.client) || {}, ev = (d.envois || []).slice(-1)[0];
      return [new Date(d.created_at).toLocaleString('fr-FR'), d.agent || '', [cl.prenom, cl.nom].filter(Boolean).join(' '), cl.email || '', ev ? new Date(ev.date).toLocaleString('fr-FR') : '', d.vu_le ? new Date(d.vu_le).toLocaleString('fr-FR') : '', d.vu_nb || 0, d.commune, d.section, d.numero, d.zone || '', (VER[d.verdict] || ['', ''])[1], d.projet || '', d.order_ref || '', d.download_slug ? location.origin + '/r/' + d.download_slug : ''];
    }));
    var csv = '﻿' + rows.map(function (r) { return r.map(function (c) { return '"' + String(c == null ? '' : c).replace(/"/g, '""') + '"'; }).join(sep); }).join('\r\n');
    var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' })); a.download = 'rapports-terrenurbanisme.csv'; document.body.appendChild(a); a.click(); a.remove();
  }
  function start() {
    if (DEMO) {
      ALL = demoRows();
      var r0 = render; render = function () { r0(); document.querySelectorAll('#bo-rows a').forEach(function (a) { var h = a.getAttribute('href') || ''; if (/personnaliser\.html/.test(h)) a.href = h + '&demo=1'; else { a.href = '/personnaliser.html?id=demo&demo=1'; a.removeAttribute('target'); } }); };
      $('bo-per').addEventListener('change', function () { window.__boLim = 50; render(); });
      $('bo-q').addEventListener('input', render);
    ['bo-fa', 'bo-fc', 'bo-fs', 'bo-tri'].forEach(function (k) { var el = $(k); if (el) el.addEventListener('change', function () { window.__boLim = 50; render(); }); });
      $('bo-exp').addEventListener('click', exporter);
      $('bo-more').addEventListener('click', function () { window.__boLim = (window.__boLim || 50) + 100; render(); });
      render(); return;
    }
    var Auth = window.TUAuth; if (!Auth || !Auth.client) { setTimeout(start, 150); return; }
    Auth.user().then(function (u) {
      if (!u) { location.replace(Auth.loginUrl ? Auth.loginUrl('/espace-pro.html') : '/connexion.html'); return; }
      Auth.client.from('dossiers').select('id,created_at,commune,section,numero,zone,verdict,projet,status,download_slug,order_ref,agent,perso,envois,vu_le,vu_nb,vu_dernier').eq('user_id', u.id).order('created_at', { ascending: false }).limit(2000).then(function (r) {
        ALL = (r.data || []).filter(function (d) { return d.status !== 'error'; });
        Promise.all([Auth.account(), Auth.agents ? Auth.agents() : []]).then(function (v) {
          var c = v[0], noms = (v[1] || []).map(function (a) { return a.nom; });
          if (c && c.illimite) { ALL = ALL.concat(exemples(noms)).sort(function (a, b) { return a.created_at < b.created_at ? 1 : -1; }); var nt = document.getElementById('bo-note'); if (nt) nt.hidden = false; }
          render();
        }).catch(render);
      });
    });
    $('bo-per').addEventListener('change', function () { window.__boLim = 50; render(); });
    $('bo-q').addEventListener('input', render);
    ['bo-fa', 'bo-fc', 'bo-fs', 'bo-tri'].forEach(function (k) { var el = $(k); if (el) el.addEventListener('change', function () { window.__boLim = 50; render(); }); });
    $('bo-exp').addEventListener('click', exporter);
    $('bo-more').addEventListener('click', function () { window.__boLim = (window.__boLim || 50) + 100; render(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
