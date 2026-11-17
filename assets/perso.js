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
  function start(u) {
    if (!u) { location.href = A.loginUrl(); return; }
    if (!id) { $('ps-load').textContent = 'Rapport introuvable.'; return; }
    call({ action: 'apercu_dossier', id: id }).then(function (r) {
      $('ps-load').hidden = true; $('ps-app').hidden = false;
      if (r.view) { $('ps-frame').src = r.view; $('ps-open').href = r.view; }
      var P = r.perso || {}, f = $('ps-form');
      var cl = P.client || {}, rc = P.reco || {};
      ['civ', 'prenom', 'nom', 'email', 'tel'].forEach(function (k) { if (cl[k]) f[k].value = cl[k]; });
      ['bas', 'haut', 'conseille', 'commentaire'].forEach(function (k) { if (rc[k]) f[k].value = rc[k]; });
      var exc = P.exclure || [], sans = P.sans || [];
      var html = (r.chapitres || Object.keys(LIB)).map(function (t) {
        var sub = t === 'Environnement et marché immobilier' ? '<label class="ps-ck" style="padding-left:30px"><input type="checkbox" data-sans="especes"' + (sans.indexOf('especes') >= 0 ? '' : ' checked') + '><span>Espèces protégées observées autour<small>Liste des espèces et coût des études écologiques</small></span></label>' : '';
        return '<label class="ps-ck"><input type="checkbox" data-ch="' + t.replace(/"/g, '&quot;') + '"' + (exc.indexOf(t) >= 0 ? '' : ' checked') + '><span>' + t + '<small>' + (LIB[t] || '') + '</small></span></label>' + sub;
      }).join('');
      $('ps-ch').innerHTML = html + '<p style="color:var(--muet);font-size:13px;margin:10px 0 0">La synthèse, l\'avertissement et les sources restent toujours présents. Une rubrique absente de ce terrain n\'apparaît pas.</p>';
      (P.photos || []).forEach(function (path) { A.client.storage.from('perso').createSignedUrl(path, 3600).then(function (s) { if (s.data) { photos.push({ path: path, url: s.data.signedUrl }); drawPhotos(); } }); });
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
        reco: { bas: f.bas.value.trim(), haut: f.haut.value.trim(), conseille: f.conseille.value.trim(), commentaire: f.commentaire.value.trim() },
        photos: photos.map(function (p) { return p.path; }),
        exclure: Array.prototype.slice.call(document.querySelectorAll('[data-ch]')).filter(function (c) { return !c.checked; }).map(function (c) { return c.getAttribute('data-ch'); }),
        sans: Array.prototype.slice.call(document.querySelectorAll('[data-sans]')).filter(function (c) { return !c.checked; }).map(function (c) { return c.getAttribute('data-sans'); })
      };
      bt.disabled = true; bt.textContent = 'Génération en cours… (1 à 2 minutes)'; msg('');
      call(body).then(function (r) {
        bt.disabled = false; bt.textContent = 'Générer à nouveau';
        $('ps-frame').src = r.view; $('ps-open').href = r.view; $('ps-dl').href = r.url; $('ps-dl').hidden = false;
        $('ps-pt').textContent = 'Version client'; $('ps-ps').textContent = 'Voici le rapport que recevra votre client. Lien valable 7 jours.';
        msg('Version client prête. Téléchargez-la pour l\'envoyer à votre client.', 'ok');
        if (window.innerWidth < 860) $('ps-pt').scrollIntoView({ behavior: 'smooth' });
      }).catch(function (er) {
        bt.disabled = false; bt.textContent = 'Générer la version client';
        msg(er && er.code === 'ancien' ? 'Ce rapport a été généré avant la mise en place de la version client. Générez un nouveau rapport sur cette parcelle.' : 'La génération n\'a pas abouti. Réessayez dans un instant.', 'err');
      });
    });
  }
  function boot() { if (!window.TUAuth || !TUAuth.ready) { setTimeout(boot, 120); return; } A = window.TUAuth; A.user().then(start); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
