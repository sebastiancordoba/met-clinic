// pie.js — lo que comparten todas las páginas (24-oct-2026). El mapa chico y «Pregúntale a tu IA» del pie se
// quitaron el 30-oct (Sebas).
//
// 1. Un solo «Agendar consulta» a la vista (24-oct, Sebas: «dos botones para lo mismo»).
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

// 2. Barra de desplazamiento flotante (24-oct, Sebas: «ocupa toda una franja vertical»).
//    Solo donde la barra del sistema ocupa ancho (Chrome, Edge y Firefox en Windows; macOS con
//    «mostrar barras siempre»): ahí se esconde la nativa y flota un pulgar delgado que aparece al
//    desplazar o al acercar el ratón al borde derecho, y se va 1 s después. Donde la barra ya es
//    flotante (macOS, iOS, Android) no se toca nada. Rueda, teclado y touchpad siguen siendo el
//    scroll nativo; el pulgar se arrastra y un clic en el carril avanza una pantalla.
(function () {
  const raiz = document.documentElement;
  if (window.innerWidth - raiz.clientWidth <= 0 || matchMedia('(pointer: coarse)').matches) return;
  raiz.classList.add('barra-propia');
  const carril = document.createElement('div');
  carril.className = 'barra-scroll';
  carril.setAttribute('aria-hidden', 'true');
  const pulgar = document.createElement('div');
  pulgar.className = 'barra-scroll__pulgar';
  carril.appendChild(pulgar);
  document.body.appendChild(carril);

  let espera, arrastre = null, pendiente = false;
  const medir = () => {
    pendiente = false;
    const vh = innerHeight, total = raiz.scrollHeight;
    carril.hidden = total <= vh + 1;
    if (carril.hidden) return;
    const alto = Math.max(40, vh * vh / total);
    pulgar.style.height = alto + 'px';
    pulgar.style.transform = 'translateY(' + (scrollY / (total - vh)) * (vh - alto) + 'px)';
  };
  const pedir = () => { if (!pendiente) { pendiente = true; requestAnimationFrame(medir); } };
  const mostrar = () => {
    carril.classList.add('visible');
    clearTimeout(espera);
    espera = setTimeout(() => {
      if (!arrastre && !carril.matches(':hover')) carril.classList.remove('visible');
    }, 1000);
  };

  addEventListener('scroll', () => { pedir(); mostrar(); }, { passive: true });
  addEventListener('resize', pedir);
  if ('ResizeObserver' in window) new ResizeObserver(pedir).observe(document.body);
  addEventListener('mousemove', (e) => { if (e.clientX >= innerWidth - 24) mostrar(); }, { passive: true });
  carril.addEventListener('mouseleave', mostrar);

  pulgar.addEventListener('pointerdown', (e) => {
    e.preventDefault();
    pulgar.setPointerCapture(e.pointerId);
    arrastre = { y: e.clientY, desde: scrollY };
    carril.classList.add('arrastrando');
  });
  pulgar.addEventListener('pointermove', (e) => {
    if (!arrastre) return;
    const vh = innerHeight, total = raiz.scrollHeight;
    const y = arrastre.desde + (e.clientY - arrastre.y) * (total - vh) / (vh - pulgar.offsetHeight);
    window.scrollTo({ top: y, behavior: 'instant' });
  });
  const soltar = () => { arrastre = null; carril.classList.remove('arrastrando'); mostrar(); };
  pulgar.addEventListener('pointerup', soltar);
  pulgar.addEventListener('pointercancel', soltar);
  carril.addEventListener('pointerdown', (e) => {
    if (e.target !== carril) return;
    const arriba = e.clientY < pulgar.getBoundingClientRect().top;
    window.scrollBy({ top: (arriba ? -1 : 1) * innerHeight * 0.9, behavior: 'smooth' });
  });
  medir();
})();


// 3. Rendimiento (4-nov): mientras la página se desplaza, la barra de arriba lleva .desplazando y el CSS
//    detiene el destello del logo, que de otro modo repinta la barra fija en cada cuadro del scroll.
//    Vuelve a correr 200 ms después de que se detiene el scroll.
(function () {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  let espera = 0;
  addEventListener('scroll', () => {
    if (!espera) nav.classList.add('desplazando');
    clearTimeout(espera);
    espera = setTimeout(() => { espera = 0; nav.classList.remove('desplazando'); }, 200);
  }, { passive: true });
})();


// 4. «Cómo llegar» (4-nov): el mapa del pie (ver generar-mapa.py) y su botón abren la
//    app de mapas del dispositivo: Apple Maps en iPhone/iPad/Mac; en lo demás, el enlace a Google Maps del HTML.
(function () {
  if (!/iPhone|iPad|Macintosh/.test(navigator.userAgent) || /Android/.test(navigator.userAgent)) return;
  document.querySelectorAll('.js-mapa-ir').forEach((a) => {
    a.href = 'https://maps.apple.com/?daddr=19.3580013,-99.1890269&q=MET%20Clinic';
  });
})();


// 5. Mapa del pie interactivo (4-nov, Sebas): mapa-pie.js (MapLibre) se baja solo cuando el pie está a ~400 px de la
//    pantalla o al primer toque/foco sobre el mapa. Mientras, el SVG del pie hace de póster (y de enlace a «Cómo llegar»).
(function () {
  const caja = document.querySelector('.pie-mapa');
  if (!caja) return;
  let pedido = false;
  const pedir = () => {
    if (pedido) return;
    pedido = true;
    const s = document.createElement('script');
    s.src = 'mapa-pie.js';
    s.async = true;
    document.head.appendChild(s);
  };
  caja.addEventListener('pointerdown', pedir, { once: true, passive: true });
  caja.addEventListener('focusin', pedir, { once: true });
  if (!('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); pedir(); } }, { rootMargin: '400px 0px' });
  io.observe(caja);
})();

// 6. Brillo del logo (13-nov, Sebas; igual en la tienda, shopify_tema_met.py). El CSS solo barre cuando el logo
//    lleva .brillando: aquí se pone al pasar el mouse (de inmediato) y solo cada 10–12 s. Entre dos brillos hay al
//    menos 2 s, y cada hover reinicia la cuenta del automático. Se detiene con la pestaña oculta. En teléfono (sin
//    hover) solo el automático. Con «reducir movimiento», nada.
(function () {
  const marcas = document.querySelectorAll('.nav__marca');
  if (!marcas.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const PAUSA = 2000, MIN = 10000, MAX = 12000;
  let ultimo = -Infinity, reloj = 0;
  const programar = () => { clearTimeout(reloj); if (!document.hidden) reloj = setTimeout(brillar, MIN + Math.random() * (MAX - MIN)); };
  function brillar() {
    const ahora = performance.now();
    if (ahora - ultimo >= PAUSA) {
      ultimo = ahora;
      marcas.forEach((m) => { m.classList.remove('brillando'); void m.offsetWidth; m.classList.add('brillando'); });
    }
    programar();
  }
  const conMouse = matchMedia('(hover: hover)').matches;
  marcas.forEach((m) => {
    m.addEventListener('animationend', () => m.classList.remove('brillando'));
    if (conMouse) m.addEventListener('mouseenter', brillar);
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) clearTimeout(reloj); else programar(); });
  reloj = setTimeout(brillar, 2600);
})();
