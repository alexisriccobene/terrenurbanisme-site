# Page de garde : le nom du partenaire précédé de sa qualité (« La Ville de… », « L'agence… », « La conciergerie… »)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + label)
    s = s.replace(old, new)
rep("return { bytes, png, nom: mq.nom || '', telephone: mq.telephone || '',",
    "return { bytes, png, nom: mq.nom || '', type: mq.type || '', telephone: mq.telephone || '',", 'retour marque')
rep("    if (MQ.nom) { const n = clean(MQ.nom).slice(0, 60); cover.drawText(n, { x: ctrX(n, 16, B), y: ty, size: 16, font: B, color: C.ink }); ty -= 20; }",
r"""    if (MQ.nom) {
      const nom = String(MQ.nom).trim().replace(/\s+/g, ' ');
      const low = nom.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
      let ty0 = String(MQ.type || '');
      if (!ty0) ty0 = /^(ville|mairie|commune|communaute)\b/.test(low) ? 'ville' : /conciergerie/.test(low) ? 'conciergerie' : /(notaire|notarial|^etude)/.test(low) ? 'notaire' : /geometre/.test(low) ? 'geometre' : /architect/.test(low) ? 'architecte' : /(agence|immobili)/.test(low) ? 'agence' : /^cabinet\b/.test(low) ? 'cabinet' : /(banque|credit)/.test(low) ? 'banque' : '';
      const QUAL = { ville: [/^(ville|mairie|commune|communaute)\b/, 'La ', 'La ville de '], agence: [/^agence\b/, "L'", "L'agence "], conciergerie: [/^conciergerie\b/, 'La ', 'La conciergerie '],
        notaire: [/^(etude|office)\b/, "L'", "L'étude "], geometre: [/^cabinet\b/, 'Le ', 'Le cabinet '], architecte: [/^(cabinet|atelier|agence)\b/, '', "L'agence d'architecture "],
        cabinet: [/^cabinet\b/, 'Le ', 'Le cabinet '], promoteur: [/^(societe|groupe)\b/, 'La ', 'La société '], constructeur: [/^(societe|groupe)\b/, 'La ', 'La société '],
        banque: [/^(banque|credit|caisse)\b/, 'La ', 'La banque '], courtier: [/^cabinet\b/, 'Le ', 'Le cabinet '], collectivite: [/^(communaute|departement|collectivite|region|syndicat)\b/, 'La ', ''] };
      const q = QUAL[ty0];
      let n = nom;
      if (q && !/^(le|la|les)\s|^l['’]/i.test(nom)) {
        if (q[0].test(low)) n = ty0 === 'architecte' ? ((/^(atelier|agence)/.test(low) ? "L'" : 'Le ') + nom) : q[1] + nom;
        else if (q[2]) n = q[2] + nom;
      }
      n = clean(n.charAt(0).toUpperCase() + n.slice(1));
      let fs = 16; while (fs > 11 && tw(n, B, fs) > CW) fs -= 0.5;
      wrap(n, B, fs, CW).slice(0, 2).forEach(l => { cover.drawText(l, { x: ctrX(l, fs, B), y: ty, size: fs, font: B, color: C.ink }); ty -= fs + 4; });
    }""", 'nom couverture')
open(p, 'w', encoding='utf-8').write(s); print('patch marque_type appliqué')
