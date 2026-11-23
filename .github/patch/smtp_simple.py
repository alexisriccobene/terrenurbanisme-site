# E-mails d'accès collaborateur et d'alerte d'ouverture : envoi SMTP direct avec confirmation du serveur (comme les rapports)
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
fn = r"""// Envoi SMTP direct sans pièce jointe : le serveur confirme la réception du message (code 250)
async function smtpSimple(toList, subject, text, html) {
  const host = Deno.env.get('SMTP_HOST') || 'ssl0.ovh.net', port = Number(Deno.env.get('SMTP_PORT') || '465');
  const user = Deno.env.get('SMTP_USER') || 'contact@terrenurbanisme.com', pass = Deno.env.get('SMTP_PASSWORD') || '';
  const enc = new TextEncoder(), dec = new TextDecoder();
  const conn = await Deno.connectTls({ hostname: host, port });
  let buf = '';
  const read = async () => { const b = new Uint8Array(4096); for (;;) { const m = buf.match(/(?:^|\r\n)(\d{3}) [^\r\n]*\r\n$/); if (m) { const c = +m[1]; buf = ''; return c; } const n = await conn.read(b); if (n === null) throw new Error('SMTP fermé'); buf += dec.decode(b.subarray(0, n)); } };
  const cmd = async (line, ok) => { await conn.write(enc.encode(line + '\r\n')); const c = await read(); if (!ok.includes(c)) throw new Error('SMTP ' + c + ' après ' + line.split(' ')[0]); };
  try {
    if (await read() !== 220) throw new Error('SMTP accueil');
    await cmd('EHLO terrenurbanisme.com', [250]);
    await cmd('AUTH LOGIN', [334]); await cmd(btoa(user), [334]); await cmd(btoa(pass), [235]);
    await cmd('MAIL FROM:<' + user + '>', [250]);
    for (const t of toList) await cmd('RCPT TO:<' + t + '>', [250, 251]);
    await cmd('DATA', [354]);
    const A = 'ta' + crypto.randomUUID().replace(/-/g, '');
    const hdr = (v) => '=?UTF-8?B?' + b64part(v).replace(/\r\n/g, '') + '?=';
    const msg = ['From: ' + hdr('TerrenUrbanisme') + ' <' + user + '>', 'To: ' + toList.join(', '), 'Subject: ' + hdr(subject), 'Date: ' + new Date().toUTCString(),
      'Message-ID: <' + crypto.randomUUID() + '@terrenurbanisme.com>', 'MIME-Version: 1.0', 'Content-Type: multipart/alternative; boundary="' + A + '"', '',
      '--' + A, 'Content-Type: text/plain; charset="utf-8"', 'Content-Transfer-Encoding: base64', '', b64part(text),
      '--' + A, 'Content-Type: text/html; charset="utf-8"', 'Content-Transfer-Encoding: base64', '', b64part(html), '--' + A + '--', '', '.', ''].join('\r\n');
    await conn.write(enc.encode(msg));
    if (await read() !== 250) throw new Error('SMTP message refusé');
    try { await conn.write(enc.encode('QUIT\r\n')); } catch (e) {}
  } finally { try { conn.close(); } catch (e) {} }
}
"""
a = "function mailHtml(d, link, attach) {"
if s.count(a) != 1: sys.exit('ancre mailHtml')
s = s.replace(a, fn + a)
# Accès collaborateur
m = re.search(r"  try \{\n    const client = new SMTPClient\(\{ connection:.*?to: em, subject: (.*?), mimeContent: mimeParts\(txt, html\) \}\); \}.*?\n  \} catch \(e\) \{ console\.error\('accès agent', e\); return jres\(\{ ok: true, mail: false \}\); \}", s, re.S)
if not m: sys.exit('ancre accès')
s = s[:m.start()] + "  try { await smtpSimple([em], " + m.group(1) + ", txt, html); } catch (e) { console.error('accès agent', String(e && e.message || e)); return jres({ ok: true, mail: false }); }" + s[m.end():]
# Alerte d'ouverture
m = re.search(r"    const client = new SMTPClient\(\{ connection:.*?subject: (qui \+ ' vient d\\'ouvrir votre rapport'), mimeContent: mimeParts\(txt, html\) \}\); \}\n.*?finally \{ if \(!coupe\) \{ try \{ await client\.close\(\); \} catch \(e\) \{\} \} \}\n", s, re.S)
if not m: sys.exit('ancre alerte')
s = s[:m.start()] + "    await smtpSimple([to], " + m.group(1) + ", txt, html);\n" + s[m.end():]
open(p, 'w', encoding='utf-8').write(s); print('patch smtp simple appliqué')
