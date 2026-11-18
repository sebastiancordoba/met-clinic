// ── Nav scroll + dark-section detection ──────────
const nav = document.getElementById('site-nav');
const darkSections = document.querySelectorAll('.is-dark');

function getDarkRanges() {
  // El rango arranca una altura de nav antes: así el nav ya va oscuro cuando la
  // sección oscura le llega por debajo — incluye el hero, que empieza en y=68.
  return Array.from(darkSections).map(el => ({
    top: el.offsetTop - nav.offsetHeight, bottom: el.offsetTop + el.offsetHeight
  }));
}
let darkRanges = getDarkRanges();
window.addEventListener('resize', () => { darkRanges = getDarkRanges(); updateNav(); });

// Al entrar, la barra va transparente sobre el video (.nav--video, ya viene en el HTML
// para que no parpadee). Al bajar 48 px, o con el menú del teléfono abierto, vuelve al crema.
const navSobreVideo = !!document.querySelector('.hero');
function updateNav() {
  const y = window.scrollY;
  const mid = y + nav.offsetHeight / 2;
  nav.classList.toggle('nav--video', navSobreVideo && y < 48 && !document.querySelector('.nav__drawer.open'));
  nav.classList.toggle('scrolled', y > 60);
  nav.classList.toggle('dark-section', darkRanges.some(r => mid >= r.top && mid <= r.bottom));
}
window.addEventListener('scroll', updateNav, { passive: true });
updateNav();

// ── Hero entrance ─────────────────────────────────
// Colgaba de 'load', que espera a TODAS las imágenes de la página: el hero se
// quedaba en blanco varios segundos. Esperaba también a que se decodificara el
// logo grande; ya no está —con el video, estorbaba—, así que el texto entra
// en cuanto hay DOM. Su fondo es el póster, que ya trae el CSS.
(() => {
  const hero = document.querySelector('.hero');
  if (hero) requestAnimationFrame(() => hero.classList.add('hero--loaded'));
})();

// ── Scroll reveal ─────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// ── Counter animation ─────────────────────────────
function runCounter(el) {
  // El HTML ya trae la cifra final (sin JS se lee bien); con «reducir movimiento» no se anima.
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    el.textContent = parseInt(el.dataset.count).toLocaleString('es-MX') + (el.dataset.suffix || '');
    return;
  }
  const target = parseInt(el.dataset.count);
  const suffix = el.dataset.suffix || '';
  const dur = 1600;
  const t0 = performance.now();
  const tick = (now) => {
    const p = Math.min((now - t0) / dur, 1);
    const v = Math.round((1 - Math.pow(1 - p, 3)) * target);
    el.textContent = v.toLocaleString('es-MX') + suffix;
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
const cObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (!e.isIntersecting || !e.target.dataset.count) return;
    runCounter(e.target);
    cObs.unobserve(e.target);
  });
}, { threshold: 0.5 });
document.querySelectorAll('[data-count]').forEach(el => cObs.observe(el));

// ── Services carousel ────────────────────────────
// Desktop: center card = 10/12, peek 1/12 each side
// Mobile:  1 card full width
(function () {
  const el    = document.getElementById('svcCarousel');
  if (!el) return; // #servicios ahora usa grid de pilares (sin carrusel)
  const track = el.querySelector('.servicios-track');
  const orig  = [...track.children]; // 6 real cards
  const N     = orig.length;

  const pre1 = orig[N - 2].cloneNode(true);
  const pre2 = orig[N - 1].cloneNode(true);
  const app1 = orig[0].cloneNode(true);
  const app2 = orig[1].cloneNode(true);
  const app3 = orig[2].cloneNode(true);
  [pre1, pre2, app1, app2, app3].forEach(c => c.setAttribute('aria-hidden', 'true'));
  track.insertBefore(pre2, orig[0]);
  track.insertBefore(pre1, pre2);
  track.appendChild(app1);
  track.appendChild(app2);
  track.appendChild(app3);

  // all (11): [pre1, pre2, c0..c5, app1, app2, app3]
  const all = [...track.children];

  let cur  = 2;
  let busy = false;

  function isDesktop() { return window.innerWidth > 640; }
  // Desktop: card width = 10/12 of container, centered (1/12 peek each side)
  // Mobile:  card width = full container
  function cw() {
    return isDesktop() ? el.offsetWidth * (10 / 12) : el.offsetWidth;
  }

  function render(animate) {
    const w = cw();
    const C = el.offsetWidth;
    // Center the active card: offset = space left on each side
    const offset = isDesktop() ? (C - w) / 2 : 0;
    all.forEach(c => { c.style.width = w + 'px'; });
    track.style.transition = animate
      ? 'transform 0.7s cubic-bezier(0.25,0.46,0.45,0.94)'
      : 'none';
    track.style.transform = `translateX(${-cur * w + offset}px)`;
    all.forEach((c, i) => {
      c.classList.remove('s-active', 's-bright', 's-side', 's-hidden');
      const d = Math.abs(i - cur);
      if      (d === 0)                    c.classList.add('s-active');
      else if (d === 1 && isDesktop())     c.classList.add('s-side');
      else                                 c.classList.add('s-hidden');
    });
  }

  function next() {
    if (busy) return;
    busy = true;
    cur++;
    render(true);
    setTimeout(() => {
      // Snap: after showing app1 (index N+2 = 8) as center, jump to real c0 (index 2)
      if (cur === N + 2) { cur = 2; render(false); }
      busy = false;
    }, 720);
  }

  render(false);
  setInterval(next, 4000);
  window.addEventListener('resize', () => render(false));
})();

