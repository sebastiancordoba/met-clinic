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
