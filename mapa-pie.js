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
  // Paleta MET (17-nov 19:00, Sebas: «más detallado y que oriente mejor»): crema/gris, avenidas más marcadas, parques
  // salvia, edificios apenas visibles y NOMBRES de avenidas, calles y colonias en gris legible (#515151 sobre crema).
  const C = { tierra: '#F2F2ED', parque: '#DDE3D5', agua: '#D9E1DD', mayor: '#BEBFB7', menor: '#D3D4CC', edificio: '#E8E8E2', texto: '#515151' };
  const grosor = (pares) => ['interpolate', ['exponential', 1.5], ['zoom'], ...pares.flat()];
  const ANCHO_MAYOR = grosor([[11, 1.4], [13, 3], [15, 6.5], [17, 13], [19, 28]]);
  const ANCHO_MENOR = grosor([[12, 0.3], [14, 1], [15, 2.2], [17, 5.5], [19, 12]]);
  const QUEDAN = /^(background|park|landcover_wood|water|waterway|building|highway_minor|highway_major_(inner|subtle)|highway_motorway_(inner|subtle|bridge_inner)|tunnel_motorway_inner|railway_transit|highway-name-(major|minor)|label_other)$/;
  const NOMBRE = ['coalesce', ['get', 'name:es'], ['get', 'name']];

  function recolorear(estilo) {
    estilo.layers = estilo.layers.filter((l) => QUEDAN.test(l.id));
    for (const l of estilo.layers) {
      if (l.type === 'symbol') {
        l.layout['text-field'] = NOMBRE;
        const colonia = l.id === 'label_other';
        if (colonia) { l.layout['text-size'] = 11; l.layout['text-letter-spacing'] = 0.18; l.layout['text-font'] = ['Noto Sans Regular']; l.minzoom = 13.5; }
        else l.layout['text-size'] = l.id === 'highway-name-major' ? 12 : 11;
        l.paint = { 'text-color': colonia ? '#6A6D66' : C.texto, 'text-halo-color': C.tierra, 'text-halo-width': 1.6, 'text-halo-blur': 0.3 };
        continue;
      }
      const p = (l.paint = {});
      if (l.id === 'background') p['background-color'] = C.tierra;
      else if (l.id === 'park' || l.id === 'landcover_wood') { p['fill-color'] = C.parque; p['fill-outline-color'] = '#CBD2C2'; }
      else if (l.id === 'water') p['fill-color'] = C.agua;
      else if (l.id === 'waterway') { p['line-color'] = C.agua; p['line-width'] = 1.5; }
      else if (l.id === 'building') { l.minzoom = 15; p['fill-color'] = C.edificio; p['fill-outline-color'] = '#DEDED7'; }
      else if (l.id === 'railway_transit') { l.minzoom = 13; p['line-color'] = '#A9AAA2'; p['line-width'] = 1.6; p['line-dasharray'] = [3, 2]; }
      else if (l.id === 'highway_minor') { l.minzoom = 13.5; p['line-color'] = C.menor; p['line-width'] = ANCHO_MENOR; }
      else { p['line-color'] = C.mayor; p['line-width'] = ANCHO_MAYOR; }
    }
    // Estaciones de metro y Metrobús de OpenStreetMap: punto salvia con su nombre.
    // El metro lo pinta nuestro marcador «M» (abajo); de las teselas, el Metrobús. El nombre del metro sí sale de las teselas.
    const esEstacion = ['all', ['==', ['get', 'class'], 'bus'], ['==', ['get', 'subclass'], 'bus_station']];
    const esMetro = ['==', ['get', 'class'], 'railway'];
    estilo.layers.push(
      { id: 'met-estacion', type: 'circle', source: 'openmaptiles', 'source-layer': 'poi', minzoom: 14, filter: esEstacion,
        paint: { 'circle-radius': 5, 'circle-color': '#82867F', 'circle-stroke-color': C.tierra, 'circle-stroke-width': 2 } },
      { id: 'met-estacion-nombre', type: 'symbol', source: 'openmaptiles', 'source-layer': 'poi', minzoom: 14, filter: ['any', esEstacion, esMetro],
        layout: { 'text-field': NOMBRE, 'text-font': ['Noto Sans Regular'], 'text-size': 11, 'text-offset': [0, 1.1], 'text-anchor': 'top', 'text-max-width': 8 },
        paint: { 'text-color': '#3F423D', 'text-halo-color': C.tierra, 'text-halo-width': 1.6 } });
    delete estilo.sprite; // sin íconos del estilo; las letras (glyphs) sí se quedan para los nombres
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
        // Un nivel más lejos que antes (Sebas 19:00): se ven Revolución, Barranca del Muerto e Insurgentes con su nombre.
        center: [-99.1872, 19.3594], zoom: angosto ? 14.6 : 14.8,
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
      // Abajo a la izquierda: arriba quedan los nombres del metro (a la izquierda) y de la clínica (a la derecha).
      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-left');
      // El crédito (OpenFreeMap, OpenMapTiles, OpenStreetMap) lo trae el estilo; va cerrado en una «i».
      map.addControl(new maplibregl.AttributionControl({ compact: true }), 'top-right');
      // «Ver más grande»: abre el mapa completo en Apple Maps (iPhone, iPad, Mac) o en Google Maps.
      const apple = /iPhone|iPad|Macintosh/.test(navigator.userAgent);
      const grande = document.createElement('a');
      grande.className = 'pie-mapa__grande'; grande.target = '_blank'; grande.rel = 'noopener';
      grande.href = apple ? 'https://maps.apple.com/?q=MET+Clinic&ll=19.3580013,-99.1890269&z=16'
        : 'https://www.google.com/maps/search/?api=1&query=MET+Clinic%2C+Guty+C%C3%A1rdenas+65%2C+Guadalupe+Inn%2C+01020+CDMX';
      grande.innerHTML = 'Ver más grande <span aria-hidden="true">↗</span>';
      map.addControl({ onAdd: () => { const c = document.createElement('div'); c.className = 'maplibregl-ctrl'; c.appendChild(grande); return c; }, onRemove: () => {} }, 'bottom-right');

      map.on('load', () => {
        map.addSource('ruta', { type: 'geojson', data: { type: 'Feature', geometry: { type: 'LineString', coordinates: RUTA } } });
        map.addLayer({ id: 'ruta', type: 'line', source: 'ruta', layout: { 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': '#262626', 'line-width': 2, 'line-dasharray': [0.1, 2.6] } });
        // Metro Barranca del Muerto (Línea 7), con su ícono; el Metrobús y otras estaciones salen de las teselas.
        new maplibregl.Marker({ element: marca('pie-mapa__metro', '<span class="pie-mapa__m" title="Metro Barranca del Muerto · Línea 7">M</span>'), anchor: 'center' })
          .setLngLat(REFS[0][1]).addTo(map);
        new maplibregl.Marker({
          element: marca('pie-mapa__pin', '<i class="pie-mapa__halo"></i><svg viewBox="-28 -64 56 66" aria-hidden="true"><path d="M0 0C-9 -17 -26 -29 -26 -36A26 26 0 1 1 26 -36C26 -29 9 -17 0 0z"/></svg><img src="images/web/met-positivo-03.webp" alt=""><span><b>MET Clinic</b> · Guty Cárdenas 65</span>'),
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
