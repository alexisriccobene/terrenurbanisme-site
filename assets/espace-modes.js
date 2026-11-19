/* Mon espace : modes de présentation (agence, mairie, particulier), en-tête de la structure et équipe */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  if (!$('esp-pro')) return;
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var TYPES = { agence: 'Agence immobilière', conciergerie: 'Conciergerie', notaire: 'Étude notariale', geometre: 'Cabinet de géomètre', architecte: 'Architecte', promoteur: 'Promoteur', constructeur: 'Constructeur', courtier: 'Courtier', banque: 'Banque' };
  var A, sb, U, C, MQ = {};
  var initials = function (n) { return String(n || '?').split(/\s+/).filter(Boolean).slice(0, 2).map(function (x) { return x.charAt(0).toUpperCase(); }).join(''); };

  /* ---------- Modes ---------- */
  function getMode() { try { return localStorage.getItem('tu_mode') || 'agence'; } catch (e) { return 'agence'; } }
  function setMode(m) { try { localStorage.setItem('tu_mode', m); } catch (e) {} }
  function apply(mode) {
    document.body.classList.remove('mode-agence', 'mode-mairie', 'mode-particulier');
    document.body.classList.add('mode-' + mode);
    document.querySelectorAll('#esp-mode button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-mode') === mode ? 'true' : 'false'); });
    var h1 = document.querySelector('#espace h1');
    $('esp-pro').hidden = mode !== 'agence';
    $('esp-hero').hidden = mode !== 'agence';
    $('esp-mairie').hidden = mode !== 'mairie';
    if ($('esp-bo')) $('esp-bo').hidden = mode !== 'agence';
    if (mode === 'agence') { if (h1) h1.textContent = MQ.nom || 'Mon espace'; $('esp-rt').textContent = 'Rapports de l\'agence'; }
    else if (mode === 'mairie') { if (h1) h1.textContent = 'Espace mairie'; $('esp-rt').textContent = 'Rapports remis aux habitants'; drawMairie(); }
    else { if (h1) h1.textContent = 'Mon espace'; $('esp-rt').textContent = 'Mes rapports complets'; }
  }

  /* ---------- En-tête de la structure ---------- */
  function drawHero() {
    $('eh-nom').textContent = MQ.nom || 'Votre agence';
    $('eh-type').textContent = TYPES[MQ.type] || 'Agence immobilière';
    var site = MQ.site ? String(MQ.site).replace(/^https?:\/\//, '').replace(/[?#].*$/, '').replace(/\/$/, '') : '';
    $('eh-co').textContent = [MQ.telephone, MQ.email, site].filter(Boolean).join('  ·  ') || 'Ajoutez vos coordonnées dans « Votre identité sur les rapports ».';
    var lg = $('eh-logo');
    if (MQ.logo_path) sb.storage.from('logos').download(MQ.logo_path).then(function (d) { if (d.data) lg.innerHTML = '<img alt="Logo" src="' + URL.createObjectURL(d.data) + '">'; });
    else lg.textContent = initials(MQ.nom || 'A');
    var h1 = document.querySelector('#espace h1'); if (h1 && document.body.classList.contains('mode-agence') && MQ.nom) h1.textContent = MQ.nom;
  }

  /* ---------- Mode mairie (présentation) ---------- */
  function drawMairie() {
    var box = $('esp-mairie'); if (box.dataset.ok) return; box.dataset.ok = '1';
    box.innerHTML = '<div class="esp-hero" style="margin:0 0 6px"><div class="esp-hero-logo">M</div><div class="esp-hero-t"><small>Commune · démonstration</small><h2>Mairie de Porto-Vecchio</h2><p>Les habitants obtiennent leur rapport d\'urbanisme depuis le site de la mairie, sur les parcelles de la commune.</p></div></div>'
      + '<div class="em-grid"><div class="em-k"><small>Rapports remis ce mois-ci</small><b>38</b></div><div class="em-k"><small>Stock restant</small><b>212</b></div><div class="em-k"><small>Appels évités au service urbanisme</small><b>≈ 60</b></div></div>'
      + '<div class="esp-card"><div class="esp-card-h"><div><h2>Ce que voit la mairie</h2><p>Les demandes des habitants parcelle par parcelle, le bouton à placer sur le site de la commune et le suivi du stock.</p></div><a class="btn" href="/espace-mairie.html">Ouvrir l\'espace mairie</a></div></div>';
  }

  /* ---------- Équipe ---------- */
  var AG = [], urls = {}, openId = null;
  function say(t, err) { var m = $('ag-msg'); m.textContent = t || ''; m.style.color = err ? 'var(--non,#B3402F)' : 'var(--ok,#2E7D4F)'; }
  function photoUrl(a) {
    if (!a.photo) return Promise.resolve('');
    if (urls[a.photo]) return Promise.resolve(urls[a.photo]);
    return sb.storage.from('perso').createSignedUrl(a.photo, 3600).then(function (r) { var u = r.data && r.data.signedUrl || ''; urls[a.photo] = u; return u; });
  }
  function av(a, big) { return '<span class="ag-av" data-av="' + a.id + '">' + esc(initials(a.nom)) + '</span>'; }
  function fillAv() { AG.forEach(function (a) { photoUrl(a).then(function (u) { if (!u) return; document.querySelectorAll('[data-av="' + a.id + '"]').forEach(function (el) { el.innerHTML = '<img alt="" src="' + u + '">'; }); }); }); }
  function load(newId) {
    return sb.from('pro_agents').select('id,nom,telephone,email,photo,member_id,acces_le').eq('user_id', U.id).order('nom').then(function (r) { AG = r.data || []; draw(newId); });
  }
  function draw(newId) {
    var list = $('ag-list');
    if (!AG.length) { list.innerHTML = '<p style="color:var(--muet);font-size:14px;margin:6px 0 0">Aucun collaborateur pour le moment. Ajoutez votre équipe : chacun apparaîtra sur les rapports qu\'il remet.</p>'; return; }
    list.innerHTML = AG.map(function (a) {
      if (String(a.id) === String(openId)) return '<div class="ag-ed" data-id="' + a.id + '"><div style="text-align:center">' + av(a, true) + '<br><label class="up-btn sm"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 18a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 18 8.5a4 4 0 0 1 .5 7.97"/><path d="M12 12v8"/><path d="m8.5 15.5 3.5-3.5 3.5 3.5"/></svg><span><b>' + (a.photo ? 'Changer la photo' : 'Ajouter une photo') + '</b></span><input type="file" accept="image/png,image/jpeg"></label></div>'
        + '<div class="f"><label>Prénom et nom<input name="nom" maxlength="80" value="' + esc(a.nom) + '"></label><label>Téléphone<input name="telephone" maxlength="30" inputmode="tel" value="' + esc(a.telephone || '') + '"></label><label style="grid-column:1/-1">E-mail<input name="email" type="email" maxlength="120" value="' + esc(a.email || '') + '"></label>'
        + '<div class="ag-acc"><div><b>' + (a.member_id ? 'Accès personnel actif' : 'Accès personnel') + '</b><span>' + (a.member_id ? 'Il se connecte avec ' + esc(a.email || 'son e-mail') + '. Ses rapports sont signés à son nom et décomptés sur vos crédits.' : 'Créez son identifiant : il reçoit un e-mail pour choisir son mot de passe. Ses rapports seront signés à son nom.') + '</span></div><button type="button" class="btn ghost" data-acc>' + (a.member_id ? 'Renvoyer l\'accès' : 'Créer son accès') + '</button></div>'
        + '<div class="a"><button type="button" class="btn" data-save>Enregistrer</button><button type="button" class="btn ghost" data-close>Fermer</button><button type="button" class="del" data-del>Supprimer</button></div></div></div>';
      return '<button type="button" class="ag-c' + (String(a.id) === String(newId) ? ' new' : '') + '" data-open="' + a.id + '">' + av(a) + '<span class="ag-i"><b>' + esc(a.nom) + '</b><span>' + esc(a.telephone || 'Téléphone à ajouter') + '</span><span>' + esc(a.email || 'E-mail à ajouter') + '</span><em>' + (a.member_id ? '<i class="ag-ok">Accès actif</i> · ' : '') + 'Modifier</em></span></button>';
    }).join('');
    fillAv();
    list.querySelectorAll('[data-open]').forEach(function (b) { b.addEventListener('click', function () { openId = b.getAttribute('data-open'); say(''); draw(); }); });
    var ed = list.querySelector('.ag-ed'); if (!ed) return;
    var a = AG.filter(function (x) { return String(x.id) === String(openId); })[0];
    ed.querySelector('[data-close]').addEventListener('click', function () { openId = null; draw(); });
    ed.querySelector('[data-save]').addEventListener('click', function (e) {
      var bt = e.target, row = { nom: ed.querySelector('[name=nom]').value.trim().slice(0, 80), telephone: ed.querySelector('[name=telephone]').value.trim().slice(0, 30) || null, email: ed.querySelector('[name=email]').value.trim().slice(0, 120) || null };
      if (row.nom.length < 2) { say('Indiquez le prénom et le nom.', true); return; }
      bt.disabled = true;
      sb.from('pro_agents').update(row).eq('id', a.id).then(function (r) { bt.disabled = false; if (r.error) { say('Enregistrement impossible, réessayez.', true); return; } say(row.nom + ' est à jour.'); openId = null; load(a.id); });
    });
    ed.querySelector('[data-acc]').addEventListener('click', function (e) {
      var bt = e.target, em = ed.querySelector('[name=email]').value.trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) { say('Indiquez d\'abord l\'e-mail du collaborateur, puis enregistrez.', true); return; }
      if (em !== (a.email || '')) { say('Enregistrez d\'abord le nouvel e-mail, puis créez l\'accès.', true); return; }
      bt.disabled = true; bt.textContent = 'Envoi…';
      sb.functions.invoke('stripe-webhook', { body: { action: 'agent_acces', agent_id: a.id } }).then(function (r) {
        bt.disabled = false;
        var er = r.error ? (r.error.context && r.error.context.json ? r.error.context.json() : Promise.resolve({})) : null;
        if (er) return er.then(function (j) { var c = j && j.error; say(c === 'deja_membre' ? 'Cette adresse est déjà le collaborateur d\'une autre agence.' : c === 'email_agence' ? 'Utilisez l\'e-mail personnel du collaborateur, pas celui de l\'agence.' : 'L\'accès n\'a pas pu être créé. Réessayez.', true); bt.textContent = a.member_id ? 'Renvoyer l\'accès' : 'Créer son accès'; });
        say(r.data && r.data.mail === false ? 'Accès créé. L\'e-mail n\'est pas parti : demandez-lui d\'aller sur « Mot de passe oublié » avec son adresse.' : 'C\'est envoyé : ' + a.nom + ' reçoit un e-mail « Votre accès TerrenUrbanisme » avec le bouton « Créer mon accès ». S\'il ne le voit pas, il regarde dans ses courriers indésirables.');
        load(a.id);
      });
    });
    var del = ed.querySelector('[data-del]');
    del.addEventListener('click', function () {
      if (!del.dataset.sure) { del.dataset.sure = '1'; del.textContent = 'Confirmer la suppression'; return; }
      sb.from('pro_agents').delete().eq('id', a.id).then(function (r) { if (r.error) { say('Suppression impossible, réessayez.', true); return; } say(a.nom + ' a été retiré.'); openId = null; load(); });
    });
    ed.querySelector('input[type=file]').addEventListener('change', function (e) {
      var f = e.target.files[0]; e.target.value = ''; if (!f) return;
      if (!/^image\/(png|jpeg)$/.test(f.type)) { say('Format accepté : JPG ou PNG.', true); return; }
      say('');
      cropper(f).then(function (blob) {
        if (!blob) return;
        say('Envoi de la photo…');
        var path = U.id + '/agents/' + a.id + '-' + Date.now() + '.jpg';
        return sb.storage.from('perso').upload(path, blob, { contentType: 'image/jpeg' }).then(function (r) { if (r.error) throw r.error; return sb.from('pro_agents').update({ photo: path }).eq('id', a.id); }).then(function (r) { if (r.error) throw r.error; a.photo = path; urls[path] = URL.createObjectURL(blob); say('Photo enregistrée. Elle figurera sur les prochaines versions client.'); draw(); });
      }).catch(function () { say('La photo n\'a pas pu être envoyée. Réessayez.', true); });
    });
  }
  // Recadrage de la photo dans un rond : glisser pour placer, curseur pour zoomer
  function cropper(f) {
    return new Promise(function (res) {
      var img = new Image(), url = URL.createObjectURL(f);
      img.onerror = function () { say('Cette image ne peut pas être lue. Choisissez une photo JPG ou PNG.', true); res(null); };
      img.onload = function () {
        var S = 280, base = Math.max(S / img.width, S / img.height), z = 1, ox = 0, oy = 0;
        var wrap = document.createElement('div'); wrap.className = 'cr-ov';
        wrap.innerHTML = '<div class="cr-box" role="dialog" aria-modal="true" aria-label="Recadrer la photo"><h3>Recadrer la photo</h3><p>Faites glisser la photo pour la placer dans le rond.</p><div class="cr-st"><canvas width="' + S * 2 + '" height="' + S * 2 + '"></canvas><div class="cr-mask"></div></div><label class="cr-z">Zoom<input type="range" min="1" max="3" step="0.01" value="1"></label><div class="cr-a"><button type="button" class="btn ghost" data-x>Annuler</button><button type="button" class="btn" data-ok>Valider la photo</button></div></div>';
        document.body.appendChild(wrap); document.body.style.overflow = 'hidden';
        var cv = wrap.querySelector('canvas'), cx = cv.getContext('2d'), rg = wrap.querySelector('input[type=range]');
        function clamp() { var w = img.width * base * z, h = img.height * base * z, mx = (w - S) / 2, my = (h - S) / 2; ox = Math.max(-mx, Math.min(mx, ox)); oy = Math.max(-my, Math.min(my, oy)); }
        function paint(ctx, size) { var k = size / S, w = img.width * base * z * k, h = img.height * base * z * k; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, size, size); ctx.drawImage(img, (size - w) / 2 + ox * k, (size - h) / 2 + oy * k, w, h); }
        function redraw() { clamp(); paint(cx, S * 2); }
        redraw();
        var drag = null;
        cv.addEventListener('pointerdown', function (e) { drag = { x: e.clientX, y: e.clientY, ox: ox, oy: oy }; cv.setPointerCapture(e.pointerId); });
        cv.addEventListener('pointermove', function (e) { if (!drag) return; var k = S / (cv.clientWidth || S); ox = drag.ox + (e.clientX - drag.x) * k; oy = drag.oy + (e.clientY - drag.y) * k; redraw(); });
        cv.addEventListener('pointerup', function () { drag = null; }); cv.addEventListener('pointercancel', function () { drag = null; });
        cv.addEventListener('wheel', function (e) { e.preventDefault(); z = Math.max(1, Math.min(3, z - e.deltaY * 0.002)); rg.value = z; redraw(); }, { passive: false });
        rg.addEventListener('input', function () { z = Number(rg.value); redraw(); });
        function close(v) { wrap.remove(); document.body.style.overflow = ''; URL.revokeObjectURL(url); res(v); }
        wrap.querySelector('[data-x]').addEventListener('click', function () { close(null); });
        wrap.querySelector('[data-ok]').addEventListener('click', function () { var o = document.createElement('canvas'); o.width = o.height = 480; paint(o.getContext('2d'), 480); o.toBlob(function (b) { close(b); }, 'image/jpeg', 0.88); });
        document.addEventListener('keydown', function esc(e) { if (e.key === 'Escape' && document.body.contains(wrap)) { document.removeEventListener('keydown', esc); close(null); } });
      };
      img.src = url;
    });
  }
  function shrink(f) {
    return new Promise(function (res, rej) {
      var img = new Image(); img.onload = function () {
        var s = Math.min(1, 480 / Math.min(img.width, img.height)), w = Math.round(img.width * s), h = Math.round(img.height * s), c = document.createElement('canvas'); c.width = w; c.height = h;
        c.getContext('2d').drawImage(img, 0, 0, w, h); c.toBlob(function (b) { b ? res(b) : rej(); }, 'image/jpeg', 0.86);
      }; img.onerror = rej; img.src = URL.createObjectURL(f);
    });
  }
  var mfile = $('mq-file'); if (mfile) mfile.addEventListener('change', function () { var f = mfile.files[0], el = $('mq-fname'); if (el) el.textContent = f ? f.name : 'PNG ou JPG, 2 Mo maximum'; });
  function initAgents() {
    $('esp-agents').hidden = false;
    $('ag-add').addEventListener('click', function () { var f = $('ag-form'); f.hidden = !f.hidden; if (!f.hidden) f.nom.focus(); });
    $('ag-form').addEventListener('submit', function (e) {
      e.preventDefault(); var f = e.target, n = f.nom.value.trim();
      if (n.length < 2) { say('Indiquez le prénom et le nom.', true); return; }
      var bt = f.querySelector('button'); bt.disabled = true;
      sb.from('pro_agents').insert({ user_id: U.id, nom: n.slice(0, 80), telephone: f.telephone.value.trim().slice(0, 30) || null, email: f.email.value.trim().slice(0, 120) || null }).select('id').then(function (r) {
        bt.disabled = false;
        if (r.error) { say('Ajout impossible, réessayez.', true); return; }
        f.reset(); f.hidden = true; say(n + ' a été ajouté. Cliquez sur sa carte pour ajouter sa photo.'); load(r.data && r.data[0] && r.data[0].id);
      });
    });
    load();
  }

  /* ---------- Collaborateur connecté avec son accès personnel ---------- */
  function membre(M) {
    document.body.classList.add('mode-membre');
    $('esp-pro').hidden = true; $('esp-mairie').hidden = true;
    $('esp-hero').hidden = false; if ($('esp-bo')) $('esp-bo').hidden = false;
    $('eh-type').textContent = 'Collaborateur'; $('eh-nom').textContent = M.nom; $('eh-co').textContent = M.agence + ' · vos rapports sont établis à votre nom et décomptés sur les crédits de l\'agence.';
    $('eh-logo').textContent = initials(M.nom);
    var h1 = document.querySelector('#espace h1'); if (h1) h1.textContent = M.agence;
    var bh = document.querySelector('.esp-bo-h h2'); if (bh) bh.textContent = 'Mes rapports';
    var bp = document.querySelector('.esp-bo-h p'); if (bp) bp.textContent = 'Les rapports que vous avez demandés, les envois à vos clients et leurs ouvertures.';
    sb.from('pro_agents').select('id,photo').eq('member_id', U.id).maybeSingle().then(function (r) { var a = r.data; if (a && a.photo) sb.storage.from('perso').createSignedUrl(a.photo, 3600).then(function (x) { if (x.data) $('eh-logo').innerHTML = '<img alt="" src="' + x.data.signedUrl + '" style="width:100%;height:100%;object-fit:cover;max-width:none;max-height:none">'; }); });
  }

  /* ---------- Démarrage ---------- */
  function boot() {
    A = window.TUAuth; if (!A || !A.ready || !A.client) { setTimeout(boot, 120); return; }
    sb = A.client;
    A.user().then(function (u) {
      if (!u) return; U = u;
      return A.account().then(function (c) {
        C = c || {};
        if (C.membre) { membre(C.membre); return; }
        var pro = !!(C.illimite || C.pro);
        var mode = C.illimite ? getMode() : pro ? 'agence' : 'particulier';
        if (C.illimite) {
          $('esp-mode').hidden = false;
          document.querySelectorAll('#esp-mode button').forEach(function (b) { b.addEventListener('click', function () { var m = b.getAttribute('data-mode'); setMode(m); apply(m); }); });
        }
        if (pro) {
          initAgents();
          sb.from('marques').select('*').eq('user_id', u.id).maybeSingle().then(function (r) { MQ = r.data || {}; drawHero(); });
          var mf = $('mq-form'); if (mf) mf.addEventListener('submit', function () { setTimeout(function () { sb.from('marques').select('*').eq('user_id', u.id).maybeSingle().then(function (r) { MQ = r.data || {}; drawHero(); }); }, 2500); });
        }
        apply(mode);
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
