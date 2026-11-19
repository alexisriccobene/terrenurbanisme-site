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
    var DM = { agence: ['Lancer une démonstration agence', '/?commune=' + encodeURIComponent('Porto-Vecchio (2A)') + '&section=G&numero=1766#recherche'], mairie: ['Lancer la démonstration habitant', '/ville/porto-vecchio'], particulier: ['Lancer une démonstration particulier', '/?commune=' + encodeURIComponent('Sotta (2A)') + '&section=B&numero=842#recherche'] }[mode] || ['Lancer la démonstration', '/'];
    if ($('esp-demo')) { $('esp-demo-l').textContent = DM[0]; $('esp-demo').href = DM[1]; }
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
  // CSS de l'espace mairie, limité au bloc #esp-mairie pour ne rien changer au reste de la page
  function scope(css) {
    var out = '', i = 0, n = css.length;
    while (i < n) {
      var o = css.indexOf('{', i); if (o < 0) break;
      var sel = css.slice(i, o).trim(), d = 1, k = o + 1;
      while (k < n && d) { if (css[k] === '{') d++; else if (css[k] === '}') d--; k++; }
      var body = css.slice(o + 1, k - 1);
      if (/^@media/.test(sel)) out += sel + '{' + scope(body) + '}';
      else if (/^@/.test(sel)) out += sel + '{' + body + '}';
      else {
        var ss = sel.split(',').map(function (x) { return x.trim(); }).filter(function (x) { return x && !/^(body|html|\[hidden\]|\.em-top|\.em-brand|\.em-login|\.em-lcard|\.em-lico|\.em-lsub|\.em-lerr|\.em-lhelp|\.em-rem|\.em-out|\.em-back|\.em-ville)\b/.test(x); });
        if (ss.length) out += ss.map(function (x) { return '#esp-mairie ' + x; }).join(',') + '{' + body + '}';
      }
      i = k;
    }
    return out;
  }
  /* ---------- Mode mairie : l'espace mairie de démonstration, sur la même page ---------- */
  function drawMairie() {
    var box = $('esp-mairie'); if (box.dataset.ok) return; box.dataset.ok = '1';
    box.innerHTML = '<p class="empty">Chargement de l\'espace mairie…</p>';
    Promise.all([fetch('/espace-mairie.html', { cache: 'no-cache' }).then(function (r) { return r.text(); }), sb.functions.invoke('stripe-webhook', { body: { action: 'ville_demo' } })]).then(function (x) {
      var r = x[1]; if (r.error || !r.data || !r.data.k) throw new Error('ville');
      var doc = new DOMParser().parseFromString(x[0], 'text/html'), main = doc.getElementById('em-app'), st0 = doc.querySelector('style');
      if (!main) throw new Error('page');
      try { sessionStorage.setItem('tu_mairie', JSON.stringify({ slug: r.data.slug, k: r.data.k })); } catch (e) {}
      if (st0) { var st = document.createElement('style'); st.textContent = scope(st0.textContent); document.head.appendChild(st); }
      main.classList.remove('wrap');
      box.innerHTML = '<div hidden><div id="em-login"><form id="em-lf"><input name="identifiant"><input name="mdp" type="password"><input name="rester" type="checkbox"><button type="submit">ok</button><p class="em-lerr"></p></form></div><button id="em-out" type="button"></button><div id="em-ville"></div><a id="em-back"></a></div>';
      box.appendChild(document.importNode(main, true));
      window.TU_MAIRIE_EMBED = true;
      var sc = document.createElement('script'); sc.src = '/assets/espace-mairie.js?v=v92'; document.body.appendChild(sc);
    }).catch(function () { box.dataset.ok = ''; box.innerHTML = '<p class="empty">L\'espace mairie de démonstration n\'a pas pu se charger. Rechargez la page.</p>'; });
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('#esp-demo'); if (!a || !document.body.classList.contains('mode-mairie')) return;
    var d = $('em-dopen'); if (d && d.href && /[?&]k=/.test(d.href)) a.href = d.href;
  }, true);
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
      if (String(a.id) === String(openId)) return '<div class="ag-ed" data-id="' + a.id + '"><div class="ag-pcol">' + av(a, true) + '<label class="up-btn sm"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 18a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 18 8.5a4 4 0 0 1 .5 7.97"/><path d="M12 12v8"/><path d="m8.5 15.5 3.5-3.5 3.5 3.5"/></svg><span><b>' + (a.photo ? 'Changer la photo' : 'Ajouter une photo') + '</b></span><input type="file" accept="image/png,image/jpeg"></label></div>'
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
    var setAv = function (u) { if (u) { $('eh-logo').innerHTML = '<img alt="" src="' + u + '" style="width:100%;height:100%;object-fit:cover;max-width:none;max-height:none">'; var pa = $('pf-av'); if (pa) pa.innerHTML = '<img alt="" src="' + u + '">'; } };
    // Mon profil : nom, téléphone, e-mail et photo, repris sur la carte « Votre conseiller » des rapports
    var card = document.createElement('div'); card.className = 'esp-card'; card.id = 'esp-profil'; card.style.marginBottom = '28px';
    var CL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 18a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 18 8.5a4 4 0 0 1 .5 7.97"/><path d="M12 12v8"/><path d="m8.5 15.5 3.5-3.5 3.5 3.5"/></svg>';
    card.innerHTML = '<div class="esp-card-h"><div><h2>Mon profil</h2><p>Votre photo, votre téléphone et votre e-mail figurent sur la carte « Votre conseiller » des rapports remis à vos clients.</p></div></div>'
      + '<div class="ag-ed" style="border:0;padding:0"><div class="ag-pcol"><span class="ag-av" id="pf-av">' + esc(initials(M.nom)) + '</span><label class="up-btn sm">' + CL + '<span><b>Changer la photo</b></span><input type="file" id="pf-file" accept="image/png,image/jpeg"></label></div>'
      + '<div class="f"><label>Prénom et nom<input id="pf-nom" maxlength="80" value="' + esc(M.nom) + '"></label><label>Téléphone<input id="pf-tel" maxlength="30" inputmode="tel" value="' + esc(M.telephone || '') + '"></label><label style="grid-column:1/-1">E-mail affiché sur les rapports<input id="pf-email" type="email" maxlength="120" value="' + esc(M.email || '') + '"></label>'
      + '<div class="a"><button type="button" class="btn" id="pf-save">Enregistrer</button><span id="pf-msg" class="ag-msg" style="margin:0"></span></div></div></div>';
    var off = $('esp-offre'); off.parentNode.insertBefore(card, off.nextSibling);
    setAv(M.photo_url);
    var photo = null, pmsg = function (t, er) { var m = $('pf-msg'); m.textContent = t; m.style.color = er ? 'var(--non,#B3402F)' : 'var(--ok,#2E7D4F)'; };
    $('pf-file').addEventListener('change', function (e) {
      var f = e.target.files[0]; e.target.value = ''; if (!f) return;
      if (!/^image\/(png|jpeg)$/.test(f.type)) { pmsg('Format accepté : JPG ou PNG.', true); return; }
      cropper(f).then(function (blob) { if (!blob) return; var rd = new FileReader(); rd.onload = function () { photo = rd.result; setAv(photo); pmsg('Photo prête : cliquez sur Enregistrer.'); }; rd.readAsDataURL(blob); });
    });
    $('pf-save').addEventListener('click', function () {
      var bt = $('pf-save'), nom = $('pf-nom').value.trim();
      if (nom.length < 2) { pmsg('Indiquez votre prénom et votre nom.', true); return; }
      bt.disabled = true; pmsg('Enregistrement…');
      sb.functions.invoke('stripe-webhook', { body: { action: 'membre_profil', nom: nom, telephone: $('pf-tel').value.trim(), email: $('pf-email').value.trim(), photo: photo } }).then(function (r) {
        bt.disabled = false;
        if (r.error || !r.data || !r.data.ok) { pmsg('L\'enregistrement n\'a pas abouti. Réessayez.', true); return; }
        photo = null; M.nom = r.data.nom; $('eh-nom').textContent = M.nom; A._ag = null;
        pmsg('Profil enregistré. Il figurera sur vos prochains rapports.');
      });
    });
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
