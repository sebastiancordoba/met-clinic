// ── Nav scroll + dark-section detection ──────────
const nav = document.getElementById('site-nav');
const darkSections = document.querySelectorAll('.is-dark');

function getDarkRanges() {
  return Array.from(darkSections).map(el => ({
    top: el.offsetTop, bottom: el.offsetTop + el.offsetHeight
  }));
}
let darkRanges = getDarkRanges();
window.addEventListener('resize', () => { darkRanges = getDarkRanges(); });

window.addEventListener('scroll', () => {
  const y = window.scrollY;
  const mid = y + nav.offsetHeight / 2;
  nav.classList.toggle('scrolled', y > 60);
  nav.classList.toggle('dark-section', darkRanges.some(r => mid >= r.top && mid <= r.bottom));
}, { passive: true });

// ── Hero entrance ─────────────────────────────────
window.addEventListener('load', () => {
  requestAnimationFrame(() => document.querySelector('.hero').classList.add('hero--loaded'));
});

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
// Desktop: 5 visible (3 bright center + 2 faded sides)
// Mobile:  3 visible (1 bright center + 2 faded sides)
(function () {
  const el    = document.getElementById('svcCarousel');
  const track = el.querySelector('.servicios-track');
  const orig  = [...track.children]; // 6 real cards
  const N     = orig.length;

  // Prepend 2 clones (last 2), append 3 clones (first 3) — enough for both modes
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

  // cur = index of the center card in `all`. Real cards start at index 2.
  let cur  = 2;
  let busy = false;

  function visible() { return window.innerWidth <= 640 ? 1 : 5; }
  function sides()   { return (visible() - 1) / 2; }        // 0 or 2
  function cw()      { return el.offsetWidth / visible(); }

  function render(animate) {
    const w = cw();
    const s = sides();
    all.forEach(c => { c.style.width = w + 'px'; });
    track.style.transition = animate
      ? 'transform 0.7s cubic-bezier(0.25,0.46,0.45,0.94)'
      : 'none';
    track.style.transform = `translateX(${-(cur - s) * w}px)`;
    all.forEach((c, i) => {
      c.classList.remove('s-active', 's-bright', 's-side', 's-hidden');
      const d = Math.abs(i - cur);
      if      (d === 0)          c.classList.add('s-active');
      else if (d === 1 && s >= 1) c.classList.add(s === 2 ? 's-bright' : 's-side');
      else if (d === 2 && s >= 2) c.classList.add('s-side');
      else                       c.classList.add('s-hidden');
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
    if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth' }); }
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

// ── Form submit placeholder ───────────────────────
document.querySelector('form').addEventListener('submit', e => e.preventDefault());
