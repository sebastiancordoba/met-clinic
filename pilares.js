// pilares.js — comportamiento compartido de las páginas de pilar
// Hamburguesa móvil + reveal al hacer scroll.

// Hamburguesa
const hamburger = document.getElementById('hamburger');
const drawer = document.getElementById('navDrawer');
if (hamburger && drawer) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    drawer.classList.toggle('open');
  });
  drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    hamburger.classList.remove('open');
    drawer.classList.remove('open');
  }));
}

// Reveal
const obs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));


/* La barra de contacto del teléfono (cuándo se ve) vive en pie.js, igual en todas las páginas. */

// Tecnología (tecnologia.html): el índice de chips resalta el aparato en pantalla y se desliza para que el chip activo
// se vea; al llegar desde el carrusel de la portada con #ancla, baja con scroll suave a ese aparato.
(function () {
  const indice = document.querySelector('.tec-indice');
  if (!indice) return;
  const chips = new Map([...indice.querySelectorAll('.tec-indice__chip')].map(c => [c.getAttribute('href').slice(1), c]));
  const fila = indice.querySelector('.tec-indice__fila');
  const secciones = [...document.querySelectorAll('.tec-aparato')];
  let actual = null;
  function marcar(id) {
    if (id === actual) return;
    actual = id;
    chips.forEach((c, k) => { c.classList.toggle('activo', k === id); if (k === id) c.setAttribute('aria-current', 'true'); else c.removeAttribute('aria-current'); });
    // El chip activo toma el color de marca (--marca-texto, ya en AA) del aparato en pantalla.
    const sec = document.getElementById(id);
    if (sec) indice.style.setProperty('--chip-activo', getComputedStyle(sec).getPropertyValue('--marca-texto').trim());
    const c = chips.get(id);
    if (c && fila) fila.scrollTo({ left: c.offsetLeft - fila.clientWidth / 2 + c.offsetWidth / 2 });
  }
  function revisar() {
    const linea = indice.getBoundingClientRect().bottom + window.innerHeight * 0.3;
    let id = null;
    for (const s of secciones) if (s.getBoundingClientRect().top <= linea) id = s.id;
    if (id) marcar(id); else { actual = null; chips.forEach(c => { c.classList.remove('activo'); c.removeAttribute('aria-current'); }); }
  }
  let pend = false;
  window.addEventListener('scroll', () => { if (!pend) { pend = true; requestAnimationFrame(() => { pend = false; revisar(); }); } }, { passive: true });
  revisar();
  const suave = !matchMedia('(prefers-reduced-motion: reduce)').matches;
  chips.forEach((c, id) => c.addEventListener('click', (e) => {
    const s = document.getElementById(id);
    if (!s) return;
    e.preventDefault();
    s.scrollIntoView({ behavior: suave ? 'smooth' : 'auto', block: 'start' });
    history.replaceState(null, '', '#' + id);
  }));
  // Llegada con #ancla: arranca arriba y baja suave (el navegador saltaría de golpe).
  const destino = location.hash && document.getElementById(location.hash.slice(1));
  if (destino && destino.classList.contains('tec-aparato') && suave) {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    window.scrollTo(0, 0);
    window.addEventListener('load', () => setTimeout(() => destino.scrollIntoView({ behavior: 'smooth', block: 'start' }), 350));
  }
})();
