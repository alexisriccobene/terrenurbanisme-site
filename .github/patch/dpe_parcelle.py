# Logements F/G autour du terrain : ajout de la parcelle cadastrale (section, numéro) de chaque logement, et du propriétaire s'il s'agit d'une société
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, label):
    global s
    if s.count(old) != 1: sys.exit('ancre introuvable : ' + label)
    s = s.replace(old, new)
rep("""by.set(k, { adresse: x.adresse_ban || '', dpe: x.etiquette_dpe, type: x.type_batiment || '', surf: Number(x.surface_habitable_logement) || null, date: x.date_etablissement_dpe ? frDate(String(x.date_etablissement_dpe).slice(0, 10)) : '', d: Math.round(d) }); }
    return [...by.values()].sort((a, b) => a.d - b.d).slice(0, 10);""",
"""by.set(k, { adresse: x.adresse_ban || '', dpe: x.etiquette_dpe, type: x.type_batiment || '', surf: Number(x.surface_habitable_logement) || null, date: x.date_etablissement_dpe ? frDate(String(x.date_etablissement_dpe).slice(0, 10)) : '', d: Math.round(d), pt }); }
    const L = [...by.values()].sort((a, b) => a.d - b.d).slice(0, 10);
    // Parcelle cadastrale de chaque logement (point de l'adresse), pour pouvoir identifier le bien et son propriétaire
    await Promise.all(L.map(async o => {
      try {
        const pj = await getJSON(`${CARTO}/cadastre/parcelle?_limit=1&geom=${encodeURIComponent(JSON.stringify({ type: 'Point', coordinates: o.pt }))}`, 8000);
        const f = pj && pj.features && pj.features[0];
        if (f && f.properties) {
          const q = f.properties; o.parcelle = 'Section ' + String(q.section || '').replace(/^0+/, '') + ' n° ' + String(Number(q.numero || 0)); o.idu = q.idu;
          const prop = pm && pm.props ? pm.props[q.idu] || '' : ''; if (prop) o.prop = prop;
        }
      } catch (e) { /* parcelle non trouvée : l'adresse suffit */ }
      delete o.pt;
    }));
    return L;""", 'dpe parcelle')
rep("""      table([{ label: 'ADRESSE', w: 0.4, bold: true }, { label: 'CLASSE', w: 0.1 }, { label: 'LOGEMENT', w: 0.15 }, { label: 'SURFACE', w: 0.12 }, { label: 'DISTANCE', w: 0.11 }, { label: 'DPE DU', w: 0.12 }],
        OP.pass.map(x => [x.adresse || '–', x.dpe, x.type ? x.type.charAt(0).toUpperCase() + x.type.slice(1) : '–', x.surf ? fmt(Math.round(x.surf)) + ' m²' : '–', fmt(Math.round(x.d / 10) * 10) + ' m', x.date || '–']), { size: 8.5, color: (r, i) => i === 1 ? C.non : null });""",
"""      table([{ label: 'PARCELLE', w: 0.17, bold: true }, { label: 'ADRESSE', w: 0.29 }, { label: 'CLASSE', w: 0.08 }, { label: 'LOGEMENT', w: 0.13 }, { label: 'SURFACE', w: 0.1 }, { label: 'DISTANCE', w: 0.1 }, { label: 'DPE DU', w: 0.13 }],
        OP.pass.map(x => [x.parcelle || '–', (x.adresse || '–') + (x.prop ? ' · propriétaire : ' + x.prop : ''), x.dpe, x.type ? x.type.charAt(0).toUpperCase() + x.type.slice(1) : '–', x.surf ? fmt(Math.round(x.surf)) + ' m²' : '–', fmt(Math.round(x.d / 10) * 10) + ' m', x.date || '–']), { size: 8.5, color: (r, i) => i === 2 ? C.non : null });
      text('La parcelle est celle du point d\\'adresse du logement (cadastre). Pour connaître son propriétaire lorsqu\\'il s\\'agit d\\'un particulier, demandez un relevé de propriété au service de la publicité foncière ou à la mairie.', { size: 8, color: C.muet });""", 'table dpe')
open(p, 'w', encoding='utf-8').write(s); print('patch dpe_parcelle appliqué')
