# Zonages communaux : le règlement est lu sur la copie stockée par TerrenUrbanisme (le site de la mairie peut être lent)
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    if s.count(old) != n: sys.exit('ancre introuvable : ' + old[:70])
    s = s.replace(old, new)
rep("select('libelle,libelong,typezone,urlfic,datappro,geom,bbox').eq('insee', insee);", "select('libelle,libelong,typezone,urlfic,copie,datappro,geom,bbox').eq('insee', insee);")
rep("properties: { libelle: r.libelle, libelong: r.libelong, typezone: r.typezone, urlfic: r.urlfic, datappro: r.datappro } }));\n  } catch (e) { console.warn('zonage_local', e); return []; }",
    "properties: { libelle: r.libelle, libelong: r.libelong, typezone: r.typezone, urlfic: r.urlfic, copie: r.copie, datappro: r.datappro } }));\n  } catch (e) { console.warn('zonage_local', e); return []; }")
rep("const urls = [gpuUrl && /\\.pdf$/i.test(gpuUrl) ? gpuUrl : '', p.urlfic", "const urls = [p.copie || '', gpuUrl && /\\.pdf$/i.test(gpuUrl) ? gpuUrl : '', p.urlfic")
rep("if (res) { res.zone = zone.code; res.url = url;", "if (res) { res.zone = zone.code; res.url = p.copie && url === p.copie && p.urlfic ? p.urlfic : url;")
open(p, 'w', encoding='utf-8').write(s); print('patch plu_local3 appliqué')
