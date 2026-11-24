"""Plan DXF téléchargeable par un lien (bouton dans le rapport et lien dans l'e-mail), en plus de la pièce jointe au PDF."""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: print('ANCRE', c, a[:120]); sys.exit(1)
    s = s.replace(a, b)
# 1. Adresse de téléchargement et service
rep("async function modulesPro(p, c, d, out = {}) {",
    """const dxfUrl = (insee, sec, num) => (Deno.env.get('SUPABASE_URL') || 'https://nmoigruxnhsidrhqtzid.supabase.co') + '/functions/v1/stripe-webhook?dxf=' + encodeURIComponent(insee + '-' + sec + '-' + num);
async function serveDxf(v) {
  const m = String(v || '').toUpperCase().match(/^((?:\\d{2}|2[AB])\\d{3}|97\\d{3})-([0-9A-Z]{1,2})-(\\d{1,4})$/);
  if (!m || /^97/.test(m[1])) return new Response('Plan indisponible pour cette parcelle.', { status: 400, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
  try {
    const pj = await getJSON(parcelUrl(m[1], m[2].padStart(2, '0'), m[3].padStart(4, '0')), 20000);
    const f = pj && pj.features && pj.features[0];
    if (!f) return new Response('Parcelle introuvable.', { status: 404, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
    const x = await planDxf(turf.feature(f.geometry));
    return new Response(x.bytes, { headers: { 'Content-Type': 'application/dxf', 'Content-Disposition': 'attachment; filename="Plan-' + m[1] + '-' + m[2] + '-' + m[3] + '.dxf"', 'Cache-Control': 'public, max-age=86400', 'X-Robots-Tag': 'noindex' } });
  } catch (e) { console.error('dxf', String(e && e.message || e).slice(0, 160)); return new Response('Plan momentanément indisponible, réessayez dans un instant.', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } }); }
}
async function modulesPro(p, c, d, out = {}) {""")
rep("  if (req.method === 'POST' && url.searchParams.get('remise') === '1') return await remiseInscription(req);",
    "  if (req.method === 'GET' && url.searchParams.get('dxf')) return await serveDxf(url.searchParams.get('dxf'));\n  if (req.method === 'POST' && url.searchParams.get('remise') === '1') return await remiseInscription(req);")
# 2. Rapport : bouton de téléchargement cliquable
i = s.index("        text('Le fichier « Plan-' + R.insee + '-' + R.section + '-' + R.numero + '.dxf » est joint à ce PDF.")
j = s.index("\n", i)
s = s[:i] + r"""        { const U = dxfUrl(R.insee, R.section, R.numero), lab = 'Télécharger le plan DXF', bw = tw(lab, B, 11) + 40; ensure(44);
          page.drawRectangle({ x: M, y: y - 32, width: bw, height: 30, color: C.t });
          page.drawText(lab, { x: M + 20, y: y - 21, size: 11, font: B, color: C.white });
          try { const { PDFName, PDFString } = PDFLib; const a = pdf.context.obj({ Type: 'Annot', Subtype: 'Link', Rect: [M, y - 32, M + bw, y - 2], Border: [0, 0, 0], A: { Type: 'Action', S: 'URI', URI: PDFString.of(U) } }); page.node.addAnnot(pdf.context.register(a)); } catch (e) {}
          y -= 44; }
        text('Cliquez sur le bouton pour télécharger le fichier « Plan-' + R.insee + '-' + R.section + '-' + R.numero + '.dxf » (le lien figure aussi dans l\'e-mail d\'envoi du rapport), puis ouvrez-le dans votre logiciel de dessin : AutoCAD, ArchiCAD, Revit, SketchUp, DraftSight… Le plan est également joint au PDF (icône trombone dans Adobe Acrobat Reader sur ordinateur).', { size: 9.5 });""" + s[j:]
# 3. E-mail d'envoi : lien vers le plan
rep("body: JSON.stringify({ to: dest, path, file, link: d.link, ref: { commune: d.ref.commune, section: d.ref.section, numero: d.ref.numero }",
    "body: JSON.stringify({ to: dest, path, file, link: d.link, ref: { commune: d.ref.commune, section: d.ref.section, numero: d.ref.numero, insee: d.ref.insee }, synth: !!synth")
rep("await sendMail(b.to, { ref: b.ref, verdict: b.verdict, link: b.link, offert: b.offert || null }, pdf, b.file, true);",
    "await sendMail(b.to, { ref: b.ref, verdict: b.verdict, link: b.link, offert: b.offert || null, synth: !!b.synth }, pdf, b.file, true);")
rep("""<p style="margin:0 0 26px"><a href="${link}" style="display:inline-block;background:#A3462C;color:#fff;text-decoration:none;font-weight:700;font-size:15px;padding:13px 22px;border-radius:12px">Ouvrir mon rapport</a></p>""",
    """<p style="margin:0 0 26px"><a href="${link}" style="display:inline-block;background:#A3462C;color:#fff;text-decoration:none;font-weight:700;font-size:15px;padding:13px 22px;border-radius:12px">Ouvrir mon rapport</a></p>
${!d.synth && d.ref && d.ref.insee && !/^97/.test(String(d.ref.insee)) ? `<p style="font-size:14px;line-height:1.6;margin:-12px 0 22px">Plan du terrain au format DXF (AutoCAD, ArchiCAD, Revit, SketchUp) : <a href="${dxfUrl(d.ref.insee, d.ref.section, d.ref.numero)}" style="color:#A3462C;font-weight:700">télécharger le plan</a></p>` : ''}""")
open(p, 'w', encoding='utf-8').write(s); print('ok dxf_lien')