// ── Smooth anchors ────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const t = document.querySelector(a.getAttribute('href'));
    if (t) {
      e.preventDefault();
      const top = t.getBoundingClientRect().top + window.scrollY - 68;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// ── Hamburger menu ────────────────────────────────
const hamburger = document.getElementById('hamburger');
const drawer = document.getElementById('nav-drawer');
hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('open');
  drawer.classList.toggle('open');
  updateNav();
});
document.querySelectorAll('.drawer-link').forEach(a => {
  a.addEventListener('click', () => {
    hamburger.classList.remove('open');
    drawer.classList.remove('open');
  });
});

// ── Especialistas carousel (vertical cards, 4/3/2 por vista) ──
(function () {
  const track = document.getElementById('espTrack');
  if (!track) return;
  const cards = [...track.children].filter(c => c.classList.contains('esp-card')); // lista maestra; sin las del <template>
  const solo = cards.length === 1;
  track.closest('.esp-carousel').classList.toggle('esp-solo', solo);
  const prev = document.getElementById('espPrev');
  const next = document.getElementById('espNext');
  const dotsWrap = document.getElementById('espDots');
  const controls = track.closest('.esp-carousel').querySelector('.esp-controls');
  let idx = 0, pages = [], perView = 0;

  function calcPer() {
    if (solo) return 1;
    const w = window.innerWidth;
    if (w <= 640) return 2;
    if (w <= 1000) return 3;
    return 4;
  }

  function build() {
    const per = calcPer();
    const firstCard = idx * (perView || per);  // recuerda la card visible al reagrupar
    perView = per;
    track.innerHTML = '';
    dotsWrap.innerHTML = '';
    pages = [];
    for (let i = 0; i < cards.length; i += per) {
      const page = document.createElement('div');
      page.className = 'esp-page';
      page.style.gridTemplateColumns = `repeat(${per}, 1fr)`;
      cards.slice(i, i + per).forEach(c => page.appendChild(c));
      track.appendChild(page);
      pages.push(page);
    }
    pages.forEach((_, i) => {
      const d = document.createElement('button');
      d.className = 'esp-dot';
      d.setAttribute('aria-label', 'Página ' + (i + 1));
      d.addEventListener('click', () => go(i));
      dotsWrap.appendChild(d);
    });
    controls.classList.toggle('is-hidden', pages.length <= 1);
    idx = Math.max(0, Math.min(Math.floor(firstCard / per), pages.length - 1));
    go(idx, true);
  }

  function go(i, instant) {
    idx = Math.max(0, Math.min(pages.length - 1, i));
    if (instant) track.style.transition = 'none';
    track.style.transform = `translateX(${-idx * 100}%)`;
    if (instant) { void track.offsetWidth; track.style.transition = ''; }
    [...dotsWrap.children].forEach((d, j) => d.classList.toggle('is-active', j === idx));
    prev.disabled = idx === 0;
    next.disabled = idx === pages.length - 1;
  }

  prev.addEventListener('click', () => go(idx - 1));
  next.addEventListener('click', () => go(idx + 1));

  let rt;
  window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(build, 150); });

  build();
})();



