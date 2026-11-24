"""Tuiles géoréférencées (WGS84) des plans de zonage officiels : extrait du plan avec la parcelle dans le rapport.
Grille fixe : tuile (ix, iy) = lon [ix*DX, (ix+1)*DX], lat [iy*DY, (iy+1)*DY], 512 px. Stockage : plu/<insee>/t/<ix>_<iy>.jpg"""
import os, json, glob, math, requests, numpy as np, cv2, fitz
from pyproj import Transformer
DX, DY, PX = 0.003, 0.002, 512
LOCAL = os.environ.get('LOCAL', '')
base = f"https://{os.environ.get('REF','')}.supabase.co"; K = os.environ.get('SR', ''); H = {'apikey': K, 'Authorization': 'Bearer ' + K}
T = Transformer.from_crs(4326, 2154, always_xy=True)
only = os.environ.get('INSEE', '')
for f in sorted(glob.glob('.github/plu/cfg/*.json')):
    cfg = json.load(open(f)); ins = cfg['insee']
    if only and ins not in only.split(','): continue
    tiles = {}
    for pl in cfg['planches']:
        b = open(f"{LOCAL}/p{pl['n']}.pdf", 'rb').read() if LOCAL else requests.get(pl['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=180).content
        page = fitz.open(stream=b, filetype='pdf')[0]; Z = 3.0
        pix = page.get_pixmap(matrix=fitz.Matrix(Z, Z), colorspace=fitz.csRGB, alpha=False)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, 3)[:, :, ::-1].copy()
        M = np.array(pl['affine']); A = np.vstack([M.T, [0, 0, 1]]); Ai = np.linalg.inv(A)
        G = np.array(pl['grille']['dxdy']) if pl.get('grille') else None; s = pl['grille']['pas'] if pl.get('grille') else 1
        def gofs(px, py):
            if G is None: return 0, 0
            fx = px / s; fy = py / s; i0 = np.clip(np.floor(fx).astype(int), 0, G.shape[1] - 2); j0 = np.clip(np.floor(fy).astype(int), 0, G.shape[0] - 2)
            ax = np.clip(fx - i0, 0, 1); ay = np.clip(fy - j0, 0, 1)
            t = G[j0, i0] * ((1 - ax) * (1 - ay))[..., None] + G[j0, i0 + 1] * (ax * (1 - ay))[..., None] + G[j0 + 1, i0] * ((1 - ax) * ay)[..., None] + G[j0 + 1, i0 + 1] * (ax * ay)[..., None]
            return t[..., 0], t[..., 1]
        def l93_to_page(X, Y):
            px = Ai[0, 0] * X + Ai[0, 1] * Y + Ai[0, 2]; py = Ai[1, 0] * X + Ai[1, 1] * Y + Ai[1, 2]
            for _ in range(3):
                gx, gy = gofs(px, py); X2 = X - gx; Y2 = Y - gy
                px = Ai[0, 0] * X2 + Ai[0, 1] * Y2 + Ai[0, 2]; py = Ai[1, 0] * X2 + Ai[1, 1] * Y2 + Ai[1, 2]
            return px, py
        # emprise de la planche en lon/lat
        W, Hh = page.rect.width, page.rect.height
        cs = np.array([[0, 0], [W, 0], [0, Hh], [W, Hh]]); q = np.column_stack([cs, np.ones(4)]) @ M
        TI = Transformer.from_crs(2154, 4326, always_xy=True); lo, la = TI.transform(q[:, 0], q[:, 1])
        for ix in range(math.floor(min(lo) / DX), math.floor(max(lo) / DX) + 1):
            for iy in range(math.floor(min(la) / DY), math.floor(max(la) / DY) + 1):
                u = (np.arange(PX) + 0.5) / PX; LON = ix * DX + u[None, :] * DX + 0 * u[:, None]; LAT = (iy + 1) * DY - u[:, None] * DY + 0 * u[None, :]
                X, Y = T.transform(LON, LAT); px, py = l93_to_page(X, Y)
                mx = (px * Z).astype(np.float32); my = (py * Z).astype(np.float32)
                ok = (mx >= 0) & (mx < img.shape[1] - 1) & (my >= 0) & (my < img.shape[0] - 1)
                if ok.mean() < 0.02: continue
                out = cv2.remap(img, mx, my, cv2.INTER_AREA if False else cv2.INTER_LINEAR, borderValue=(255, 255, 255))
                # garder les pixels non blancs : une planche ne masque pas sa voisine hors de son cadre
                key = (ix, iy)
                if key in tiles:
                    prev = tiles[key]; m = ok & (out.min(2) < 245); prev[m] = out[m]
                else:
                    out[~ok] = 255; tiles[key] = out
        print(ins, 'planche', pl['n'], 'tuiles', len(tiles), flush=True)
    for (ix, iy), im in tiles.items():
        if im.min() > 240: continue
        ok, jp = cv2.imencode('.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 82])
        if LOCAL: open(f'{LOCAL}/t_{ix}_{iy}.jpg', 'wb').write(jp.tobytes()); continue
        r = requests.post(f'{base}/storage/v1/object/plu/{ins}/t/{ix}_{iy}.jpg', headers={**H, 'Content-Type': 'image/jpeg', 'x-upsert': 'true'}, data=jp.tobytes(), timeout=60)
        if r.status_code >= 300: print('upload', r.status_code, r.text[:200])
    print(ins, 'tuiles envoyées', len(tiles), flush=True)
