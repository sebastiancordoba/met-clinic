/* Burbuja «Pregúntale a la Dra. Melina» (tienda). Aparece al bajar ~40 % de la primera pantalla; con mouse se abre al
   pasar encima, con toque o teclado al presionar; Esc cierra; la ✕ la quita por el resto de la sesión. En la ficha
   agrega «¿Dudas? Pregúntale a la Dra. Melina» bajo «Agregar» y en el teléfono se esconde mientras se ve ese botón. */
(function () {
  var raiz = document.querySelector('.met-burbuja');
  if (!raiz) return;
  var CLAVE = 'met-burbuja-cerrada';
  var boton = raiz.querySelector('.met-burbuja__boton');
  var tarjeta = raiz.querySelector('.met-burbuja__tarjeta');
  var cerrar = raiz.querySelector('.met-burbuja__cerrar');
  var pw = document.querySelector('.page-wrapper');
  var conMouse = window.matchMedia('(hover: hover) and (pointer: fine)');
  var quitada = false;
  try { quitada = sessionStorage.getItem(CLAVE) === '1'; } catch (e) {}
  var forzada = false, tapada = false, timer = 0;

  raiz.hidden = false;
  function y() { return Math.max(window.scrollY || 0, pw ? pw.scrollTop : 0); }
  function pintar() {
    var ver = forzada || (!quitada && y() > window.innerHeight * 0.4);
    raiz.classList.toggle('visible', ver);
    raiz.classList.toggle('tapada', ver && tapada && !abierta());
    if (!ver && abierta()) abrir(false);
  }
  /* Teléfono (Hermes, 17-nov): se esconde mientras bajas y vuelve al subir o al quedarte quieto ~600 ms. */
  var angostoBurbuja = window.matchMedia('(max-width: 640px)');
  var yPrev = 0, quieto = 0;
  function bajando(v) {
    if (!angostoBurbuja.matches || abierta()) { raiz.classList.remove('escondida'); yPrev = v; return; }
    if (v > yPrev + 4) raiz.classList.add('escondida');
    else if (v < yPrev - 4) raiz.classList.remove('escondida');
    yPrev = v;
    clearTimeout(quieto);
    quieto = setTimeout(function () { raiz.classList.remove('escondida'); }, 600);
  }
  var pendiente = false;
  function alDesplazar() { if (pendiente) return; pendiente = true; requestAnimationFrame(function () { pendiente = false; bajando(y()); pintar(); }); }
  if (pw) pw.addEventListener('scroll', alDesplazar, { passive: true });
  window.addEventListener('scroll', alDesplazar, { passive: true });
  window.addEventListener('resize', alDesplazar, { passive: true });

  function abierta() { return !tarjeta.hidden; }
  function abrir(si, foco) {
    clearTimeout(timer);
    tarjeta.hidden = !si;
    boton.setAttribute('aria-expanded', String(si));
    if (si && foco) (tarjeta.querySelector('a') || cerrar).focus();
    if (!si) { forzada = false; pintar(); }
  }
  boton.addEventListener('click', function (ev) {
    /* Con mouse ya se abrió al pasar encima: el clic solo la deja abierta (no la cierra). Con toque o teclado alterna. */
    if (conMouse.matches && ev.detail > 0) { abrir(true); return; }
    abrir(!abierta(), true);
  });
  raiz.addEventListener('mouseenter', function () { if (conMouse.matches) abrir(true); });
  raiz.addEventListener('mouseleave', function () {
    if (!conMouse.matches || raiz.contains(document.activeElement)) return;
    timer = setTimeout(function () { abrir(false); }, 350);
  });
  raiz.addEventListener('focusout', function (ev) { if (!raiz.contains(ev.relatedTarget) && conMouse.matches) abrir(false); });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && abierta()) { abrir(false); if (!quitada || forzada) boton.focus(); }
  });
  document.addEventListener('click', function (ev) {
    if (abierta() && !raiz.contains(ev.target) && !ev.target.closest('.met-dudas')) abrir(false);
  });
  cerrar.addEventListener('click', function () {
    quitada = true;
    try { sessionStorage.setItem(CLAVE, '1'); } catch (e) {}
    abrir(false); forzada = false; pintar();
  });

  /* Ficha de producto: línea bajo «Agregar» que abre la misma tarjeta */
  if (raiz.dataset.ficha) {
    var agregar = document.querySelector('.product-details add-to-cart-component, .product-details .add-to-cart-button, form[action*="/cart/add"] [type="submit"][name="add"], form[action*="/cart/add"] button[type="submit"]');
    var bloque = agregar && (agregar.closest('.buy-buttons-block, .product-form-buttons') || agregar.closest('form') || agregar);
    if (bloque && !document.querySelector('.met-dudas')) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'met-dudas';
      b.setAttribute('aria-controls', 'met-burbuja-tarjeta');
      b.innerHTML = '<img src="' + boton.querySelector('img').src + '" alt="" width="28" height="28" loading="lazy"><span>¿Dudas? Pregúntale a la Dra. Melina</span>';
      b.addEventListener('click', function (ev) {
        ev.stopPropagation(); forzada = true; tapada = false; pintar(); abrir(true, true);
      });
      bloque.insertAdjacentElement('afterend', b);
    }
    /* Teléfono: que la burbuja no tape «Agregar» mientras está a la vista */
    if (agregar && 'IntersectionObserver' in window) {
      var angosto = window.matchMedia('(max-width: 640px)');
      new IntersectionObserver(function (e) { tapada = angosto.matches && e[0].isIntersecting; pintar(); }).observe(agregar);
    }
  }
  pintar();
})();
