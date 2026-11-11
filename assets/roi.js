/* Calculateur « Combien vaut votre temps ? » : temps et argent gagnés avec TerrenUrbanisme, par métier.
   S'insère dans tout élément <div data-roi="metier"></div>. */
(function () {
  var METIERS = {
    agence:        { l: 'Agent immobilier, mandataire', taux: 50,  n: 10, q: 'biens étudiés par mois' },
    notaire:       { l: 'Notaire, clerc',               taux: 120, n: 8,  q: 'dossiers par mois' },
    architecte:    { l: 'Architecte, maître d’œuvre', taux: 70, n: 6, q: 'projets étudiés par mois' },
    geometre:      { l: 'Géomètre-expert',              taux: 70,  n: 8,  q: 'dossiers par mois' },
    diagnostiqueur:{ l: 'Diagnostiqueur',               taux: 50,  n: 10, q: 'biens par mois' },
    avocat:        { l: 'Avocat, juriste',              taux: 150, n: 4,  q: 'dossiers par mois' },
    promoteur:     { l: 'Promoteur, marchand de biens', taux: 100, n: 20, q: 'terrains étudiés par mois' },
    particulier:   { l: 'Particulier',                  taux: 25,  n: 1,  q: 'terrain(s)' },
    mairie:        { l: 'Agent du service urbanisme',   taux: 30,  n: 40, q: 'demandes d’habitants par mois' }
  };
  // Ce que le rapport vérifie à votre place, et le temps passé à le faire site par site
  var ETAPES = [
    ['Retrouver la parcelle sur le cadastre et sa surface', 5],
    ['Identifier la zone sur le Géoportail de l’urbanisme', 10],
    ['Lire le règlement de la zone (hauteur, emprise, reculs…)', 30],
    ['Vérifier les servitudes et les périmètres protégés', 10],
    ['Consulter les risques sur Géorisques', 10],
    ['Vérifier Loi Littoral, Montagne et PADDUC', 10],
    ['Chercher les ventes de terrains du secteur (DVF)', 10],
    ['Repérer les permis délivrés à proximité', 5],
    ['Vérifier les réseaux : électricité, eau, assainissement, fibre', 10],
    ['Estimer la taxe d’aménagement', 5],
    ['Rédiger un compte rendu clair pour le client', 15]
  ];
  var MAN = ETAPES.reduce(function (a, e) { return a + e[1]; }, 0); // 120 min
  var TU = 3;
  function eur(v) { return Math.round(v).toLocaleString('fr-FR').replace(/ /g, ' ') + ' €'; }
  function h(v) { var x = Math.round(v * 10) / 10; return String(x).replace('.', ',') + ' h'; }
  var POP = [['Moins de 2\u00a0000 habitants', 79], ['2\u00a0000 à 10\u00a0000 habitants', 149], ['10\u00a0000 à 50\u00a0000 habitants', 249], ['50\u00a0000 à 200\u00a0000 habitants', 490], ['Plus de 200\u00a0000 habitants', 990]];
  function cout(m, n, pop) {
    if (m === 'mairie') return { p: POP[pop == null ? 2 : pop][1], lib: 'Offre communale' };
    if (n <= 3) return { p: n === 1 ? 19.9 : n === 2 ? 29.8 : 38.7, lib: n === 1 ? 'Rapport à l’unité' : 'Lot de ' + n + ' rapports' };
    if (n <= 15) return { p: 29, lib: 'Abonnement Solo' };
    if (n <= 50) return { p: 55, lib: 'Abonnement Agence' };
    if (n <= 150) return { p: 139, lib: 'Abonnement Réseau' };
    return { p: 139 * Math.ceil(n / 150), lib: Math.ceil(n / 150) + ' abonnements Réseau' };
  }
  function build(el) {
    var m0 = METIERS[el.getAttribute('data-roi')] ? el.getAttribute('data-roi') : 'agence';
    var opts = Object.keys(METIERS).filter(function (k) { return m0 === 'mairie' ? k === 'mairie' : k !== 'mairie'; })
      .map(function (k) { return '<option value="' + k + '"' + (k === m0 ? ' selected' : '') + '>' + METIERS[k].l + '</option>'; }).join('');
    el.className = 'roi';
    el.innerHTML =
      '<div class="roi-head"><div class="roi-eb">Les données sont gratuites. Votre temps ne l\u2019est pas.</div><h2>Combien vaut une heure de votre temps ?</h2>' +
      '<p class="lede">' + (m0 === 'mairie' ? 'Chaque question d\u2019habitant sur un terrain oblige un agent à consulter une dizaine de sources : PLU, servitudes, risques, réseaux. 1 à 2 heures par dossier. Le rapport TerrenUrbanisme y répond en 3 minutes, sans mobiliser le service.' : 'Toutes ces informations sont publiques, mais dispersées sur une dizaine de sites qu\u2019il faut consulter un par un. Pour une seule parcelle, cela prend 1 à 2 heures. Le rapport TerrenUrbanisme réunit tout en 3 minutes.') + '</p></div>' +
      '<div class="roi-grid"><div class="roi-in">' +
      (m0 === 'mairie' ? '<label><span>Taille de la commune</span><select data-k="pop">' + POP.map(function (p, i) { return '<option value="' + i + '"' + (i === 2 ? ' selected' : '') + '>' + p[0] + '</option>'; }).join('') + '</select></label>' : '<label><span>Votre métier</span><select data-k="m">' + opts + '</select></label>') +
      '<label><span>Valeur d’une heure de votre temps</span><span class="roi-v"><input type="number" min="10" max="500" step="5" data-k="taux"> €</span></label>' +
      '<label><span data-k="ql">Dossiers par mois</span><span class="roi-v"><input type="number" min="1" max="1000" step="1" data-k="n"></span></label>' +
      '<label><span>Temps d’une recherche faite à la main</span><span class="roi-v"><input type="number" min="15" max="300" step="5" data-k="man"> min</span></label>' +
      '</div><div class="roi-out">' +
      '<div class="roi-k"><span>Temps gagné chaque mois</span><b data-o="h"></b></div>' +
      '<div class="roi-k"><span>Valeur de ce temps</span><b data-o="v"></b></div>' +
      '<div class="roi-k"><span data-o="cl">Coût TerrenUrbanisme</span><b data-o="c"></b></div>' +
      '<div class="roi-k roi-net"><span>Gain net chaque mois</span><b data-o="g"></b></div>' +
      '<p class="roi-x" data-o="x"></p></div></div>' +
      '<details class="roi-det"><summary>Le détail des ' + ETAPES.length + ' vérifications faites à votre place</summary><table>' +
      ETAPES.map(function (e) { return '<tr><td>' + e[0] + '</td><td>' + e[1] + ' min</td></tr>'; }).join('') +
      '<tr class="roi-tot"><td>À la main, site par site</td><td>' + Math.floor(MAN / 60) + ' h' + (MAN % 60 ? ' ' + (MAN % 60) : '') + '</td></tr>' +
      '<tr class="roi-tot"><td>Avec TerrenUrbanisme</td><td>' + TU + ' min</td></tr></table>' +
      '<p class="muted">Temps indicatifs pour une parcelle, à adapter à votre pratique : modifiez les valeurs ci-dessus pour faire votre propre calcul.</p></details>';
    var q = function (k) { return el.querySelector('[data-k="' + k + '"]'); }, o = function (k) { return el.querySelector('[data-o="' + k + '"]'); };
    function preset(k) { var M = METIERS[k]; q('taux').value = M.taux; q('n').value = M.n; q('ql').textContent = M.q.charAt(0).toUpperCase() + M.q.slice(1); }
    function calc() {
      var k = q('m') ? q('m').value : m0, taux = Math.max(0, +q('taux').value || 0), n = Math.max(1, Math.round(+q('n').value || 1)), man = Math.max(TU, +q('man').value || 90);
      var hrs = n * (man - TU) / 60, val = hrs * taux, c = cout(k, n, q('pop') ? +q('pop').value : null), g = val - c.p;
      o('h').textContent = h(hrs); o('v').textContent = eur(val); o('cl').textContent = c.lib; o('c').textContent = eur(c.p); o('g').textContent = (g >= 0 ? '+' : '') + eur(g);
      o('x').textContent = c.p > 0 && val > c.p ? (m0 === 'mairie' ? 'Chaque euro investi en rend ' : 'Chaque euro investi vous en rapporte ') + String(Math.round(val / c.p * 10) / 10).replace('.', ',') + ' en temps gagné, soit ' + h(hrs * 12) + (m0 === 'mairie' ? ' par an rendues au service urbanisme.' : ' par an rendues à votre activité.') : '';
    }
    preset(m0); q('man').value = 90;
    el.addEventListener('input', function (e) { if (e.target.getAttribute('data-k') === 'm') preset(e.target.value); calc(); });
    el.addEventListener('change', function (e) { if (e.target.getAttribute('data-k') === 'm') { preset(e.target.value); calc(); } });
    calc();
  }
  function init() { Array.prototype.forEach.call(document.querySelectorAll('[data-roi]'), build); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
