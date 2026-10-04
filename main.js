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

function updateNav() {
  const y = window.scrollY;
  const mid = y + nav.offsetHeight / 2;
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
  const cards = [...track.children];           // lista maestra (referencias persistentes)
  const prev = document.getElementById('espPrev');
  const next = document.getElementById('espNext');
  const dotsWrap = document.getElementById('espDots');
  const controls = track.closest('.esp-carousel').querySelector('.esp-controls');
  let idx = 0, pages = [], perView = 0;

  function calcPer() {
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
   Hay cuatro versiones (ver optimizar-video.sh) y se baja solo una:
   recorte vertical si la pantalla es alta y angosta, 1080p si no; AV1 si el
   navegador lo decodifica, H.264 si no.
   Si el navegador bloquea el autoplay, play() rechaza y queda el póster. */
(function () {
  const v = document.querySelector('.hero__media--video video');
  if (!v || !v.dataset.base) return;
  const menosMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ahorro = navigator.connection && navigator.connection.saveData;
  if (menosMovimiento || ahorro) return;
  const vertical = window.matchMedia('(max-aspect-ratio: 2/3)').matches;
  const av1 = v.canPlayType('video/mp4; codecs="av01.0.08M.10"') === 'probably';
  const arrancar = () => {
    v.src = v.dataset.base + (vertical ? '-movil' : '-1080') + (av1 ? '.av1' : '') + '.mp4';
    v.play().catch(() => {});
  };
  if (document.readyState === 'complete') arrancar();
  else window.addEventListener('load', arrancar, { once: true });
})();


/* ── Barra de contacto en móvil ──────────────────────────────────────────
   Se esconde cuando #contacto está en pantalla: ahí ya están los mismos dos
   botones en grande y repetirlos abajo solo estorba. */
(function () {
  const barra = document.querySelector('.barra-movil');
  const contacto = document.getElementById('contacto');
  if (!barra || !contacto || !('IntersectionObserver' in window)) return;
  new IntersectionObserver(([e]) => barra.classList.toggle('oculta', e.isIntersecting),
    { threshold: 0.25 }).observe(contacto);
})();
