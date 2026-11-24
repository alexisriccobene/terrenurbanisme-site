# Fibre : hors Corse, si la commune n'est pas encore préparée, préparation sur le serveur GitHub et attente (2 min max) avant la lecture directe
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "    if (!cache && !/^(2A|2B|20)$/.test(String(dep))) dispatchFibre(inseeTag).catch(() => {});"
assert s.count(a) == 1
s = s.replace(a, """    if (!cache && !/^(2A|2B|20)$/.test(String(dep))) {
      if (await dispatchFibre(inseeTag)) for (let i = 0; i < 12 && !cache; i++) { await new Promise(rs => setTimeout(rs, 10000)); cache = await fibreCache(inseeTag); }
    }""")
open(p, 'w', encoding='utf-8').write(s); print('patch fibre attente appliqué')
