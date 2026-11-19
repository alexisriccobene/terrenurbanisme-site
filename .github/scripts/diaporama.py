import subprocess, sys
def diaporama(images, out, d=3.5):
    # Carrousel 4:5 -> Short 9:16 : chaque image centrée sur la couleur de fond du visuel, fondu enchaîné
    n = len(images); d = 6.0 if n == 1 else d; f = 0.5
    bgs = ['#' + subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', im, '-vf', 'crop=2:2:8:8', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout[:3].hex() for im in images]
    cmd = ['ffmpeg', '-y', '-loglevel', 'error']
    for im in images: cmd += ['-loop', '1', '-t', str(d), '-i', im]
    fc = ''.join('[%d:v]scale=1080:1350,pad=1080:1920:0:285:color=%s,setsar=1,fps=30,format=yuv420p[s%d];' % (i, bgs[i], i) for i in range(n))
    last = 's0'
    for i in range(1, n):
        fc += '[%s][s%d]xfade=transition=fade:duration=%s:offset=%s[x%d];' % (last, i, f, round(i * (d - f), 2), i); last = 'x%d' % i
    cmd += ['-filter_complex', fc.rstrip(';'), '-map', '[%s]' % last, '-c:v', 'libx264', '-crf', '26', '-preset', 'veryfast', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True); return out
if __name__ == '__main__': diaporama(sys.argv[2:], sys.argv[1])
