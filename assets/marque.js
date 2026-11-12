/* Mon espace : logo et coordonnées affichés sur les rapports des abonnés (co-marquage, rapport établi par TerrenUrbanisme) */
(function(){
  var box = document.getElementById('esp-marque'); if (!box) return;
  var A = window.TUAuth; if (!A || !A.ready || !A.client) return;
  var sb = A.client, $ = function(id){ return document.getElementById(id); };
  var ACTIVE = ['active', 'trialing', 'past_due'];
  // Retire les marges vides (transparentes ou blanches) autour du logo, pour qu'il apparaisse en grand sur le rapport
  function rogner(f){
    return new Promise(function(res){
      var img = new Image(), url = URL.createObjectURL(f);
      img.onload = function(){
        try {
          var w = img.naturalWidth, h = img.naturalHeight, c = document.createElement('canvas'); c.width = w; c.height = h;
          var x = c.getContext('2d'); x.drawImage(img, 0, 0); var d = x.getImageData(0, 0, w, h).data;
          var x0 = w, y0 = h, x1 = -1, y1 = -1;
          for (var j = 0; j < h; j++) for (var i = 0; i < w; i++) { var k = (j * w + i) * 4; if (d[k + 3] > 16 && (d[k] < 245 || d[k + 1] < 245 || d[k + 2] < 245)) { if (i < x0) x0 = i; if (i > x1) x1 = i; if (j < y0) y0 = j; if (j > y1) y1 = j; } }
          if (x1 < 0 || (x1 - x0 + 1) * (y1 - y0 + 1) > w * h * 0.9) { res(f); return; }
          var m = Math.round(Math.max(x1 - x0, y1 - y0) * 0.04), cw = x1 - x0 + 1 + 2 * m, chh = y1 - y0 + 1 + 2 * m, s = Math.min(1, 1200 / Math.max(cw, chh));
          var o = document.createElement('canvas'); o.width = Math.round(cw * s); o.height = Math.round(chh * s);
          o.getContext('2d').drawImage(c, x0 - m, y0 - m, cw, chh, 0, 0, o.width, o.height);
          o.toBlob(function(b){ res(b || f); }, 'image/png');
        } catch (e) { res(f); }
      };
      img.onerror = function(){ res(f); };
      img.src = url;
    });
  }
  A.user().then(function(u){
    if (!u) return;
    box.hidden = false;
    var msg = $('mq-msg'), prev = $('mq-prev'), file = $('mq-file'), path = null;
    sb.from('comptes').select('statut_abonnement, formule').eq('user_id', u.id).maybeSingle().then(function(r){
      var abo = (u.id === 'ca45b46d-24e0-4b79-8067-217f6b84a6ed') || (r.data && ACTIVE.indexOf(r.data.statut_abonnement || '') >= 0 && !/^essentiel/.test(r.data.formule || ''));
      $('mq-note').innerHTML = abo ? 'Votre logo et vos coordonnées figurent sur la page de garde et en tête de chaque page de vos prochains rapports. Le rapport reste établi par TerrenUrbanisme.'
        : 'Réservé aux abonnements Agence et Réseau : enregistrez votre logo dès maintenant, il apparaîtra sur vos rapports dès votre abonnement. <a href="/tarifs.html">Voir les abonnements</a>';
    });
    sb.from('marques').select('*').eq('user_id', u.id).maybeSingle().then(function(r){
      var m = r.data || {};
      ['nom', 'telephone', 'email', 'site'].forEach(function(k){ $('mq-' + k).value = m[k] || ''; });
      path = m.logo_path || null;
      if (path) sb.storage.from('logos').download(path).then(function(d){ if (d.data) { prev.src = URL.createObjectURL(d.data); prev.hidden = false; } });
    });
    file.addEventListener('change', function(){
      var f = file.files[0]; msg.textContent = '';
      if (!f) return;
      if (!/^image\/(png|jpeg)$/.test(f.type)) { msg.textContent = 'Format accepté : PNG ou JPG.'; file.value = ''; return; }
      if (f.size > 2 * 1024 * 1024) { msg.textContent = 'Le fichier dépasse 2 Mo.'; file.value = ''; return; }
      prev.src = URL.createObjectURL(f); prev.hidden = false;
    });
    $('mq-form').addEventListener('submit', function(e){
      e.preventDefault(); msg.textContent = 'Enregistrement…';
      var f = file.files[0], up = Promise.resolve(path);
      if (f) {
        up = rogner(f).then(function(blob){
          var png = blob.type === 'image/png', p = u.id + '/logo-' + Date.now() + (png ? '.png' : '.jpg');
          return sb.storage.from('logos').upload(p, blob, { contentType: blob.type, upsert: true }).then(function(r){ if (r.error) throw r.error; return p; });
        });
      }
      up.then(function(lp){
        var row = { user_id: u.id, logo_path: lp, updated_at: new Date().toISOString() };
        ['nom', 'telephone', 'email', 'site'].forEach(function(k){ var v = $('mq-' + k).value.trim(); row[k] = v || null; });
        return sb.from('marques').upsert(row).then(function(r){ if (r.error) throw r.error; path = lp; msg.textContent = 'Enregistré. Vos prochains rapports porteront votre logo.'; file.value = ''; });
      }).catch(function(){ msg.textContent = 'L\'enregistrement n\'a pas abouti. Vérifiez le fichier et réessayez.'; });
    });
  });
})();
