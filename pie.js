// pie.js — la franja nueva del pie de página, en todas las páginas (24-oct-2026).
//
// 1. Mapa chico en los colores del pie (grafito, calles tenues, letras crema).
//    El mismo MapLibre + OpenFreeMap del mapa de #contacto, pero quieto
//    (interactive:false): es para ubicar, no para explorar; para llegar están
//    los enlaces de abajo. Se baja solo cuando el pie está a ~400 px, así que
//    no frena la carga. Sin WebGL o sin red queda la caja oscura con los
//    enlaces, que funcionan solos. La atribución de OpenStreetMap es
//    obligatoria: no la quites.
// 2. «Pregúntale a tu IA»: los enlaces ya traen la pregunta (ChatGPT, Claude
//    y Perplexity la aceptan en la URL). Gemini no acepta ?q= (probado el
//    24-oct): ahí se copia la pregunta al portapapeles y se avisa.

(function () {
  const caja = document.getElementById('pieMapa');
  if (!caja) return;
  const clinica = [parseFloat(caja.dataset.lng), parseFloat(caja.dataset.lat)];

  const P = { tierra: '#2E2E2B', edificio: '#353532', borde: '#3D3D39', parque: 'rgba(130,134,127,0.22)',
    agua: '#33373A', calle: '#45443F', calleMayor: '#55534C', texto: '#B9B2A4', halo: '#2E2E2B' };
  const quitar = /^(airport|aeroway|highway-shield|road_shield|boundary|label_country|label_state|landcover_(ice|glacier)|poi)/;

  function recolorear(estilo) {
    estilo.layers = estilo.layers.filter((l) => !quitar.test(l.id));
    for (const l of estilo.layers) {
      const p = (l.paint = l.paint || {});
      const id = l.id;
      if (id === 'background') p['background-color'] = P.tierra;
      else if (id === 'park' || id === 'landcover_wood') { p['fill-color'] = P.parque; p['fill-opacity'] = 1; }
      else if (id === 'water') p['fill-color'] = P.agua;
      else if (id === 'waterway') p['line-color'] = P.agua;
      else if (id === 'landuse_residential') p['fill-opacity'] = 0;
      else if (id === 'building') { p['fill-color'] = P.edificio; p['fill-outline-color'] = P.borde; }
      else if (/casing/.test(id)) p['line-color'] = P.tierra;
      else if (/^highway|^road_pier/.test(id) && l.type === 'line') p['line-color'] = /major|motorway|trunk|primary/.test(id) ? P.calleMayor : P.calle;
      else if (/^railway/.test(id)) p['line-color'] = /dash/.test(id) ? P.tierra : P.calle;
      if (l.type === 'symbol' && l.paint) {
        p['text-color'] = P.texto; p['text-halo-color'] = P.halo; p['text-halo-width'] = 1.2; p['text-halo-blur'] = 0;
      }
    }
    return estilo;
  }

  // Si la portada ya está bajando MapLibre para #contacto, se espera a ese mismo <script>.
  function cargar(url, tipo) {
    const previo = document.querySelector(tipo === 'css' ? `link[href="${url}"]` : `script[src="${url}"]`);
    if (previo) {
      if (tipo === 'css' || window.maplibregl) return Promise.resolve();
      return new Promise((ok, mal) => { previo.addEventListener('load', ok); previo.addEventListener('error', mal); });
    }
    return new Promise((ok, mal) => {
      const el = document.createElement(tipo === 'css' ? 'link' : 'script');
      if (tipo === 'css') { el.rel = 'stylesheet'; el.href = url; } else { el.src = url; }
      el.onload = ok; el.onerror = mal;
      document.head.appendChild(el);
    });
  }

  async function iniciar() {
    const base = 'https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/4.7.1/';
    try {
      const [, , estilo] = await Promise.all([
        cargar(base + 'maplibre-gl.min.css', 'css'),
        cargar(base + 'maplibre-gl.min.js', 'js'),
        fetch('https://tiles.openfreemap.org/styles/positron').then((r) => r.json()),
      ]);
      const map = new maplibregl.Map({
        container: caja, style: recolorear(estilo),
        center: clinica, zoom: 15.4, interactive: false,
        attributionControl: false, fadeDuration: 0,
        locale: { 'AttributionControl.ToggleAttribution': 'Créditos del mapa' },
      });
      map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');
      map.on('load', () => caja.classList.add('pie-mapa__lienzo--listo'));
      // Es un mapa quieto: el lienzo no recibe foco ni se anuncia como otra región (la caja ya
      // lleva su etiqueta), y el marcador es decorativo.
      const lienzo = map.getCanvas();
      lienzo.setAttribute('tabindex', '-1'); lienzo.setAttribute('aria-hidden', 'true'); lienzo.removeAttribute('role');
      const el = document.createElement('div');
      el.className = 'pie-pin';
      el.innerHTML = '<img src="images/web/met-positivo-03.webp" alt="">';
      new maplibregl.Marker({ element: el, anchor: 'center' }).setLngLat(clinica).addTo(map);
      el.removeAttribute('aria-label'); el.removeAttribute('role'); el.setAttribute('aria-hidden', 'true');
    } catch (e) {
      // sin WebGL o sin red: se queda la caja oscura; los enlaces de abajo funcionan solos
    }
  }

  if (!('IntersectionObserver' in window)) { iniciar(); return; }
  const io = new IntersectionObserver(([e]) => {
    if (!e.isIntersecting) return;
    io.disconnect();
    iniciar();
  }, { rootMargin: '400px 0px' });
  io.observe(caja);
})();

(function () {
  const gemini = document.querySelector('.pie-ia__btn[data-copiar]');
  const nota = document.querySelector('.pie-ia__nota');
  if (!gemini || !nota) return;
  gemini.addEventListener('click', () => {
    const texto = gemini.dataset.copiar;
    if (navigator.clipboard) navigator.clipboard.writeText(texto).catch(() => {});
    nota.hidden = false;
  });
})();

// 3. Un solo «Agendar consulta» a la vista (24-oct, Sebas: «dos botones para lo mismo»).
//    Mientras se ve el botón principal de la primera pantalla (portada o cabecera del
//    servicio), <html> lleva .cta-principal-visible: el CSS esconde el botón de la barra
//    de arriba, y aquí se esconde la barra fija del teléfono. Al salir ese botón de la
//    pantalla aparecen los dos. La barra también se esconde sobre el bloque final
//    (#contacto o .pilar-cta), que ya trae los mismos botones en grande.
//    El HTML ya trae los dos estados «escondidos» para que no parpadeen al cargar.
(function () {
  const raiz = document.documentElement;
  const barra = document.querySelector('.barra-movil');
  const principal = document.querySelector('.hero .btn-primary, .pilar-hero .btn-primary');
  const final = document.querySelector('#contacto, .pilar-cta');
  if (!principal || !('IntersectionObserver' in window)) {
    raiz.classList.remove('cta-principal-visible');
    if (barra) barra.classList.remove('oculta');
    return;
  }
  const visible = new Map();
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => visible.set(e.target, e.isIntersecting));
    const arriba = !!visible.get(principal);
    raiz.classList.toggle('cta-principal-visible', arriba);
    if (barra) barra.classList.toggle('oculta', arriba || !!visible.get(final));
  }, { threshold: 0.25 });
  io.observe(principal);
  if (final) io.observe(final);
})();
