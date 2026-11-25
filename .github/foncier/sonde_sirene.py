# Sonde : colonnes et volume des fichiers Sirene (stock + géolocalisation INSEE), jointure test sur la Haute-Corse
import subprocess, sys, time
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'duckdb'], check=True)
import duckdb
GEO = 'https://static.data.gouv.fr/resources/geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques/20261123-064215/geoloc-geolocalisationetablissement-sirene-pour-etudes-statistiques-parquet.parquet'
STK = 'https://static.data.gouv.fr/resources/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/20261103-101714/stock-stocketablissement-parquet.parquet'
c = duckdb.connect(); c.execute('INSTALL httpfs; LOAD httpfs;')
for n, u in [('geo', GEO), ('stock', STK)]:
    print(n, c.execute(f"DESCRIBE SELECT * FROM read_parquet('{u}')").fetchall(), flush=True)
t = time.time()
print(c.execute(f"SELECT * FROM read_parquet('{GEO}') LIMIT 3").fetchall(), flush=True)
print('geo epsg', c.execute(f"SELECT epsg, count(*) FROM read_parquet('{GEO}') GROUP BY 1 ORDER BY 2 DESC LIMIT 10").fetchall() if True else '', time.time() - t, flush=True)
