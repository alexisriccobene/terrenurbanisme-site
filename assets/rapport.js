/* Lecture d'un rapport en ligne (pdf.js) : script séparé pour respecter la politique de sécurité du site */
const slug = (location.pathname.indexOf('/r/') === 0 ? decodeURIComponent(location.pathname.slice(3).replace(/[/]$/, '')) : '') || new URLSearchParams(location.search).get('r') || '';
const url = '/rapport/' + encodeURIComponent(slug) + '.pdf' + (new URLSearchParams(location.search).get('a') === '1' ? '?a=1' : '');
document.getElementById('dl').href = url;
const show = t => { document.getElementById('wrap').innerHTML = '<div class="msg">' + t + '</div>'; };
if (!/^[a-z0-9-]{8,120}$/.test(slug)) show('Ce lien de rapport n\'est pas valide. Retrouvez vos rapports dans <a href="/espace.html">votre espace</a>.');
else {
  try {
    const pdfjsLib = await import('/assets/pdfjs/pdf.min.mjs');
    globalThis.pdfjsLib = pdfjsLib;
    pdfjsLib.GlobalWorkerOptions.workerSrc = '/assets/pdfjs/pdf.worker.min.mjs';
    const { EventBus, PDFLinkService, PDFViewer, LinkTarget } = await import('/assets/pdfjs/pdf_viewer.mjs');
    const eventBus = new EventBus();
    const linkService = new PDFLinkService({ eventBus, externalLinkTarget: LinkTarget.BLANK, externalLinkRel: 'noopener noreferrer' });
    const viewer = new PDFViewer({ container: document.getElementById('wrap'), viewer: document.getElementById('viewer'), eventBus, linkService, textLayerMode: 1, annotationMode: pdfjsLib.AnnotationMode.ENABLE });
    linkService.setViewer(viewer);
    eventBus.on('pagesinit', () => { viewer.currentScaleValue = window.innerWidth < 900 ? 'page-width' : 'page-fit'; if (window.innerWidth >= 900) viewer.currentScaleValue = Math.min(1.4, viewer.currentScale * 1.6).toString(); });
    eventBus.on('pagechanging', e => { document.getElementById('pg').textContent = 'Page ' + e.pageNumber + ' / ' + viewer.pagesCount; });
    window.addEventListener('resize', () => { if (window.innerWidth < 900) viewer.currentScaleValue = 'page-width'; });
    const doc = await pdfjsLib.getDocument({ url, isEvalSupported: false }).promise;
    viewer.setDocument(doc); linkService.setDocument(doc, null);
    doc.getMetadata().then(m => { const t = m && m.info && m.info.Title; if (t) document.title = t + ' | TerrenUrbanisme'; }).catch(() => {});
    document.getElementById('pg').textContent = 'Page 1 / ' + doc.numPages;
  } catch (e) {
    show('Le rapport n\'a pas pu être affiché ici. <br><br><a class="btn p" href="' + url + '">Ouvrir le PDF</a>');
  }
}
