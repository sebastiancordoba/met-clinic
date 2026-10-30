// pie.js — lo que comparten todas las páginas (24-oct-2026). El mapa chico del pie se quitó el 30-oct (Sebas).
//
// 1. «Pregúntale a tu IA»: los enlaces ya traen la pregunta (ChatGPT, Claude
//    y Perplexity la aceptan en la URL). Gemini no acepta ?q= (probado el
//    24-oct): ahí se copia la pregunta al portapapeles y se avisa.

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

// 2. Un solo «Agendar consulta» a la vista (24-oct, Sebas: «dos botones para lo mismo»).
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

// 3. Barra de desplazamiento flotante (24-oct, Sebas: «ocupa toda una franja vertical»).
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
