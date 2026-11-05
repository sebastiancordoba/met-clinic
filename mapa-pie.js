/* mapa-pie.js — el mapa del pie se vuelve un mapa de verdad (4-nov-2026, Sebas: «que se pueda mover, acercar y alejar»).

   pie.js (5) lo baja solo cuando el pie se acerca a la pantalla o al primer toque, y hasta entonces se ve el SVG de
   generar-mapa.py, que hace de póster. Aquí se baja MapLibre GL (cdnjs) y las teselas vectoriales de OpenStreetMap que
   sirve OpenFreeMap (sin llave ni cuenta). El estilo «positron» se recolorea con la paleta del SVG: crema liso, calles en
   dos grosores (las avenidas más gruesas), parques pálidos y sin nombres de calles ni edificios. Pin, referencias y ruta
   a pie son los mismos del SVG. Con `cooperativeGestures` el mapa no se roba el scroll de la página: en el teléfono se
   mueve con dos dedos y en la compu se acerca con Ctrl/⌘ + rueda. Si falla (sin WebGL, sin red, CDN caído) se queda el
   póster, que ya es un enlace a «Cómo llegar». */
(function () {
  const enlace = document.querySelector('.pie-mapa__enlace');
  if (!enlace || window.__mapaPie) return;
  window.__mapaPie = true;

  const CLINICA = [-99.1890269, 19.3580013];
  const REFS = [
    ['METRO BARRANCA DEL MUERTO', [-99.18926, 19.36155]],
    ['PLAZA INN', [-99.18727, 19.35223]],
    ['ALTAVISTA', [-99.18974, 19.34888]],
    ['SAN ÁNGEL', [-99.19241, 19.34464]],
  ];
  const RUTA = [[-99.189188, 19.361545], [-99.189192, 19.361514], [-99.189305, 19.360622], [-99.189348, 19.360269],
    [-99.18927, 19.360328], [-99.188611, 19.360149], [-99.188788, 19.358649], [-99.188861, 19.357985], CLINICA];
  // Los mismos colores del SVG (index.html, #mapaBase).
  const C = { tierra: '#F2F2ED', parque: '#E1E5DA', agua: '#DDE3DF', mayor: '#C9CAC3', menor: '#D6D7CF' };
  const grosor = (pares) => ['interpolate', ['exponential', 1.5], ['zoom'], ...pares.flat()];
  const ANCHO_MAYOR = grosor([[11, 1.2], [13, 2.6], [15, 5.5], [17, 11], [19, 26]]);
  const ANCHO_MENOR = grosor([[12, 0.3], [14, 0.9], [15, 2], [17, 5], [19, 12]]);
  const QUEDAN = /^(background|park|landcover_wood|water|waterway|highway_minor|highway_major_(inner|subtle)|highway_motorway_(inner|subtle|bridge_inner)|tunnel_motorway_inner)$/;

  function recolorear(estilo) {
    estilo.layers = estilo.layers.filter((l) => QUEDAN.test(l.id));
    for (const l of estilo.layers) {
      const p = (l.paint = {});
      if (l.id === 'background') p['background-color'] = C.tierra;
      else if (l.id === 'park' || l.id === 'landcover_wood') { p['fill-color'] = C.parque; p['fill-outline-color'] = '#D2D6CA'; }
      else if (l.id === 'water') p['fill-color'] = C.agua;
      else if (l.id === 'waterway') { p['line-color'] = C.agua; p['line-width'] = 1.5; }
      else if (l.id === 'highway_minor') { l.minzoom = 15; p['line-color'] = C.menor; p['line-width'] = ANCHO_MENOR; p['line-opacity'] = 0.8; } // la trama fina, ya de cerca
      else { p['line-color'] = C.mayor; p['line-width'] = ANCHO_MAYOR; }
    }
    delete estilo.glyphs; delete estilo.sprite; // sin etiquetas del estilo: no hacen falta letras ni íconos
    return estilo;
  }

  function cargar(url, tipo) {
    return new Promise((ok, mal) => {
      const el = document.createElement(tipo === 'css' ? 'link' : 'script');
      if (tipo === 'css') { el.rel = 'stylesheet'; el.href = url; } else { el.src = url; el.async = true; }
      el.onload = ok; el.onerror = mal;
      document.head.appendChild(el);
    });
  }

  function marca(clase, html) {
    const el = document.createElement('div');
    el.className = clase;
    el.innerHTML = html;
    return el;
  }

  async function iniciar() {
    const base = 'https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/4.7.1/';
    try {
      const [, , estilo] = await Promise.all([
        cargar(base + 'maplibre-gl.min.css', 'css'),
        cargar(base + 'maplibre-gl.min.js', 'js'),
        fetch('https://tiles.openfreemap.org/styles/positron').then((r) => r.json()),
      ]);
      const lienzo = document.createElement('div');
      lienzo.className = 'pie-mapa__lienzo';
      enlace.appendChild(lienzo);
      const angosto = matchMedia('(max-width:1000px)').matches;
      const menosMovimiento = matchMedia('(prefers-reduced-motion: reduce)').matches;
      const map = new maplibregl.Map({
        container: lienzo,
        style: recolorear(estilo),
        bounds: [[-99.1935, 19.3440], [-99.1855, 19.3625]],
        // En compu la tarjeta tapa el tercio izquierdo: el encuadre se corre a la derecha.
        fitBoundsOptions: { padding: angosto ? { top: 44, bottom: 22, left: 24, right: 120 } : { top: 60, bottom: 30, left: 360, right: 260 } },
        minZoom: 11, maxZoom: 18.5,
        attributionControl: false,
        cooperativeGestures: true,
        dragRotate: false, pitchWithRotate: false, touchPitch: false,
        fadeDuration: menosMovimiento ? 0 : 200,
        locale: {
          'CooperativeGesturesHandler.WindowsHelpText': 'Usa Ctrl + rueda para acercar el mapa',
          'CooperativeGesturesHandler.MacHelpText': 'Usa ⌘ + rueda para acercar el mapa',
          'CooperativeGesturesHandler.MobileHelpText': 'Usa dos dedos para mover el mapa',
          'NavigationControl.ZoomIn': 'Acercar', 'NavigationControl.ZoomOut': 'Alejar',
          'AttributionControl.ToggleAttribution': 'Créditos del mapa',
        },
      });
      map.touchZoomRotate.disableRotation();
      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), angosto ? 'top-left' : 'top-right');
      // El crédito (OpenFreeMap, OpenMapTiles, OpenStreetMap) lo trae el estilo; va cerrado en una «i».
      map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');

      map.on('load', () => {
        map.addSource('ruta', { type: 'geojson', data: { type: 'Feature', geometry: { type: 'LineString', coordinates: RUTA } } });
        map.addLayer({ id: 'ruta', type: 'line', source: 'ruta', layout: { 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': '#262626', 'line-width': 2, 'line-dasharray': [0.1, 2.6] } });
        for (const [nombre, lugar] of REFS) {
          new maplibregl.Marker({ element: marca('pie-mapa__ref', `<span class="pie-mapa__punto"></span><span>${nombre}</span>`), anchor: 'left', offset: [-8, 0] })
            .setLngLat(lugar).addTo(map);
        }
        new maplibregl.Marker({
          element: marca('pie-mapa__pin', '<svg viewBox="-28 -64 56 66" aria-hidden="true"><path d="M0 0C-9 -17 -26 -29 -26 -36A26 26 0 1 1 26 -36C26 -29 9 -17 0 0z"/></svg><img src="images/web/met-positivo-03.webp" alt=""><span>MET CLINIC</span>'),
          anchor: 'bottom-left', offset: [angosto ? -17 : -22, 0],
        }).setLngLat(CLINICA).addTo(map);
      });
      // El póster se va cuando el mapa ya pintó: así no hay un cuadro en blanco.
      map.once('idle', () => {
        const cred = lienzo.querySelector('.maplibregl-ctrl-attrib');
        if (cred) cred.classList.remove('maplibregl-compact-show');
        enlace.classList.add('pie-mapa--vivo');
        enlace.removeAttribute('href');
        enlace.setAttribute('role', 'region');
        enlace.setAttribute('aria-label', 'Mapa de MET Clinic, Guty Cárdenas 65, Guadalupe Inn');
      });
    } catch (e) {
      /* sin WebGL o sin red: se queda el póster, que ya es un enlace a «Cómo llegar» */
    }
  }
  iniciar();
})();
