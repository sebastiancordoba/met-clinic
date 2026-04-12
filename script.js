/* MET Clinic — Script */

(function () {
  'use strict';

  // ── THEME TOGGLE ──
  const html = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  let theme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  html.setAttribute('data-theme', theme);

  function updateToggleIcon(t) {
    if (!toggle) return;
    toggle.innerHTML = t === 'dark'
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    toggle.setAttribute('aria-label', 'Cambiar a modo ' + (t === 'dark' ? 'claro' : 'oscuro'));
  }

  updateToggleIcon(theme);

  if (toggle) {
    toggle.addEventListener('click', () => {
      theme = theme === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', theme);
      updateToggleIcon(theme);
    });
  }

  // ── NAV SCROLL BEHAVIOR ──
  const nav = document.getElementById('nav');
  let lastScrollY = 0;

  function handleNavScroll() {
    const scrollY = window.scrollY;
    if (scrollY > 20) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
    lastScrollY = scrollY;
  }

  window.addEventListener('scroll', handleNavScroll, { passive: true });
  handleNavScroll();

  // ── MOBILE MENU ──
  const burger = document.getElementById('burger');
  const mobileMenu = document.getElementById('mobile-menu');

  if (burger && mobileMenu) {
    burger.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      burger.setAttribute('aria-expanded', isOpen);
      burger.setAttribute('aria-label', isOpen ? 'Cerrar menú' : 'Abrir menú');

      // Animate burger
      const spans = burger.querySelectorAll('span');
      if (isOpen) {
        spans[0].style.transform = 'translateY(6.5px) rotate(45deg)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'translateY(-6.5px) rotate(-45deg)';
      } else {
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      }
    });

    // Close mobile menu on link click
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        const spans = burger.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      });
    });
  }

  // ── SMOOTH SCROLL FOR NAV LINKS ──
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── SCROLL REVEAL ANIMATIONS ──
  function addRevealClasses() {
    const elements = document.querySelectorAll([
      '.section-header',
      '.service-card',
      '.doctora__visual',
      '.doctora__content',
      '.opinion-card',
      '.price-card',
      '.contact__info',
      '.contact__map',
      '.hero__stats .stat',
    ].join(','));

    elements.forEach((el, i) => {
      el.classList.add('reveal');
      el.style.transitionDelay = (i % 4) * 80 + 'ms';
    });
  }

  function initIntersectionObserver() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // Respect reduced motion
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    addRevealClasses();
    initIntersectionObserver();
  }

  // ── ACTIVE NAV LINK ──
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav__links a[href^="#"]');

  function setActiveLink() {
    const scrollY = window.scrollY + 120;
    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');
      const link = document.querySelector(`.nav__links a[href="#${id}"]`);
      if (link) {
        if (scrollY >= top && scrollY < top + height) {
          navLinks.forEach(l => l.style.color = '');
          link.style.color = 'var(--color-primary)';
        }
      }
    });
  }

  window.addEventListener('scroll', setActiveLink, { passive: true });

  // ── STAT NUMBER COUNTER ANIMATION ──
  function animateCounter(el, target, duration = 1200) {
    let start = null;
    const isDecimal = target.toString().includes('.');
    const num = parseFloat(target);
    const suffix = target.toString().replace(num.toString(), '');

    function step(timestamp) {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      const current = Math.floor(eased * num);
      el.textContent = current.toLocaleString('es-MX') + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }

  function initCounters() {
    const stats = document.querySelectorAll('.stat__num');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const text = el.textContent;
          const numMatch = text.match(/[\d,]+/);
          if (numMatch) {
            const raw = parseInt(numMatch[0].replace(/,/g, ''), 10);
            const suffix = text.replace(numMatch[0], '');
            animateCounter(el, text.includes('+') ? raw + '+' : text.includes('★') ? text : raw + suffix);
          }
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
      stats.forEach(el => observer.observe(el));
    }
  }

  initCounters();

})();
