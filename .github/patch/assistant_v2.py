# Assistant : conseil de formule calculé (prix exacts pour n'importe quel nombre de rapports) et connaissances élargies
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "- Au-delà de 100 rapports ou pour un réseau : offre personnalisée sur devis (formulaire sur la page Tarifs) ou démonstration en visio."
assert s.count(a) == 1
b = a + """
- Tu es un conseiller commercial : quand on te demande un prix, donne toujours un chiffre et une recommandation claire (la formule que tu conseilles, puis au plus une alternative). Si un « CONSEIL CALCULÉ » figure en fin de ces instructions, reprends exactement ses montants : ils sont exacts. N'invente jamais d'autre montant.
- Particulier ou professionnel : les lots de 2 et 3 sont pensés pour les particuliers ; les crédits et l'abonnement pour les professionnels (logo sur le rapport). Un particulier peut aussi acheter des crédits."""
s = s.replace(a, b)
a2 = "AUTRES RÉPONSES UTILES"
assert s.count(a2) == 1
s = s.replace(a2, a2 + """
- Trouver sa parcelle sans connaître son numéro : indiquer seulement la commune (ou l'adresse) dans la recherche, puis zoomer sur le plan IGN (villes, villages, routes, cours d'eau) ou la photo aérienne et cliquer sur son terrain ; la référence cadastrale s'affiche. On peut aussi la lire sur l'acte de propriété, l'avis de taxe foncière ou sur cadastre.gouv.fr.
- Plusieurs parcelles contiguës : un rapport par parcelle ; le lot de 2 ou 3 ou les crédits réduisent le prix.
- Commune dont le PLU n'est pas publié en ligne : le rapport l'indique avec le statut officiel du document et renvoie vers la mairie pour le plan.
- Remboursement : pas de formule « satisfait ou remboursé » ; en cas de problème sur un rapport, écrire à contact@terrenurbanisme.com.""")
a3 = "  const q = msgs[msgs.length - 1].content; let reply = '', err = null;"
assert s.count(a3) == 1
b3 = a3 + """
  let sysTxt = ASSISTANT_SYS;
  try {
    const users = msgs.filter(m => m.role === 'user').map(m => m.content).reverse();
    let nv = 0;
    for (const t of users.slice(0, 3)) { const m = t.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').match(/(\\d{1,4})\\s?(rapports?|credits?|parcelles?|terrains?|dossiers?|biens?|analyses?|lots?)/); if (m) { nv = +m[1]; break; } }
    if (nv > 0) sysTxt += '\\n\\nCONSEIL CALCULÉ (montants exacts) : ' + conseilVolumeSrv(nv);
  } catch (e) {}"""
s = s.replace(a3, b3)
s = s.replace("system: [{ type: 'text', text: ASSISTANT_SYS, cache_control: { type: 'ephemeral' } }], messages: msgs", "system: [{ type: 'text', text: sysTxt, cache_control: { type: 'ephemeral' } }], messages: msgs")
assert "text: sysTxt" in s
fn = r"""
// Conseil de formule pour n rapports (mêmes prix que la page Tarifs)
function conseilVolumeSrv(n) {
  const PK = [['unit', 1, 29.9, 'rapport à l\'unité'], ['pack2', 2, 49.8, 'lot de 2'], ['pack3', 3, 59.7, 'lot de 3'], ['pro10', 10, 149, '10 crédits'], ['pro30', 30, 357, '30 crédits'], ['pro100', 100, 790, '100 crédits']];
  const eu = v => { const r = Math.round(v * 100) / 100, e = Math.floor(r), c = Math.round((r - e) * 100); return String(e).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + (c ? ',' + String(c).padStart(2, '0') : '') + ' €'; };
  if (n === 1) return '1 rapport : 29,90 €.';
  if (n === 2) return '2 rapports : lot de 2 à 49,80 €, soit 24,90 € le rapport.';
  if (n === 3) return '3 rapports : lot de 3 à 59,70 €, soit 19,90 € le rapport.';
  if (n > 100) return n + ' rapports : offre personnalisée sur devis (/tarifs.html#offre), réponse sous 24 heures ouvrées ; à titre indicatif, 100 crédits à 790 € (7,90 € le rapport).';
  const M = n + 100, best = [0], how = [[]];
  for (let q = 1; q <= M; q++) { best[q] = Infinity; for (const k of PK) { const r = Math.max(0, q - k[1]); if (best[r] + k[2] < best[q]) { best[q] = best[r] + k[2]; how[q] = how[r].concat([k]); } } }
  const L = how[n], P = best[n], Q = L.reduce((a, k) => a + k[1], 0);
  const c = {}, o = []; L.forEach(k => { if (!c[k[3]]) o.push(k[3]); c[k[3]] = (c[k[3]] || 0) + 1; });
  const desc = o.map(x => (c[x] > 1 ? c[x] + ' × ' : '') + x).join(' + ');
  let t = n + ' rapports : au plus juste ' + desc + ' = ' + eu(P) + (Q > n ? ' pour ' + Q + ' rapports' : '') + ' (' + eu(P / Q) + ' le rapport).';
  const up = PK.find(k => k[1] >= 10 && k[1] >= n);
  if (up && up[3] !== desc) t += ' Formule conseillée si son prix est proche ou si d\'autres terrains sont prévus : ' + up[3] + ' à ' + eu(up[2]) + ' (' + eu(up[2] / up[1]) + ' le rapport, sans limite de durée).';
  const ab = n <= 10 ? [10, 129] : n <= 30 ? [30, 297] : null;
  t += ab ? ' Besoin mensuel : abonnement ' + ab[0] + ' rapports par mois à ' + eu(ab[1]) + ' (' + eu(ab[1] / ab[0]) + ' le rapport), sans engagement.' : ' Besoin mensuel au-delà de 30 rapports : offre personnalisée.';
  return t;
}
"""
s = s.rstrip('\n') + '\n' + fn
open(p, 'w', encoding='utf-8').write(s); print('patch assistant_v2 appliqué')
