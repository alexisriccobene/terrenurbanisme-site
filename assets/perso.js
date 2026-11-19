/* Version client d'un rapport : choix des rubriques, avis de valeur, photos et client (agences) */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var A = window.TUAuth, id = new URLSearchParams(location.search).get('id') || '';
  var LIB = {
    'Identification de la parcelle': 'Localisation, surface, références cadastrales',
    'Règles d\'urbanisme applicables': 'Document d\'urbanisme, zone, prescriptions, servitudes',
    'Ce que vous pouvez construire': 'Règlement de la zone, surface constructible, implantation',
    'Règles propres à la Corse': 'Loi Littoral, loi Montagne, PADDUC',
    'Loi Littoral et loi Montagne': 'Lois d\'aménagement',
    'Risques naturels et technologiques': 'Inondation, feu de forêt, argiles, catastrophes naturelles',
    'Le terrain : accès, relief et réseaux': 'Accès, pente, ensoleillement, assainissement, électricité, eau, fibre',
    'Valeur de marché': 'Fourchette de prix d\'après les ventes publiées',
    'Conditions de vente du terrain': 'Terrain agricole : SAFER, fermier en place',
    'Environnement et marché immobilier': 'Espaces naturels et ventes immobilières alentour',
    'Historique du site': 'Photos aériennes depuis 1950, permis accordés autour',
    'Opportunités autour du terrain': 'Grands terrains peu bâtis, logements énergivores',
    'Votre projet, étape par étape': 'Démarches, délais, coûts des études, taxe d\'aménagement',
    'État des risques (ERP) pré-rempli': 'Formulaire réglementaire',
    'Professionnels recommandés': 'Professionnels partenaires de la commune'
  };
  // Ce que le client ne verra plus si la rubrique est décochée
  var DEL = {
    'Identification de la parcelle': 'la fiche de la parcelle, les plans de situation et la vue aérienne',
    'Règles d\'urbanisme applicables': 'la zone du PLU, le plan de zonage, les prescriptions et les servitudes',
    'Ce que vous pouvez construire': 'les règles de la zone, la surface constructible et le plan d\'implantation',
    'Règles propres à la Corse': 'la loi Littoral, la loi Montagne et le PADDUC',
    'Loi Littoral et loi Montagne': 'la distance au rivage et les règles des lois Littoral et Montagne',
    'Risques naturels et technologiques': 'la carte des risques et les arrêtés de catastrophe naturelle',
    'Le terrain : accès, relief et réseaux': 'l\'accès, la pente, l\'ensoleillement, l\'assainissement et les raccordements',
    'Valeur de marché': 'le détail des ventes et l\'évolution des prix (notre fourchette reste rappelée à côté de votre prix)',
    'Conditions de vente du terrain': 'les règles SAFER et les droits du fermier en place',
    'Environnement et marché immobilier': 'les espaces naturels, les espèces protégées et les ventes alentour',
    'Historique du site': 'les photos aériennes depuis 1950 et les permis accordés autour',
    'Opportunités autour du terrain': 'la liste des grands terrains peu bâtis et des logements énergivores',
    'Votre projet, étape par étape': 'les démarches, les délais, le coût des études et la taxe d\'aménagement',
    'État des risques (ERP) pré-rempli': 'le formulaire d\'état des risques à joindre à la vente',
    'Professionnels recommandés': 'la liste des professionnels partenaires'
  };
  // Aperçu des pages retirées : les pages de chaque rubrique sont repérées dans le PDF du rapport
  var PV = { doc: null, map: null, p: null, cache: {} };
  function nrm(t) { return String(t || '').toLowerCase().replace(/[\u2019']/g, '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, ''); }
  function loadPV() {
    if (PV.p) return PV.p;
    if (!MAIL.slug) return Promise.reject(new Error('slug'));
    PV.p = import('/assets/pdfjs/pdf.min.mjs').then(function (lib) {
      lib.GlobalWorkerOptions.workerSrc = '/assets/pdfjs/pdf.worker.min.mjs';
      return lib.getDocument({ url: '/rapport/' + encodeURIComponent(MAIL.slug) + '.pdf', isEvalSupported: false }).promise;
    }).then(function (doc) {
      PV.doc = doc;
      var titles = Object.keys(LIB).sort(function (a, b) { return b.length - a.length; }).map(function (t) { return [t, nrm(t)]; });
      var STOP = [[null, 'sommaire'], [null, 'synthese'], [null, 'recommandationdelagence'], [null, 'avertissementetsources'], [null, 'annexe']];
      var map = { especes: [] }, cur = null, n = 0;
      function next() {
        if (++n > doc.numPages) { PV.map = map; return map; }
        return doc.getPage(n).then(function (pg) {
          return pg.getTextContent().then(function (tc) {
            var h = pg.view[3], top = '', all = '';
            tc.items.forEach(function (it) { var y = it.transform ? it.transform[5] : 0; all += it.str; if (y > h - 190) top += it.str; });
            var nt = nrm(top);
            // Le titre de rubrique placé le plus haut sur la page (bandeau de la rubrique en cours) l'emporte
            var bi = 1e9, bt;
            titles.concat(STOP).forEach(function (x) { var i = nt.indexOf(x[1]); if (i >= 0 && i < bi) { bi = i; bt = x[0]; } });
            if (bt !== undefined) cur = bt;
            if (cur) { (map[cur] = map[cur] || []).push(n); if (cur === 'Environnement et marché immobilier' && /especesprotegees/.test(nrm(all))) map.especes.push(n); }
            return next();
          });
        });
      }
      return next();
    });
    return PV.p;
  }
  function thumb(n) {
    if (PV.cache[n]) return Promise.resolve(PV.cache[n]);
    return PV.doc.getPage(n).then(function (pg) {
      var v0 = pg.getViewport({ scale: 1 }), sc = 220 / v0.width, v = pg.getViewport({ scale: sc });
      var c = document.createElement('canvas'); c.width = v.width; c.height = v.height;
      return pg.render({ canvasContext: c.getContext('2d'), viewport: v }).promise.then(function () { PV.cache[n] = c.toDataURL('image/jpeg', 0.8); return PV.cache[n]; });
    });
  }
  // Grand aperçu d'une page retirée (clic sur la miniature)
  var LB = { pages: [], i: 0 };
  function big(n) {
    return PV.doc.getPage(n).then(function (pg) {
      var v0 = pg.getViewport({ scale: 1 }), sc = Math.min(2.2, 1500 / v0.width), v = pg.getViewport({ scale: sc });
      var c = document.createElement('canvas'); c.width = v.width; c.height = v.height;
      return pg.render({ canvasContext: c.getContext('2d'), viewport: v }).promise.then(function () { return c.toDataURL('image/jpeg', 0.88); });
    });
  }
  function lbShow() {
    var n = LB.pages[LB.i]; $('ps-lb-t').textContent = 'Page ' + n + ' · ' + (LB.i + 1) + ' sur ' + LB.pages.length;
    $('ps-lb-prev').disabled = LB.i === 0; $('ps-lb-next').disabled = LB.i === LB.pages.length - 1;
    $('ps-lb-i').src = PV.cache[n] || ''; $('ps-lb-i').alt = 'Page ' + n;
    big(n).then(function (src) { if (LB.pages[LB.i] === n) $('ps-lb-i').src = src; });
  }
  function lbOpen(pages, n) { LB.pages = pages; LB.i = Math.max(0, pages.indexOf(n)); $('ps-lb').hidden = false; document.body.style.overflow = 'hidden'; lbShow(); $('ps-lb-x').focus(); }
  function lbClose() { $('ps-lb').hidden = true; document.body.style.overflow = ''; }
  document.addEventListener('DOMContentLoaded', function () {
    if (!$('ps-lb')) return;
    $('ps-lb-x').addEventListener('click', lbClose);
    $('ps-lb-prev').addEventListener('click', function () { if (LB.i > 0) { LB.i--; lbShow(); } });
    $('ps-lb-next').addEventListener('click', function () { if (LB.i < LB.pages.length - 1) { LB.i++; lbShow(); } });
    $('ps-lb').addEventListener('click', function (e) { if (e.target === $('ps-lb') || e.target.className === 'ps-lb-img') lbClose(); });
    document.addEventListener('keydown', function (e) { if ($('ps-lb').hidden) return; if (e.key === 'Escape') lbClose(); if (e.key === 'ArrowLeft') $('ps-lb-prev').click(); if (e.key === 'ArrowRight') $('ps-lb-next').click(); });
  });
  function showPV(box, key) {
    box.hidden = false; box.innerHTML = '<p class="ps-pv-t">Chargement de l\'aperçu…</p>';
    loadPV().then(function (map) {
      var pages = map[key] || [];
      if (!pages.length) { box.innerHTML = '<p class="ps-pv-t">Cette rubrique ne figure pas dans le rapport de ce terrain.</p>'; return; }
      var shown = pages.slice(0, 8);
      box.innerHTML = '<p class="ps-pv-t">' + (pages.length > 1 ? pages.length + ' pages retirées (p. ' + pages[0] + ' à ' + pages[pages.length - 1] + ')' : '1 page retirée (p. ' + pages[0] + ')') + '</p><div class="ps-pv-g">' + shown.map(function (n) { return '<figure data-n="' + n + '" tabindex="0" role="button" aria-label="Agrandir la page ' + n + '"><span>p. ' + n + '</span></figure>'; }).join('') + (pages.length > 8 ? '<figure class="more"><span>+ ' + (pages.length - 8) + '</span></figure>' : '') + '</div>';
      box.querySelectorAll('figure[data-n]').forEach(function (f) {
        var go = function () { lbOpen(pages, Number(f.getAttribute('data-n'))); };
        f.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); go(); });
        f.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
      });
      shown.reduce(function (pr, n) { return pr.then(function () { return thumb(n).then(function (src) { var f = box.querySelector('figure[data-n="' + n + '"]'); if (f) f.insertAdjacentHTML('afterbegin', '<img alt="Page ' + n + '" src="' + src + '">'); }); }); }, Promise.resolve());
    }).catch(function () { box.innerHTML = '<p class="ps-pv-t">L\'aperçu n\'est pas disponible pour ce rapport.</p>'; });
  }
  function drawCk() {
    var env = document.querySelector('[data-ch="Environnement et marché immobilier"]'), esp = document.querySelector('[data-sans="especes"]');
    if (esp) { esp.disabled = !!(env && !env.checked); if (esp.disabled) esp.checked = false; }
    var off = [];
    document.querySelectorAll('#ps-ch .ps-ck').forEach(function (l) {
      var c = l.querySelector('input'), o = l.querySelector('.ps-off'), t = c.getAttribute('data-ch') || 'Espèces protégées observées autour';
      l.classList.toggle('is-off', !c.checked);
      if (!c.checked) off.push(t);
      o.textContent = c.checked ? '' : (c.disabled ? 'Retiré avec la rubrique Environnement et marché immobilier.' : 'Retiré du rapport : ' + (c.getAttribute('data-sans') ? 'la liste des espèces protégées et le coût des études écologiques' : DEL[t] || 'cette rubrique') + '.');
    });
    document.querySelectorAll('#ps-ch .ps-pv').forEach(function (box) {
      var key = box.getAttribute('data-pv'), c = box.previousElementSibling && box.previousElementSibling.querySelector('input');
      if (!c || c.checked || c.disabled || !MAIL.slug) { box.hidden = true; box.innerHTML = ''; box.dataset.on = ''; return; }
      if (box.dataset.on) return;
      box.dataset.on = '1'; showPV(box, key);
    });
    var r = $('ps-off-sum'); if (r) r.textContent = off.length ? off.length + ' rubrique' + (off.length > 1 ? 's retirées' : ' retirée') + ' de la version client : ' + off.join(', ') + '.' : 'Toutes les rubriques sont incluses dans la version client.';
  }
  var photos = []; // { path, url }
  function msg(t, kind) { var m = $('ps-msg'); m.className = 'ps-msg' + (kind ? ' ps-' + kind : ''); m.textContent = t || ''; }
  function call(body) {
    return A.client.functions.invoke('stripe-webhook', { body: body }).then(function (r) {
      if (r.error) return (r.error.context && r.error.context.json ? r.error.context.json() : Promise.resolve({})).then(function (j) { var e = new Error(j && j.error || 'erreur'); e.code = j && j.error; throw e; });
      return r.data;
    });
  }
  function drawPhotos() {
    $('ps-ph').innerHTML = photos.map(function (p, i) { return '<div><img src="' + p.url + '" alt=""><button type="button" data-i="' + i + '">Retirer</button></div>'; }).join('');
    $('ps-ph').querySelectorAll('button').forEach(function (b) { b.addEventListener('click', function () { photos.splice(+b.getAttribute('data-i'), 1); drawPhotos(); }); });
  }
  // Photo réduite à 1600 px (JPEG) avant envoi
  function shrink(file) {
    return new Promise(function (res, rej) {
      var img = new Image(), u = URL.createObjectURL(file);
      img.onload = function () {
        var k = Math.min(1, 1600 / Math.max(img.width, img.height)), c = document.createElement('canvas');
        c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
        c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(u);
        c.toBlob(function (b) { b ? res(b) : rej(new Error('photo')); }, 'image/jpeg', 0.85);
      };
      img.onerror = function () { URL.revokeObjectURL(u); rej(new Error('photo')); };
      img.src = u;
    });
  }
  var MAIL = { url: '', ref: '', agent: '', cl: {} };
  function nomClient(c) { return [c.civ || '', c.nom || c.prenom || ''].join(' ').trim(); }
  function drawMail() {
    var f = $('ps-form'), c = { civ: f.civ.value, prenom: f.prenom.value.trim(), nom: f.nom.value.trim(), email: f.email.value.trim() };
    if (!$('ps-to').dataset.edit) $('ps-to').value = c.email;
    if (!$('ps-obj').dataset.edit) $('ps-obj').value = 'Votre rapport d\'urbanisme et avis de valeur' + (MAIL.ref ? ' · ' + MAIL.ref : '');
    var sal = c.civ === 'Mme' ? 'Madame' : c.civ === 'M.' ? 'Monsieur' : c.civ === 'M. et Mme' ? 'Madame, Monsieur' : '';
    var who = sal ? sal + (c.civ === 'M. et Mme' ? '' : ' ' + (c.nom || c.prenom)) : (c.prenom || c.nom || '');
    if (!$('ps-body').dataset.edit) $('ps-body').value = 'Bonjour' + (who ? ' ' + who : '') + ',\n\nVeuillez trouver ci-dessous le rapport d\'urbanisme détaillé de votre bien, accompagné de notre avis de valeur :\n\n' + (MAIL.url || '[le lien apparaîtra ici après la génération]') + '\n\nNous restons à votre entière disposition pour en échanger.\n\nBien cordialement,';
    var to = $('ps-to').value.trim(), body = $('ps-body').value;
    $('ps-mail').href = 'mailto:' + encodeURIComponent(to).replace(/%40/g, '@') + '?subject=' + encodeURIComponent($('ps-obj').value) + '&body=' + encodeURIComponent(body);
  }
  // Calcul affiché à l'agent : prix net vendeur, honoraires, prix attendu
  function drawCalc() {
    var f = $('ps-form'), box = $('ps-calc'); if (!box) return;
    var pc = Number(String(f.conseille.value).replace(/[^0-9]/g, '')), h = Number(String(f.hono.value).replace(',', '.')) || 0, n = Number(String(f.nego.value).replace(',', '.')) || 0;
    if (!pc || (!h && !n)) { box.hidden = true; return; }
    var e = function (v) { return Math.round(v).toLocaleString('fr-FR') + ' €'; }, out = [];
    if (h) { var net = Math.round(pc / (1 + h / 100) / 100) * 100; out.push('Prix net vendeur : <b>' + e(net) + '</b>'); out.push('Honoraires : ' + e(pc - net) + ' à la charge ' + (f.hono_charge.value === 'acquereur' ? 'de l\'acquéreur' : 'du vendeur')); }
    if (n) out.push('Prix de vente attendu : environ ' + e(Math.round(pc * (1 - n / 100) / 1000) * 1000));
    box.innerHTML = out.join('<br>'); box.hidden = false;
  }
  function showSend(url) {
    MAIL.url = url || MAIL.url; $('ps-send').hidden = false; drawMail();
  }
  function start(u) {
    if (!u) { location.href = A.loginUrl(); return; }
    if (!id) { $('ps-load').textContent = 'Rapport introuvable.'; return; }
    call({ action: 'apercu_dossier', id: id }).then(function (r) {
      $('ps-load').hidden = true; $('ps-app').hidden = false;
      if (r.view) { $('ps-frame').src = r.view; $('ps-open').href = r.view; }
      var P = r.perso || {}, f = $('ps-form');
      A.client.from('dossiers').select('commune,section,numero,agent,download_slug').eq('id', id).maybeSingle().then(function (q) { var d = q.data || {}; MAIL.slug = d.download_slug || ''; drawCk(); if (d.download_slug && !r.client) $('ps-open').href = '/r/' + d.download_slug; MAIL.ref = [d.commune, d.section, d.numero].filter(Boolean).join(' '); MAIL.agent = d.agent || ''; drawMail(); });
      ['ps-to', 'ps-obj', 'ps-body'].forEach(function (k) { $(k).addEventListener('input', function () { $(k).dataset.edit = '1'; drawMail(); }); });
      ['civ', 'prenom', 'nom', 'email'].forEach(function (k) { f[k].addEventListener('input', drawMail); f[k].addEventListener('change', drawMail); });
      $('ps-mail').addEventListener('click', function () { var to = $('ps-to').value.trim(); A.client.rpc('dossier_envoi', { p_id: id, p_email: to }).then(function () { $('ps-smsg').textContent = 'Envoi enregistré le ' + new Date().toLocaleDateString('fr-FR') + (to ? ' pour ' + to : '') + '. Il apparaît dans votre back-office.'; }); });
      $('ps-copy').addEventListener('click', function () { var t = $('ps-body').value; var ok = function () { $('ps-copy').textContent = 'Message copié'; }; if (navigator.clipboard) navigator.clipboard.writeText(t).then(ok, function () { $('ps-body').select(); }); else $('ps-body').select(); });
      if (new URLSearchParams(location.search).get('neuf')) msg('Votre rapport est prêt. Choisissez les rubriques, ajoutez votre prix et vos photos, puis générez la version de votre client.', 'ok');
      var cl = P.client || {}, rc = P.reco || {};
      ['civ', 'prenom', 'nom', 'email', 'tel'].forEach(function (k) { if (cl[k]) f[k].value = cl[k]; });
      ['type', 'designation', 'bas', 'haut', 'conseille', 'commentaire', 'hono', 'hono_charge', 'nego', 'delai'].forEach(function (k) { if (rc[k]) f[k].value = rc[k]; });
      var fi = rc.fiche || {};
      ['shab', 'sterrain', 'pieces', 'chambres', 'annee', 'dpe', 'etat'].forEach(function (k) { if (fi[k]) f[k].value = fi[k]; });
      (fi.atouts || []).forEach(function (a) { var c = document.querySelector('#ps-at input[value="' + a.replace(/"/g, '') + '"]'); if (c) c.checked = true; });
      if (rc.alerte === false) f.alerte.checked = false;
      ['conseille', 'hono', 'hono_charge', 'nego'].forEach(function (k) { f[k].addEventListener('input', drawCalc); f[k].addEventListener('change', drawCalc); }); drawCalc();
      var exc = P.exclure || [], sans = P.sans || [];
      var html = (r.chapitres || Object.keys(LIB)).map(function (t) {
        var sub = t === 'Environnement et marché immobilier' ? '<label class="ps-ck"><input type="checkbox" data-sans="especes"' + (sans.indexOf('especes') >= 0 ? '' : ' checked') + '><span>Espèces protégées observées autour<small>Liste des espèces et coût des études écologiques</small><em class="ps-off"></em></span></label><div class="ps-pv" data-pv="especes"></div>' : '';
        return '<label class="ps-ck"><input type="checkbox" data-ch="' + t.replace(/"/g, '&quot;') + '"' + (exc.indexOf(t) >= 0 ? '' : ' checked') + '><span>' + t + '<small>' + (LIB[t] || '') + '</small><em class="ps-off"></em></span></label><div class="ps-pv" data-pv="' + t.replace(/"/g, '&quot;') + '"></div>' + sub;
      }).join('');
      $('ps-ch').innerHTML = html + '<p style="color:var(--muet);font-size:13px;margin:10px 0 0">La synthèse, l\'avertissement et les sources restent toujours présents. Une rubrique absente de ce terrain n\'apparaît pas.</p><p class="ps-sum" id="ps-off-sum"></p>';
      $('ps-ch').addEventListener('change', drawCk); drawCk();
      (P.photos || []).forEach(function (path) { A.client.storage.from('perso').createSignedUrl(path, 3600).then(function (s) { if (s.data) { photos.push({ path: path, url: s.data.signedUrl }); drawPhotos(); } }); });
      if (r.client) { $('ps-frame').src = r.client.view; $('ps-open').href = r.client.court ? r.client.court + '?a=1' : r.client.view; $('ps-dl').href = r.client.url; $('ps-dl').hidden = false; showSend(r.client.court || r.client.url); $('ps-pt').textContent = 'Dernière version client'; $('ps-ps').textContent = 'Modifiez les réglages puis générez à nouveau si besoin.'; }
      if (!r.pret) msg('Ce rapport a été généré avant la mise en place de la version client. Générez un nouveau rapport sur cette parcelle pour pouvoir le personnaliser.', 'err');
    }).catch(function () { $('ps-load').textContent = 'Ce rapport n\'est pas accessible depuis votre compte.'; });
    $('ps-files').addEventListener('change', function (e) {
      var files = Array.prototype.slice.call(e.target.files || []).slice(0, 8 - photos.length); e.target.value = '';
      if (!files.length) return;
      msg('Envoi des photos…');
      Promise.all(files.map(function (file, i) {
        return shrink(file).then(function (b) {
          var path = u.id + '/' + id + '/' + Date.now() + '-' + i + '.jpg';
          return A.client.storage.from('perso').upload(path, b, { contentType: 'image/jpeg' }).then(function (r) { if (r.error) throw r.error; photos.push({ path: path, url: URL.createObjectURL(b) }); });
        });
      })).then(function () { drawPhotos(); msg(''); }).catch(function () { drawPhotos(); msg('Une photo n\'a pas pu être envoyée. Réessayez avec une photo au format JPEG ou PNG.', 'err'); });
    });
    $('ps-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var f = e.target, bt = $('ps-go');
      var body = { action: 'personnaliser', id: id,
        client: { civ: f.civ.value, prenom: f.prenom.value.trim(), nom: f.nom.value.trim(), email: f.email.value.trim(), tel: f.tel.value.trim() },
        reco: { type: f.type.value, designation: f.designation.value.trim(), alerte: f.alerte.checked, hono: f.hono.value.trim(), hono_charge: f.hono_charge.value, nego: f.nego.value.trim(), delai: f.delai.value,
          fiche: { shab: f.shab.value.trim(), sterrain: f.sterrain.value.trim(), pieces: f.pieces.value.trim(), chambres: f.chambres.value.trim(), annee: f.annee.value.trim(), dpe: f.dpe.value, etat: f.etat.value, atouts: Array.prototype.slice.call(document.querySelectorAll('#ps-at input:checked')).map(function (c) { return c.value; }) }, bas: f.bas.value.trim(), haut: f.haut.value.trim(), conseille: f.conseille.value.trim(), commentaire: f.commentaire.value.trim() },
        photos: photos.map(function (p) { return p.path; }),
        exclure: Array.prototype.slice.call(document.querySelectorAll('[data-ch]')).filter(function (c) { return !c.checked; }).map(function (c) { return c.getAttribute('data-ch'); }),
        sans: Array.prototype.slice.call(document.querySelectorAll('[data-sans]')).filter(function (c) { return !c.checked; }).map(function (c) { return c.getAttribute('data-sans'); })
      };
      bt.disabled = true; bt.textContent = 'Génération en cours… (1 à 2 minutes)'; msg('');
      function done(cl) {
        bt.disabled = false; bt.textContent = 'Générer à nouveau';
        $('ps-frame').src = cl.view; $('ps-open').href = cl.court ? cl.court + '?a=1' : cl.view; $('ps-dl').href = cl.url; $('ps-dl').hidden = false;
        $('ps-pt').textContent = 'Version client'; $('ps-ps').textContent = 'Voici le rapport que recevra votre client. Lien valable 7 jours.';
        showSend(cl.court || cl.url); msg('Version client prête. Téléchargez-la ou envoyez-la directement à votre client.', 'ok');
        if (window.innerWidth < 860) $('ps-pt').scrollIntoView({ behavior: 'smooth' });
      }
      function fail(er) {
        bt.disabled = false; bt.textContent = 'Générer la version client';
        msg(er && er.code === 'ancien' ? 'Ce rapport a été généré avant la mise en place de la version client. Générez un nouveau rapport sur cette parcelle.' : 'La génération n\'a pas abouti. Réessayez dans un instant.', 'err');
      }
      var t0 = Date.now();
      function poll() {
        call({ action: 'apercu_dossier', id: id }).then(function (r) {
          var st = r.perso && r.perso.status;
          if (st === 'pret' && r.client) return done(r.client);
          if (st === 'erreur' || Date.now() - t0 > 8 * 60000) return fail();
          setTimeout(poll, 6000);
        }).catch(function () { setTimeout(poll, 8000); });
      }
      call(body).then(function (r) { if (r && r.pending) { msg('Génération en cours, cela prend 2 à 4 minutes. Vous pouvez rester sur cette page.'); setTimeout(poll, 20000); } else poll(); }).catch(fail);
    });
  }
  function boot() { if (!window.TUAuth || !TUAuth.ready) { setTimeout(boot, 120); return; } A = window.TUAuth; A.user().then(start); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
