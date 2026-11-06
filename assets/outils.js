/* TerrenUrbanisme — outils gratuits : déclaration préalable ou permis, taxe d'aménagement */
(function(){
  'use strict';
  var $ = function(id){ return document.getElementById(id); };
  var num = function(id){ var v = parseFloat(String(($(id) || {}).value || '').replace(',', '.')); return isFinite(v) && v > 0 ? v : 0; };
  var eur = function(n){ return Math.round(n).toLocaleString('fr-FR') + ' €'; };
  var CTA = '<a class="btn" href="/#recherche">Vérifier la zone de mon terrain</a>';

  /* ---------- Simulateur : déclaration préalable ou permis ---------- */
  var sim = $('sim-dp');
  if (sim){
    var type = $('sd-type'), rows = sim.querySelectorAll('[data-for]'), out = $('sd-out');
    var show = function(){ var t = type.value; rows.forEach(function(r){ r.hidden = r.getAttribute('data-for').split(' ').indexOf(t) < 0; }); };
    type.addEventListener('change', function(){ show(); out.hidden = true; });
    show();
    sim.addEventListener('submit', function(e){
      e.preventDefault();
      var t = type.value, s = num('sd-surf'), ex = num('sd-exist'), zu = $('sd-zu').value, prot = $('sd-prot').value === 'oui', cov = $('sd-cov').value === 'haute', works = $('sd-works').value === 'oui', voies = $('sd-voies').value === 'oui';
      var r = { key: '', label: '', why: [], delai: '', cerfa: '', archi: false, warn: [] };
      if (prot) r.warn.push('Votre terrain est en secteur protégé : l\'avis de l\'architecte des Bâtiments de France est requis et allonge le délai d\'un mois.');
      if (t === 'construction' || t === 'annexe'){
        if (!s){ out.hidden = false; out.innerHTML = '<p class="err">Indiquez la surface créée (surface de plancher ou emprise au sol, la plus grande des deux).</p>'; return; }
        if (s <= 5 && !prot){ r.key = 'none'; r.label = 'Aucune autorisation en principe'; r.why.push('Moins de 5 m² créés, hors secteur protégé.'); }
        else if (s <= 20){ r.key = 'dp'; r.label = 'Déclaration préalable'; r.why.push('Entre 5 et 20 m² créés' + (prot && s <= 5 ? ', en secteur protégé' : '') + '.'); }
        else { r.key = 'pc'; r.label = 'Permis de construire'; r.why.push('Plus de 20 m² créés.'); }
        if (t === 'construction' && s > 150){ r.archi = true; }
      } else if (t === 'extension'){
        if (!s){ out.hidden = false; out.innerHTML = '<p class="err">Indiquez la surface de l\'extension.</p>'; return; }
        var total = ex + s, seuil = zu === 'oui' ? 40 : 20;
        if (s <= 5 && !prot){ r.key = 'none'; r.label = 'Aucune autorisation en principe'; r.why.push('Moins de 5 m² créés, hors secteur protégé.'); }
        else if (s <= 20){ r.key = 'dp'; r.label = 'Déclaration préalable'; r.why.push('Extension de 20 m² ou moins.'); }
        else if (s <= seuil && total <= 150){ r.key = 'dp'; r.label = 'Déclaration préalable'; r.why.push('Extension de 40 m² ou moins en zone urbaine d\'un PLU, et surface totale après travaux de 150 m² ou moins.'); }
        else { r.key = 'pc'; r.label = 'Permis de construire'; r.why.push(s > seuil ? 'Extension de plus de ' + seuil + ' m²' + (zu === 'oui' ? ' en zone urbaine' : ' hors zone urbaine d\'un PLU') + '.' : 'La surface totale de la maison dépasse 150 m² après travaux.'); }
        if (zu === 'nsp') r.warn.push('Le seuil de 40 m² ne vaut qu\'en zone urbaine (U) d\'un PLU. Ailleurs, il est de 20 m². Vérifiez la zone de votre terrain.');
        if (r.key === 'pc' && total > 150) r.archi = true;
      } else if (t === 'piscine'){
        if (!s){ out.hidden = false; out.innerHTML = '<p class="err">Indiquez la surface du bassin.</p>'; return; }
        if (s <= 10 && !prot){ r.key = 'none'; r.label = 'Aucune autorisation en principe'; r.why.push('Bassin de 10 m² ou moins, hors secteur protégé.'); }
        else if (s <= 100 && !cov){ r.key = 'dp'; r.label = 'Déclaration préalable'; r.why.push('Bassin de 100 m² ou moins, non couvert ou avec une couverture de moins de 1,80 m.'); }
        else { r.key = 'pc'; r.label = 'Permis de construire'; r.why.push(cov ? 'Couverture de 1,80 m ou plus.' : 'Bassin de plus de 100 m².'); }
      } else if (t === 'facade'){ r.key = 'dp'; r.label = 'Déclaration préalable'; r.why.push('Modification de l\'aspect extérieur : façade, ouvertures, toiture, couleur.'); }
      else if (t === 'cloture'){ r.key = 'dp'; r.label = 'Déclaration préalable, si la commune l\'exige'; r.why.push('Une clôture n\'est soumise à déclaration que si la commune l\'a décidé, ou en secteur protégé. Renseignez-vous en mairie.'); }
      else if (t === 'destination'){
        if (works){ r.key = 'pc'; r.label = 'Permis de construire'; r.why.push('Changement de destination avec modification des structures porteuses ou de la façade.'); }
        else { r.key = 'dp'; r.label = 'Déclaration préalable'; r.why.push('Changement de destination sans modification des structures porteuses ni de la façade.'); }
      } else if (t === 'division'){
        if (voies || prot){ r.key = 'pa'; r.label = 'Permis d\'aménager'; r.why.push(voies ? 'Création de voies, d\'espaces ou d\'équipements communs.' : 'Terrain en secteur protégé.'); }
        else { r.key = 'dp'; r.label = 'Déclaration préalable'; r.why.push('Division en vue de bâtir, sans voie ni espace commun.'); }
      }
      var maison = (t === 'construction' || t === 'annexe' || t === 'extension' || t === 'piscine' || t === 'facade' || t === 'cloture');
      if (r.key === 'dp'){ r.delai = (prot ? '2 mois' : '1 mois'); r.cerfa = t === 'division' ? 'Cerfa n° 13702 (déclaration préalable, lotissements et divisions)' : maison ? 'Cerfa n° 13703 (déclaration préalable, maison individuelle)' : 'Cerfa n° 13404 (déclaration préalable)'; }
      if (r.key === 'pc'){ r.delai = (maison ? '2 mois' : '3 mois') + (prot ? ' + 1 mois' : ''); r.cerfa = maison ? 'Cerfa n° 13406 (permis de construire, maison individuelle)' : 'Cerfa n° 13409 (permis de construire)'; }
      if (r.key === 'pa'){ r.delai = '3 mois' + (prot ? ' + 1 mois' : ''); r.cerfa = 'Cerfa n° 13409 (permis d\'aménager)'; }
      var col = { none:'ok', dp:'cond', pc:'non', pa:'non' }[r.key];
      out.hidden = false;
      out.innerHTML = '<div class="tool-res ' + col + '"><span class="tool-k">Autorisation à demander</span><b>' + r.label + '</b>' +
        '<ul>' + r.why.map(function(w){ return '<li>' + w + '</li>'; }).join('') + '</ul>' +
        (r.delai ? '<p><strong>Délai d\'instruction :</strong> ' + r.delai + ' à compter du dossier complet.</p>' : '') +
        (r.cerfa ? '<p><strong>Formulaire :</strong> ' + r.cerfa + ', sur service-public.fr.</p>' : '') +
        (r.archi ? '<p><strong>Architecte obligatoire :</strong> la surface de plancher totale dépasse 150 m².</p>' : '') +
        r.warn.map(function(w){ return '<p class="tool-warn">' + w + '</p>'; }).join('') +
        '<p class="fine">Résultat indicatif selon le Code de l\'urbanisme. Le PLU de votre commune peut fixer des règles plus strictes (hauteur, emprise, aspect) qui s\'appliquent dans tous les cas.</p>' +
        '<div class="tool-cta"><span>Avant de déposer votre dossier, vérifiez ce que le PLU autorise sur votre parcelle : zone, hauteur, emprise au sol, reculs.</span>' + CTA + '</div></div>';
      out.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  /* ---------- Calculateur : taxe d'aménagement (valeurs 2026) ---------- */
  var tx = $('calc-ta');
  if (tx){
    var V = { horsIdf: 892, idf: 1011, piscine: 251, place: 2928 };
    var idfSel = $('ta-idf'), regRow = $('ta-reg-row');
    var sync = function(){ regRow.hidden = idfSel.value !== 'oui'; };
    idfSel.addEventListener('change', sync); sync();
    // Commune : les taux votés (DGFiP) sont chargés depuis nos données communales
    var IDF = ['75','77','78','91','92','93','94','95'], com = $('ta-com'), lst = $('ta-com-list'), inf = $('ta-com-info'), tmr, choix = null;
    var fr = function(n){ return String(Math.round(n * 100) / 100).replace('.', ','); };
    var pick = function(c){
      choix = c; com.value = c.nom + ' (' + c.code + ')'; lst.hidden = true; lst.innerHTML = '';
      var dep = c.code.slice(0, 2) === '97' ? c.code.slice(0, 3) : c.code.slice(0, 2);
      idfSel.value = IDF.indexOf(dep) >= 0 ? 'oui' : 'non'; sync();
      inf.textContent = 'Recherche des taux votés…';
      fetch('/data/communes/' + dep + '.json').then(function(r){ return r.json(); }).then(function(all){
        var t = (all[c.code] || {}).ta || {}, d = all._dep || {}, msg = [];
        if (t.c != null){ $('ta-tc').value = fr(t.c); msg.push('taux communal ' + fr(t.c) + ' %'); } else msg.push('aucun taux communal publié : vérifiez en mairie');
        if (d.td != null){ $('ta-td').value = fr(d.td); msg.push('taux départemental ' + fr(d.td) + ' %'); }
        if (d.tr != null && IDF.indexOf(dep) >= 0){ $('ta-tr').value = fr(d.tr); }
        if (t.s && Object.keys(t.s).length) msg.push('certains secteurs ont un taux différent : le rapport de votre parcelle applique le bon');
        inf.textContent = 'Taux appliqués : ' + msg.join(' · ') + '.';
      }).catch(function(){ inf.textContent = 'Taux de la commune indisponibles : saisissez-les ci-dessous.'; });
    };
    if (com){
      com.addEventListener('input', function(){
        clearTimeout(tmr); choix = null; var q = com.value.trim(); if (q.length < 2){ lst.hidden = true; return; }
        tmr = setTimeout(function(){
          var u = /^\d[\dAB]\d{3}$/i.test(q) ? 'https://geo.api.gouv.fr/communes?code=' + q.toUpperCase() : 'https://geo.api.gouv.fr/communes?nom=' + encodeURIComponent(q) + '&boost=population&limit=6';
          fetch(u + (u.indexOf('?') > 0 ? '&' : '?') + 'fields=nom,code,codesPostaux').then(function(r){ return r.json(); }).then(function(L){
            lst.innerHTML = ''; (L || []).slice(0, 6).forEach(function(c){ var b = document.createElement('button'); b.type = 'button'; b.className = 'ta-opt'; b.textContent = c.nom + ' (' + ((c.codesPostaux || [])[0] || c.code) + ')'; b.addEventListener('click', function(){ pick(c); }); lst.appendChild(b); });
            lst.hidden = !lst.children.length;
          }).catch(function(){});
        }, 250);
      });
    }
    tx.addEventListener('submit', function(e){
      e.preventDefault();
      var s = num('ta-surf'), rp = $('ta-rp').value === 'oui', idf = idfSel.value === 'oui', pis = num('ta-pis'), pl = Math.floor(num('ta-places'));
      var tc = num('ta-tc') / 100, td = num('ta-td') / 100, tr = idf ? num('ta-tr') / 100 : 0, taux = tc + td + tr;
      var out = $('ta-out');
      if (!s && !pis && !pl){ out.hidden = false; out.innerHTML = '<p class="err">Indiquez au moins une surface, une piscine ou des places de stationnement.</p>'; return; }
      if (!taux){ out.hidden = false; out.innerHTML = '<p class="err">Indiquez les taux de votre commune et de votre département.</p>'; return; }
      var v = idf ? V.idf : V.horsIdf;
      var abat = rp ? Math.min(s, 100) : 0, plein = s - abat;
      var baseSurf = abat * v * 0.5 + plein * v, basePis = pis * V.piscine, basePl = pl * V.place;
      var base = baseSurf + basePis + basePl, total = base * taux;
      var part = function(t){ return eur(base * t); };
      out.hidden = false;
      out.innerHTML = '<div class="tool-res cond"><span class="tool-k">Taxe d\'aménagement estimée</span><b class="tool-big">' + eur(total) + '</b>' +
        '<table class="tool-tab"><tbody>' +
        (s ? '<tr><td>Surface taxable : ' + s.toLocaleString('fr-FR') + ' m² × ' + v.toLocaleString('fr-FR') + ' €' + (rp ? ' (abattement de 50 % sur les ' + abat + ' premiers m²)' : '') + '</td><td>' + eur(baseSurf) + '</td></tr>' : '') +
        (pis ? '<tr><td>Piscine : ' + pis.toLocaleString('fr-FR') + ' m² × ' + V.piscine + ' €</td><td>' + eur(basePis) + '</td></tr>' : '') +
        (pl ? '<tr><td>Stationnement extérieur : ' + pl + ' place' + (pl > 1 ? 's' : '') + ' × ' + V.place.toLocaleString('fr-FR') + ' €</td><td>' + eur(basePl) + '</td></tr>' : '') +
        '<tr class="tot"><td>Assiette totale</td><td>' + eur(base) + '</td></tr>' +
        '<tr><td>Part communale (' + (tc * 100).toLocaleString('fr-FR') + ' %)</td><td>' + part(tc) + '</td></tr>' +
        '<tr><td>Part départementale (' + (td * 100).toLocaleString('fr-FR') + ' %)</td><td>' + part(td) + '</td></tr>' +
        (idf ? '<tr><td>Part régionale (' + (tr * 100).toLocaleString('fr-FR') + ' %)</td><td>' + part(tr) + '</td></tr>' : '') +
        '<tr class="tot"><td>Total</td><td>' + eur(total) + '</td></tr></tbody></table>' +
        '<p><strong>Quand payer :</strong> la taxe se déclare sur impots.gouv.fr dans les 90 jours suivant l\'achèvement des travaux. Au-delà de 1 500 €, elle est payée en deux fois.</p>' +
        '<p class="fine">Estimation indicative avec les valeurs forfaitaires 2026 (' + V.horsIdf + ' €/m² hors Île-de-France, ' + V.idf.toLocaleString('fr-FR') + ' €/m² en Île-de-France, ' + V.piscine + ' €/m² de piscine, ' + V.place.toLocaleString('fr-FR') + ' € par place). La redevance d\'archéologie préventive peut s\'ajouter, et votre commune peut prévoir des exonérations (abris de jardin, résidences principales en prêt à taux zéro…). Le montant définitif figure sur l\'avis des impôts.</p>' +
        '<div class="tool-cta lead"><span><strong>Et sur votre terrain ?</strong> Le rapport TerrenUrbanisme calcule la taxe exacte de votre parcelle, avec le taux de son secteur et la surface que le PLU vous autorise réellement à construire, ainsi que le raccordement à l\'électricité et à l\'eau, les risques et la valeur du terrain.</span><a class="btn" href="/#recherche">Vérifier mon terrain' + (choix ? ' à ' + choix.nom : '') + '</a></div></div>';
      out.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
})();