/* ── Video del hero ───────────────────────────────────────────────────────
   Se carga a mano y no con autoplay+src en el HTML por tres razones:
   - quien tiene `prefers-reduced-motion` se queda con el póster fijo;
   - quien tiene ahorro de datos (`saveData`) no paga el video de fondo;
   - la primera pintura no compite con el video por la conexión.
   Hay cuatro versiones (ver optimizar-video.sh) y se baja solo una. En el
   teléfono, el recorte vertical (pesa la tercera parte). En lo demás, la que
   se amplíe menos en el recuadro real del hero: en un iPad vertical el
   1080p recortado conserva más detalle que el vertical estirado. AV1 si el
   navegador lo decodifica, H.264 si no.
   Si el navegador bloquea el autoplay, play() rechaza y queda el póster. */
(function () {
  const v = document.querySelector('.hero__media--video video');
  if (!v || !v.dataset.base) return;
  const menosMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ahorro = navigator.connection && navigator.connection.saveData;
  if (menosMovimiento || ahorro) return;
  const caja = v.parentElement.getBoundingClientRect();
  const zoom = (w, h) => Math.max(caja.width / w, caja.height / h);
  const vertical = window.matchMedia('(max-width: 640px)').matches || zoom(720, 1080) < zoom(1920, 1080);
  // En iPhone/iPad siempre H.264 (Sebas 19:23: no corría en su iPhone): iOS solo decodifica AV1 por hardware en los
  // modelos recientes y H.264 lo decodifica cualquiera, con menos batería. AV1 se queda para compu y Android.
  const ios = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const av1 = !ios && v.canPlayType('video/mp4; codecs="av01.0.08M.10"') === 'probably';
  // Velocidad para comparar (24-oct, Sebas: «va muy rápido»): ?video=lento (0.8×, 15 s),
  // ?video=medio (0.9×, 13.4 s) o ?video=<número> para probar otra (0.5–1.5, p. ej. ?video=0.85).
  // Es sobre el archivo, que desde el 30-oct ya viene más lento: 11 tomas en 12 s (optimizar-video.sh).
  const pedida = (location.search.match(/[?&]video=([a-z]+|\d*\.?\d+)/) || [])[1];
  const velocidad = { lento: 0.8, medio: 0.9 }[pedida] || Math.min(1.5, Math.max(0.5, parseFloat(pedida))) || 1;
  const arrancar = () => {
    // Sin cuadro todavía, WebKit pinta el <video> en negro encima del póster (Sebas 23:41, recarga lenta en la tienda):
    // se queda invisible (.sin-cuadro, sin transición) hasta que tiene el primer cuadro, que es el mismo del póster.
    v.classList.add('sin-cuadro');
    const yaHay = () => v.classList.remove('sin-cuadro');
    v.addEventListener('loadeddata', yaHay, { once: true });
    v.addEventListener('playing', yaHay, { once: true });
    v.src = v.dataset.base + (vertical ? '-movil' : '-1080') + (av1 ? '.av1' : '') + '.mp4';
    if (velocidad !== 1) v.defaultPlaybackRate = v.playbackRate = velocidad;
    // Si el archivo no se puede decodificar (p. ej. AV1 que el navegador dijo aceptar), se cae a H.264.
    v.addEventListener('error', () => {
      if (v.src.indexOf('av1') === -1) return;
      v.src = v.src.replace('.av1.mp4', '.mp4').replace('av1.mp4', '.mp4');
      intentar();
    }, { once: true });
    intentar();
    // Fuera de la pantalla se pausa (4-nov, rendimiento): decodificar 1080p mientras se lee el resto
    // de la página le quitaba cuadros al scroll y batería al teléfono. Al volver, sigue donde iba.
    let visible = true;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(([e]) => {
        visible = e.isIntersecting;
        if (visible) intentar(); else v.pause();
      }).observe(v.parentElement);
    }
    // iOS bloquea el autoplay con «Modo de bajo consumo» y a veces tras volver a la pestaña: se reintenta al primer
    // toque o desplazamiento y al volver a ver la página. Si sigue bloqueado, queda el póster fijo (fondo del div).
    const otraVez = () => { if (visible && v.paused) intentar(); };
    ['touchstart', 'pointerdown', 'scroll', 'keydown'].forEach((t) => window.addEventListener(t, otraVez, { passive: true }));
    document.addEventListener('visibilitychange', () => { if (!document.hidden) otraVez(); });
    window.addEventListener('pageshow', otraVez);
  };
  // iOS exige que esté silenciado al momento de play(): atributo y propiedad, siempre antes de cada intento.
  function intentar() {
    v.muted = true; v.defaultMuted = true; v.setAttribute('muted', ''); v.playsInline = true; v.setAttribute('playsinline', '');
    const pr = v.play();
    if (pr && pr.catch) pr.catch(() => {});
  }
  if (document.readyState === 'complete') arrancar();
  else window.addEventListener('load', arrancar, { once: true });
})();


