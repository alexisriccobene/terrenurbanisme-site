# Synthèse du rapport : quand aucune hauteur chiffrée n'est retenue, reprendre ce que dit le règlement (non réglementée, plan des hauteurs…) au lieu de « Non précisée »
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "['Hauteur maximale', K.H ? String(K.H).replace('.', ',') + ' m' + (K.niv ? ', soit ' + K.niv + ' niveau' + (K.niv > 1 ? 'x' : '') + ' environ' : '') : 'Non précisée'],"
assert s.count(a) == 1
b = "['Hauteur maximale', K.H ? String(K.H).replace('.', ',') + ' m' + (K.niv ? ', soit ' + K.niv + ' niveau' + (K.niv > 1 ? 'x' : '') + ' environ' : '') : hauteurTexte(d)],"
s = s.replace(a, b)
f = r"""
// Hauteur sans valeur chiffrée : ce que dit la règle lue dans le règlement
function hauteurTexte(d) {
  let t = null;
  try {
    const seen = new Set();
    const find = o => {
      if (!o || typeof o !== 'object' || seen.has(o)) return null; seen.add(o);
      if (Array.isArray(o.regles)) { const r = o.regles.find(x => x && /hauteur/i.test(x.critere || '')); if (r && r.regle) return String(r.regle); }
      for (const v of Object.values(o)) { const x = find(v); if (x) return x; }
      return null;
    };
    t = find(d && d.reglement);
  } catch (e) { t = null; }
  if (!t) return 'Non précisée';
  if (/plan des hauteurs|plan de(s)? hauteur|document graphique|plan de zonage|indiqu\S* (sur|au) (le )?plan/i.test(t)) return 'Fixée sur le plan des hauteurs du PLU (voir la règle de la zone)';
  if (/non r[ée]glement[ée]e?|sans objet|pas de (r[èe]gle|limite)|n'est pas r[ée]glement/i.test(t)) return 'Non réglementée';
  t = t.replace(/\s+/g, ' ').trim();
  if (t.length > 120) { const k = t.lastIndexOf(' ', 117); t = t.slice(0, k > 60 ? k : 117) + '…'; }
  return t;
}
"""
s = s.rstrip('\n') + '\n' + f
open(p, 'w', encoding='utf-8').write(s); print('patch hauteur_texte appliqué')
