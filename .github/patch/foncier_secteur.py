"""Foncier entreprises : procédures collectives récentes du secteur (BODACC du jour), liens vers les annonces et les ventes aux enchères, facture en franchise de TVA."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, tag):
    global s
    c = s.count(a)
    if c != 1: print('ANCRE', tag, c); sys.exit(1)
    s = s.replace(a, b)

rep("TerrenUrbanisme, marque de la SASU ArConciergerie · SIREN 948 992 102 · TVA FR31948992102 · contact@terrenurbanisme.com",
    "TerrenUrbanisme, entreprise individuelle · SIREN 898 332 473 · TVA non applicable, article 293 B du CGI · contact@terrenurbanisme.com", 'footer')
import re as _re
_n = len(_re.findall(r"f\.set\('line_items\[0\]\[tax_rates\]\[0\]', TAX\)", s))
if _n != 1: print('ANCRE tax', _n); sys.exit(1)
s = _re.sub(r"f\.set\('line_items\[0\]\[tax_rates\]\[0\]', TAX\)", "void TAX /* franchise en base de TVA, article 293 B du CGI */", s)

rep("// ---------- PDF ----------", r"""// ---------- Secteur : procédures collectives du jour et liens d'annonces ----------
const getJ = async (u: string, ms = 15000) => { try { const r = await fetch(u, { signal: AbortSignal.timeout(ms) }); return r.ok ? await r.json() : null; } catch { return null; } };
const pj = (v: any) => { if (!v || v === 'None') return null; if (typeof v === 'object') return v; try { return JSON.parse(v); } catch { return null; } };
async function secteur(q: any, depList: string[], sites: any[]) {
  const g = await getJ(`https://geo.api.gouv.fr/communes/${encodeURIComponent(q.insee || '')}?fields=nom,codesPostaux,codeDepartement`);
  const nomC = (g && g.nom) || q.commune, cp0 = g && g.codesPostaux && g.codesPostaux[0] ? g.codesPostaux[0] : '';
  const deps = depList.length ? depList : (g && g.codeDepartement ? [g.codeDepartement] : []);
  const cps = new Set<string>();
  for (const d of deps) {
    const l = await getJ(`https://geo.api.gouv.fr/departements/${d}/communes?fields=centre,codesPostaux`, 20000) || [];
    for (const c of l) { const ce = c.centre && c.centre.coordinates; if (ce && hav(q.lat, q.lon, ce[1], ce[0]) <= q.rayon_km + 2) (c.codesPostaux || []).forEach((x: string) => cps.add(x)); }
  }
  const since = new Date(Date.now() - 365 * 864e5).toISOString().slice(0, 10), L = [...cps], raw: any[] = [];
  for (let i = 0; i < L.length && raw.length < 600; i += 30) {
    const ch = L.slice(i, i + 30);
    const where = `familleavis="collective" and dateparution>="${since}" and (${ch.map(x => 'cp="' + x + '"').join(' or ')})`;
    const j = await getJ('https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records?where=' + encodeURIComponent(where) + '&select=commercant,ville,cp,dateparution,jugement,registre,url_complete,listepersonnes&order_by=dateparution%20desc&limit=100');
    for (const r of (j && j.results) || []) raw.push(r);
  }
  const bySiren = new Map<string, any>();
  for (const r of raw) {
    const ju = pj(r.jugement) || {}; const nat = String(ju.nature || ''), fam = String(ju.famille || '');
    if (!/liquidation|redressement|cession|sauvegarde/i.test(nat) || /cl[ôo]ture|r[ée]solution du plan|homologation|infirm|rapport/i.test(nat)) continue;
    const reg = Array.isArray(r.registre) ? r.registre : String(r.registre || '').match(/\d{9}/g) || [];
    const siren = String(reg.find((x: string) => /^\d{9}$/.test(String(x).replace(/\s/g, ''))) || '').replace(/\s/g, '');
    const comp = String(ju.complementJugement || '');
    const mm = comp.match(/(?:d[ée]sign(?:ant|e)|nomm(?:ant|e))\s+(?:en qualit[ée] de\s+)?(?:mandataire judiciaire|liquidateur(?: judiciaire)?|administrateur judiciaire)\s*:?\s*([^,;.]+(?:,\s*repr[ée]sent[ée]e? par [^,;.]+)?)/i);
    const lp = pj(r.listepersonnes); const pers = lp && (Array.isArray(lp.personne) ? lp.personne[0] : lp.personne) || {};
    const it = { nom: r.commercant || pers.denomination || '', activite: String(pers.activite || '').replace(/\s+/g, ' ').slice(0, 110), ville: r.ville || '', cp: r.cp || '', date: ju.date || r.dateparution || '', nature: nat.replace(/^Jugement (d'ouverture d'une procédure de |prononçant (la |le )?|d'ouverture de )/i, '').replace(/^./, (c: string) => c.toUpperCase()), mandataire: mm ? mm[1].trim().replace(/\s+/g, ' ') : '', url: r.url_complete || '', siren, liq: /liquidation/i.test(nat) };
    const k = siren || (it.nom + it.cp);
    if (!bySiren.has(k)) bySiren.set(k, it);
  }
  const procs = [...bySiren.values()].sort((a, b) => (Number(b.liq) - Number(a.liq)) || String(b.date).localeCompare(String(a.date)));
  let maj = 0;
  for (const s0 of sites) { if (!s0.siren) continue; const p0 = bySiren.get(String(s0.siren)); if (p0) { s0.proc_nature = p0.nature; s0.proc_date = p0.date; s0.proc_url = p0.url; s0.mandataire = p0.mandataire; if (!s0.dif) { s0.dif = true; s0.score += 25; } maj++; } }
  if (maj) sites.sort((a, b) => b.score - a.score);
  const slug = String(nomC).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const sc = cp0 ? slug + '-' + cp0 : '';
  const links: [string, string, string][] = [];
  if (sc) {
    if (q.besoin !== 'terrain') {
      links.push(['BureauxLocaux : entrepôts et locaux d\'activité à vendre', 'Annonces d\'agences spécialisées en immobilier d\'entreprise, autour de ' + nomC + '.', `https://www.bureauxlocaux.com/immobilier-d-entreprise/annonces/${sc}/vente-entrepots`]);
      links.push(['BureauxLocaux : entrepôts et locaux d\'activité à louer', 'Les mêmes biens en location, souvent plus rapides à occuper.', `https://www.bureauxlocaux.com/immobilier-d-entreprise/annonces/${sc}/location-entrepots`]);
      links.push(['Geolocaux : entrepôts à louer', 'Autre portail d\'immobilier d\'entreprise, avec la carte des annonces.', `https://geolocaux.com/location/entrepot/${sc}`]);
      links.push(['Zimo : locaux d\'activité à vendre', 'Agrégateur qui rassemble les annonces de nombreuses agences.', `https://www.zimo.fr/annonces/immobilier-professionnel/vente/local-d-activite/${sc}`]);
    }
    if (q.besoin !== 'batiment') {
      links.push(['BureauxLocaux : terrains d\'activité à vendre', 'Terrains industriels et commerciaux proposés par les agences.', `https://www.bureauxlocaux.com/immobilier-d-entreprise/annonces/${sc}/vente-terrains`]);
      links.push(['Geolocaux : terrains à vendre', 'Terrains proposés aux entreprises, avec la carte des annonces.', `https://geolocaux.com/vente/terrain/${sc}`]);
      links.push(['Zimo : terrains à vendre', 'Terrains constructibles ou non, toutes agences confondues.', `https://www.zimo.fr/annonces/immobilier-professionnel/vente/terrain/${sc}`]);
      links.push(['Zimo : terrains agricoles à vendre', 'Pour une activité agricole ou un projet qui en a besoin.', `https://www.zimo.fr/annonces/immobilier-professionnel/vente/terrain-agricole/${sc}`]);
      links.push(['SAFER : propriétés agricoles à vendre', 'Biens mis en vente par les SAFER, qui attribuent les terres agricoles.', 'https://www.proprietes-rurales.com/vente-propriete-agricole/']);
    }
  }
  const ench: [string, string, string][] = [
    ['Licitor : prochaines ventes aux enchères immobilières', 'Biens saisis ou vendus sur décision de justice, avec la date de l\'audience et la mise à prix.', 'https://www.licitor.com/ventes-aux-encheres-immobilieres/france.html'],
    ['Avoventes : site des avocats pour les ventes judiciaires', 'Plateforme du Conseil national des barreaux : ventes aux enchères devant les tribunaux.', 'https://avoventes.fr/recherche/toutes']
  ];
  return { nomC, procs, maj, links, ench };
}

// ---------- PDF ----------""", 'secteur')

_m = _re.findall(r"async function buildPdf\(q(?::\s*any)?,\s*sites(?::\s*any\[\])?,\s*ref(?::\s*string)?\)\s*\{", s)
if len(_m) != 1:
    i0 = s.find('function buildPdf'); print('ANCRE sig', len(_m), repr(s[i0-20:i0+120])); sys.exit(1)
s = s.replace(_m[0], "async function buildPdf(q: any, sites: any[], ref: string, X: any = {}) {")
_m = _re.findall(r"const bytes = await buildPdf\(row,\s*sites,\s*ref\);", s)
if len(_m) != 1:
    i0 = s.find('await buildPdf'); print('ANCRE call', len(_m), repr(s[i0-40:i0+80])); sys.exit(1)
s = s.replace(_m[0], "const X = await secteur(row, depList, sites).catch((e: any) => { console.error('secteur', e); return {}; });\n    const bytes = await buildPdf(row, sites, ref, X);")

_SEC = r"""  // Procédures collectives récentes du secteur
  const linkAt = (x: number, yb: number, w: number, h: number, u: string) => {
    try { const a = pdf.context.obj({ Type: 'Annot', Subtype: 'Link', Rect: [x, yb, x + w, yb + h], Border: [0, 0, 0], A: { Type: 'Action', S: 'URI', URI: PDFLib.PDFString.of(u) } }); const r0 = pdf.context.register(a); const an = page.node.lookup(PDFLib.PDFName.of('Annots')); if (an) an.push(r0); else page.node.set(PDFLib.PDFName.of('Annots'), pdf.context.obj([r0])); } catch (e) { console.error('lien', e); }
  };
  const bouton = (t: string, d: string, u: string) => {
    const ld = wrap(d, F, 8.5, CW - 60); const h = 26 + ld.length * 11; ensure(h + 8);
    page.drawRectangle({ x: M, y: y - h + 10, width: CW, height: h, borderColor: rgb(C.ligne), borderWidth: 0.8, color: rgb(C.white) });
    page.drawText(clean(t), { x: M + 12, y: y - 6, size: 10, font: B, color: rgb(C.t) });
    ld.forEach((l, i) => page.drawText(l, { x: M + 12, y: y - 20 - i * 11, size: 8.5, font: F, color: rgb(C.muet) }));
    page.drawText('Ouvrir', { x: W - M - 46, y: y - 6, size: 9, font: B, color: rgb(C.t) });
    linkAt(M, y - h + 10, CW, h, u); y -= h + 6;
  };
  if (X.procs && X.procs.length) {
    const P = X.procs as any[];
    newPage('Entreprises en procédure collective dans votre secteur');
    text(`${nb(P.length)} entreprise${P.length > 1 ? 's' : ''} du secteur (rayon de ${q.rayon_km} km) ${P.length > 1 ? 'ont' : 'a'} fait l'objet, depuis douze mois, d'un redressement, d'une liquidation ou d'un plan de cession. Source : BODACC, consulté le jour du rapport.`, { size: 9.5 });
    note('Pourquoi c\'est utile : les locaux, hangars, terrains ou baux de ces entreprises peuvent être vendus ou cédés, souvent rapidement et en dessous du marché. La vente est conduite par le mandataire ou le liquidateur désigné par le tribunal : c\'est lui qu\'il faut contacter, en citant le nom de la société.' + (X.maj ? ` ${nb(X.maj)} des sites listés plus haut appartiennent à l'une de ces entreprises.` : ''));
    table([{ label: 'SOCIÉTÉ', w: 0.2, bold: true }, { label: 'ACTIVITÉ', w: 0.24 }, { label: 'COMMUNE', w: 0.13 }, { label: 'PROCÉDURE', w: 0.2 }, { label: 'MANDATAIRE OU LIQUIDATEUR', w: 0.23 }],
      P.slice(0, 80).map(p => [p.nom, p.activite || '–', p.ville, p.nature + (p.date ? ' (' + String(p.date).split('-').reverse().join('/') + ')' : ''), p.mandataire || 'Voir l\'annonce BODACC']), { color: (r: any[], i: number) => i === 3 && /liquidation/i.test(String(r[3])) ? C.non : null });
    if (P.length > 80) text(`Les ${nb(P.length - 80)} procédures suivantes, plus anciennes, sont disponibles sur demande.`, { size: 8.5, color: C.muet });
    text('Le détail de chaque procédure (jugement, mandataire, date de cessation des paiements) se consulte sur bodacc.fr en recherchant le nom de la société.', { size: 8.5, color: C.muet });
  }
  // Annonces et ventes aux enchères
  if ((X.links && X.links.length) || (X.ench && X.ench.length)) {
    newPage('Annonces et ventes en cours');
    text(`Les biens mis en vente ces derniers jours n'apparaissent pas encore dans les fichiers publics. Ces boutons ouvrent directement les annonces correspondant à votre recherche autour de ${X.nomC || q.commune} : cliquez pour voir les offres du jour.`, { size: 9.5 });
    if (X.links && X.links.length) { h3('Annonces d\'immobilier d\'entreprise'); for (const [t, d, u] of X.links) bouton(t, d, u); }
    if (X.ench && X.ench.length) { h3('Ventes aux enchères judiciaires'); text('Biens vendus sur décision de justice : la visite est organisée avant l\'audience et l\'enchère se porte par l\'intermédiaire d\'un avocat.', { size: 9 }); for (const [t, d, u] of X.ench) bouton(t, d, u); }
  }

"""
if s.count("// Électricité") != 1: print('ANCRE sections', s.count("// Électricité")); sys.exit(1)
s = s.replace("// Électricité", _SEC.strip() + "\n  // Électricité", 1)

_ME = "['Électricité', 'Postes électriques recensés dans OpenStreetMap.']"
if s.count(_ME) != 1: print('ANCRE methode', s.count(_ME)); sys.exit(1)
s = s.replace(_ME, _ME + ",\n    ['Procédures récentes', 'Annonces de procédures collectives du BODACC des douze derniers mois, interrogées le jour du rapport, pour les communes du rayon de recherche.'],\n    ['Annonces', 'Liens vers les recherches des portails d\\'annonces et des sites de ventes aux enchères : les offres affichées sont celles du jour où vous cliquez.']")
open(p, 'w', encoding='utf-8').write(s); print('ok foncier')