/* La barra de contacto del teléfono (cuándo se ve) vive en pie.js, igual en todas las páginas. */


/* «Cómo llegar» (Apple Maps en iPhone/iPad/Mac) vive en pie.js (4), igual en todas las páginas. */


/* ── Equipo en el teléfono: puntos del carrusel ─────────────────────────
   En el teléfono .equipo-grid es una fila que se desliza (CSS); aquí solo los
   puntos que dicen en qué tarjeta vas. Son decorativos (aria-hidden). */
(function () {
  const fila = document.querySelector('.equipo-grid');
  const puntos = document.querySelector('.equipo-puntos');
  if (!fila || !puntos) return;
  const tarjetas = [...fila.children];
  puntos.innerHTML = tarjetas.map(() => '<span></span>').join('');
  const marcar = () => {
    const paso = tarjetas.length > 1 ? tarjetas[1].offsetLeft - tarjetas[0].offsetLeft : 1;
    const i = Math.min(tarjetas.length - 1, Math.round(fila.scrollLeft / paso));
    [...puntos.children].forEach((p, k) => p.classList.toggle('activo', k === i));
  };
  fila.addEventListener('scroll', marcar, { passive: true });
  window.addEventListener('resize', marcar);
  marcar();
})();


/* ── Carrusel de aparatos (#tecnologia) ────────────────────────────────
   Las flechas avanzan casi una vista; se apagan en las orillas. En el teléfono
   no hay flechas: se desliza con el dedo (scroll-snap). */
(function () {
  const fila = document.querySelector('.aparatos__fila');
  if (!fila) return;
  const flechas = document.querySelectorAll('.aparatos__flecha');
  const actualizar = () => {
    const max = fila.scrollWidth - fila.clientWidth - 2;
    flechas.forEach((b) => { b.disabled = b.dataset.dir === '-1' ? fila.scrollLeft <= 2 : fila.scrollLeft >= max; });
  };
  flechas.forEach((b) => b.addEventListener('click', () => {
    fila.scrollBy({ left: Number(b.dataset.dir) * fila.clientWidth * 0.9, behavior: 'smooth' });
  }));
  fila.addEventListener('scroll', actualizar, { passive: true });
  window.addEventListener('resize', actualizar);
  actualizar();
})();


/* ── Agenda de Doctoralia dentro de #contacto ───────────────────────────
   El widget oficial (platform.docplanner.com) muestra los horarios libres de
   la doctora y agenda sin salir de la página. Se inserta al pedirlo, no antes:
   carga analítica de terceros y pesa. */
(function () {
  const btn = document.getElementById('agendaAbrir');
  const caja = document.getElementById('agendaCaja');
  if (!btn || !caja) return;
  btn.addEventListener('click', () => {
    const abierta = !caja.hidden;
    caja.hidden = abierta;
    btn.setAttribute('aria-expanded', String(!abierta));
    btn.textContent = abierta ? 'Ver horarios disponibles aquí' : 'Ocultar horarios';
    if (abierta || caja.dataset.cargada) return;
    caja.dataset.cargada = '1';
    caja.innerHTML = '<a id="zl-url" class="zl-url" href="https://www.doctoralia.com.mx/melina-trujillo-quiroz/ginecologo/ciudad-de-mexico"'
      + ' rel="nofollow" data-zlw-doctor="melina-trujillo-quiroz" data-zlw-type="big_with_calendar" data-zlw-opinion="false"'
      + ' data-zlw-hide-branding="true" data-zlw-saas-only="false" data-zlw-a11y-title="Agenda de citas de la Dra. Melina Trujillo">'
      + 'Agenda de la Dra. Melina Trujillo en Doctoralia</a>';
    const s = document.createElement('script');
    s.id = 'zl-widget-s';
    s.src = 'https://platform.docplanner.com/js/widget.js';
    document.body.appendChild(s);
  });
})();
