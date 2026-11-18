#!/usr/bin/env python3
"""Lleva la página al tema de Shopify (17-nov-2026, Sebas: «migrar la página dentro de Shopify»).

La página sigue siendo la fuente: este script lee index.html, las páginas internas, sus CSS y JS, y escribe en
tema-shopify/ los archivos que el agente de la tienda (met-clinic/claude-1) sube al tema «MET · Cosmo (apple)»:

  sections/met-pg-*.liquid       un bloque de la portada por sección; una sección por página interna; el pie
  templates/index.json           la portada de la clínica en «/»
  templates/page.met-*.json      Nosotros, Preguntas y los 7 servicios (/pages/<nombre>, con templateSuffix)
  assets/met-pagina.css.liquid   el CSS de la página con alcance .met-pg (no choca con Horizon)
  assets/met-pilares.css.liquid  el de las páginas internas, igual
  assets/met-pagina.js           main.js / pilares.js + lo de pie.js que aplica, guardado para correr en el tema
  assets/met-mapa-pie.js         el mapa vivo del pie (MapLibre)
  assets/met-pg-*                las imágenes, el video y la fuente que usan

No escribe en la tienda: solo genera archivos. El encabezado es el del tema (menú met-encabezado).
Uso: python3 exportar-tema.py   (vuelve a generar todo; corre de nuevo tras cambiar la página)
"""
import json
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / 'tema-shopify'
ENVOLTURA = 'met-pg redondeado apple'

PAGINAS = {  # archivo → (template, título de la sección)
    'nosotros.html': ('nosotros', 'La clínica'),
    'preguntas.html': ('preguntas', 'Preguntas frecuentes'),
    'pilar-ginecologia.html': ('pilar-ginecologia', 'Ginecología'),
    'pilar-facial.html': ('pilar-facial', 'Facial'),
    'pilar-corporal.html': ('pilar-corporal', 'Corporal'),
    'pilar-depilacion.html': ('pilar-depilacion', 'Depilación'),
    'pilar-piel.html': ('pilar-piel', 'Manchas y piel'),
    'pilar-capilar.html': ('pilar-capilar', 'Capilar'),
    'pilar-longevidad.html': ('pilar-longevidad', 'Longevidad'),
}
TIENDA = 'https://met-clinic.myshopify.com'
assets: set[str] = set()


# ── Rutas ────────────────────────────────────────────────────────────────────────────────────────────────────────
def nombre_asset(ruta: str) -> str:
    ruta = ruta.split('?')[0]
    base = re.sub(r'^(images/|BRANDING/webfonts/|video/)', '', ruta).replace('/', '-')
    nombre = 'met-pg-' + base
    assets.add(ruta + '\t' + nombre)
    return nombre


def url_asset(ruta: str) -> str:
    return "{{ '" + nombre_asset(ruta) + "' | asset_url }}"


def enlace(href: str) -> str:
    if href.startswith(TIENDA):
        resto = href[len(TIENDA):]
        return resto if resto not in ('', '/') else '/collections/all'
    m = re.match(r'^(index\.html)?(#.*)?$', href)
    if m and href and (m.group(1) or m.group(2)):
        return '/' + (m.group(2) or '') if m.group(1) else href
    m = re.match(r'^([a-z-]+)\.html(#.*)?$', href)
    if m:
        if m.group(1) == 'tienda':
            return '/collections/all'
        return f'/pages/{m.group(1)}' + (m.group(2) or '')
    return href


def html_a_liquid(html: str) -> str:
    def attr(m):
        nombre, valor = m.group(1), m.group(2)
        if nombre in ('src', 'poster', 'data-src') and re.match(r'^(images|BRANDING|video)/', valor):
            return f'{nombre}="{url_asset(valor)}"'
        if nombre == 'srcset':
            partes = []
            for p in valor.split(','):
                p = p.strip()
                u, _, d = p.partition(' ')
                partes.append((url_asset(u) if re.match(r'^(images|BRANDING)/', u) else u) + (' ' + d if d else ''))
            return f'srcset="{", ".join(partes)}"'
        if nombre == 'href':
            if re.match(r'^(images|BRANDING)/', valor):
                return f'href="{url_asset(valor)}"'
            return f'href="{enlace(valor)}"'
        return m.group(0)
    html = re.sub(r'\b(src|poster|data-src|srcset|href)="([^"]*)"', attr, html)
    html = re.sub(r"url\((['\"]?)((?:images|BRANDING)/[^'\")]+)\1\)", lambda m: f"url('{url_asset(m.group(2))}')", html)
    # El video del hero: main.js arma la URL con data-base; en el tema cada archivo lleva su asset_url.
    html = html.replace('data-base="video/hero"', ' '.join(
        f'data-{k}="{url_asset("video/hero-" + v)}"' for k, v in
        (('h1080', '1080.mp4'), ('h1080av1', '1080.av1.mp4'), ('movil', 'movil.mp4'), ('movilav1', 'movil.av1.mp4'))))
    if '{{' in html.replace("{{ '", '') or '{%' in html:
        pass
    return html


# ── CSS con alcance ──────────────────────────────────────────────────────────────────────────────────────────────
def bloques(css: str):
    """(cabecera, cuerpo) de nivel superior; cuerpo None para sentencias sueltas (@import…)."""
    i, n = 0, len(css)
    while i < n:
        j = css.find('{', i)
        k = css.find(';', i)
        if j == -1:
            break
        if k != -1 and k < j and css[i:k].strip().startswith('@'):
            yield css[i:k].strip(), None
            i = k + 1
            continue
        cab = css[i:j].strip()
        prof, p = 1, j + 1
        while prof and p < n:
            if css[p] == '{':
                prof += 1
            elif css[p] == '}':
                prof -= 1
            p += 1
        yield cab, css[j + 1:p - 1]
        i = p


def partir_selectores(s: str):
    out, prof, ac = [], 0, ''
    for ch in s:
        if ch == '(':
            prof += 1
        elif ch == ')':
            prof -= 1
        if ch == ',' and prof == 0:
            out.append(ac.strip())
            ac = ''
        else:
            ac += ch
    out.append(ac.strip())
    return [x for x in out if x]


def alcance(sel: str) -> str:
    sel = sel.strip()
    if sel in (':root', 'html', 'body', 'html, body', '*'):
        return '.met-pg' if sel != '*' else '.met-pg *'
    m = re.match(r'^html((?:\.[\w-]+|:not\([^)]*\))*)(.*)$', sel)
    if m:
        clases, resto = m.group(1), m.group(2)
        propias = re.findall(r'\.([\w-]+)', clases)
        otras = [c for c in propias if c not in ('redondeado', 'apple')]
        pre = '.met-pg' if not otras else 'html' + ''.join('.' + c for c in otras) + ' .met-pg'
        if ':not(' in clases:  # ?estilo=actual / normal no aplican en el tema: la regla siempre vale
            pre = '.met-pg'
        resto = resto.strip()
        if not resto:
            return pre
        if resto.startswith(('>', '+', '~')):
            return pre + ' ' + resto
        return pre + ' ' + resto
    m = re.match(r'^body\b(.*)$', sel)
    if m:
        return '.met-pg' + m.group(1)
    if sel.startswith(('*', '::')):
        return '.met-pg ' + sel
    return '.met-pg ' + sel


# Ajustes propios del tema: el encabezado de Horizon no es fijo ni transparente, así que la página no deja hueco
# para él (la portada mide la pantalla menos el encabezado y la cabecera de las internas no baja 68 px).
AJUSTES_TEMA = """
.met-pg .pilar-hero{margin-top:0}
.met-pg .portada{height:calc(100svh - var(--met-encabezado, 68px));min-height:480px}
/* Orilla a orilla abajo en el teléfono (Sebas 18-nov 09:06): el video baja detrás de la barra flotante de Safari (100lvh);
   gana al 100svh !important de met-apple.css (claude-1). La tarjeta de datos flota en index.html.
   +2 px: --met-encabezado (70) mide 2 px más que el encabezado real (68) y la portada sube 2 px de más; sin ellos asoma una
   línea crema abajo. */
@media (max-width:640px){html body:has(.met-pg .hero) .met-pg .portada{height:calc(100lvh + 2px) !important}}
/* Un solo «Agendar consulta» a la vista (pie.js 1): el del encabezado se esconde mientras se ve el de la portada. */
#header-group .met-agendar{transition:opacity .3s,visibility .3s}
html.cta-principal-visible #header-group .met-agendar{opacity:0;visibility:hidden;pointer-events:none}
/* Dónde está uno (pie.js 7) en el menú de Horizon: línea salvia de 2 px que se desliza bajo el ítem activo. */
#header-group .met-menu-lista{position:relative}
#header-group .nav__indicador{position:absolute;left:0;bottom:2px;width:100px;height:2px;border-radius:2px;background:#82867F;
  transform-origin:0 0;opacity:0;pointer-events:none;list-style:none;transition:transform .25s cubic-bezier(.25,.46,.45,.94),opacity .25s}
#header-group .nav__indicador.sin-transicion{transition:none}
#header-group .menu-list__link[aria-current]{color:#262626}
@media (prefers-reduced-motion: reduce){#header-group .nav__indicador{transition:opacity .2s}}
"""

# El scroll-spy de la página (pie.js 7) adaptado al menú de Horizon: los enlaces son /#seccion; en las páginas
# internas marca su ítem fijo (servicios → «Servicios», nosotros → «Equipo»).
JS_RECARGA = r"""
/* Recargar la portada la deja arriba (Sebas 17:40). scroll-container.js de Horizon guarda en history.state el
   scrollTop de .page-wrapper al salir (pagehide) y lo restaura en pageshow también al RECARGAR: una recarga tras un
   desplazamiento mínimo caía a media portada, con el encabezado ya sólido. Solo en recarga y sin ancla se borra
   ese dato antes de pageshow; atrás/adelante sigue restaurando como antes. */
(function () {
  try {
    var nav = performance.getEntriesByType('navigation')[0];
    if (!nav || nav.type !== 'reload' || location.hash) return;
    var st = history.state;
    if (st && typeof st === 'object' && 'scrollTop' in st) {
      var limpio = Object.assign({}, st); delete limpio.scrollTop;
      history.replaceState(limpio, '');
    }
    var pw = document.querySelector('.page-wrapper');
    var arriba = function () { if (pw) pw.scrollTop = 0; window.scrollTo(0, 0); };
    arriba();
    /* Desde que el documento es el que desplaza (claude-1, 19:15), el navegador también restaura solo al recargar
       (scrollRestoration «auto»), después de cargar: se vuelve a subir tras load, salvo que la persona ya se haya movido. */
    var movio = false;
    ['wheel', 'touchstart', 'keydown'].forEach(function (t) { addEventListener(t, function () { movio = true; }, { once: true, passive: true }); });
    addEventListener('load', function () {
      requestAnimationFrame(function () { if (!movio) arriba(); });
      setTimeout(function () { if (!movio) arriba(); }, 150);
    });
  } catch (e) {}
})();
"""

JS_MENU_TEMA = r"""
(function () {
  const primero = document.querySelector('#header-group .menu-list__link');
  // En Horizon los ítems van en <overflow-list> (que mide a sus hijos): la línea cuelga del <nav class="menu-list">.
  const lista = primero && (primero.closest('.menu-list') || primero.closest('nav'));
  if (!lista) return;
  lista.classList.add('met-menu-lista');
  const enlaces = [...lista.querySelectorAll('.menu-list__link')].filter((a) => a.tagName === 'A');
  const linea = document.createElement('span');
  linea.className = 'nav__indicador sin-transicion';
  linea.setAttribute('aria-hidden', 'true');
  lista.appendChild(linea);
  let activo = null;
  function poner(a, tipo) {
    activo = a || null;
    enlaces.forEach((e) => { if (e === activo) e.setAttribute('aria-current', tipo || 'location'); else e.removeAttribute('aria-current'); });
    if (!activo || !activo.offsetWidth) { linea.style.opacity = '0'; return; }
    const base = lista.getBoundingClientRect(), r = (activo.querySelector('.menu-list__link-title') || activo).getBoundingClientRect();
    linea.style.transform = `translateX(${r.left - base.left}px) scaleX(${r.width / 100})`;
    linea.style.opacity = '1';
  }
  const arrancar = () => requestAnimationFrame(() => requestAnimationFrame(() => linea.classList.remove('sin-transicion')));
  const ruta = location.pathname;
  const porHash = (h) => enlaces.find((a) => a.hash === h);
  const fijo = /^\/pages\/pilar-/.test(ruta) ? porHash('#servicios') : /^\/pages\/nosotros/.test(ruta) ? porHash('#especialistas')
    : enlaces.find((a) => a.classList.contains('menu-list__link--active') && !a.hash);
  const recolocar = () => poner(activo, activo && activo.getAttribute('aria-current'));
  addEventListener('resize', recolocar);
  document.fonts && document.fonts.ready.then(recolocar);
  if (ruta !== '/' || !('IntersectionObserver' in window)) { if (fijo) poner(fijo, 'page'); arrancar(); return; }
  const porId = new Map(enlaces.filter((a) => a.hash && a.pathname === '/').map((a) => [a.hash.slice(1), a]));
  let enMedio = null, espera = 0;
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => { if (e.isIntersecting) enMedio = e.target; else if (enMedio === e.target) enMedio = null; });
    clearTimeout(espera);
    espera = setTimeout(() => { const a = enMedio ? porId.get(enMedio.id) : null; if (a !== activo) poner(a); }, 120);
  }, { rootMargin: '-45% 0px -54% 0px' });
  document.querySelectorAll('.met-pg section[id]').forEach((s) => io.observe(s));
  arrancar();
})();
"""


PIE_CLAVES = ('footer', 'pie', 'mapa', 'maplibregl', 'barra-movil', 'btn-primary', 'cta-principal-visible')


def css_a_tema(css: str, fuentes_tema=('Metropolis', 'Larken'), solo_pie: bool = False) -> str:
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = []
    for cab, cuerpo in bloques(css):
        if cuerpo is None:
            continue
        if cab.startswith('@font-face'):
            fam = re.search(r"font-family:\s*'([^']+)'", cuerpo)
            if fam and fam.group(1) in fuentes_tema:
                continue  # el tema ya las trae (met-marca.css)
            out.append(cab + '{' + cuerpo.strip() + '}')
        elif cab.startswith(('@keyframes', '@-webkit-keyframes')):
            out.append(cab + '{' + cuerpo.strip() + '}')
        elif cab.startswith(('@media', '@supports', '@container', '@layer')):
            dentro = css_a_tema(cuerpo, fuentes_tema, solo_pie)
            if dentro.strip():
                out.append(cab + '{' + dentro + '}')
        elif cab.startswith('@'):
            out.append(cab + '{' + cuerpo.strip() + '}')
        else:
            lista = partir_selectores(cab)
            if solo_pie and not any(any(k in x for k in PIE_CLAVES) for x in lista) \
                    and not all(x in (':root', 'html', 'body', '*', '*::before', '*::after') or x.startswith('html.redondeado') and ' ' not in x
                                or x.startswith('html.apple') and ' ' not in x for x in lista):
                continue
            sels = ', '.join(alcance(s) for s in lista)
            out.append(sels + '{' + cuerpo.strip() + '}')
    texto = '\n'.join(out)
    return re.sub(r"url\((['\"]?)((?:images|BRANDING)/[^'\")]+)\1\)", lambda m: f"url('{url_asset(m.group(2))}')", texto)


# ── CSS crítico de la portada (Hermes/Sebas, 17-nov 23:58) ─────────────────────────────────────────────────────────
# En 3G la portada salía en blanco hasta que bajaba met-pagina.css (90 KB, bloqueante en el <body>). Ahora va en línea
# solo lo que pinta la primera pantalla y met-pagina.css baja sin bloquear (preload → stylesheet). Las reglas se eligen
# probando cada selector contra el HTML real de la portada (y sus ancestros: .met-pg, body, html) con un comparador
# sencillo que, ante la duda, INCLUYE la regla (pseudo-clases, :not/:has/:is, atributos y hermanos cuentan como
# coincidencia): sobra algún byte, nunca falta una regla.
class _Nodo:
    def __init__(self, tag, attrs, padre):
        self.tag, self.padre, self.hijos = tag, padre, []
        a = dict(attrs)
        self.id = a.get('id') or ''
        self.clases = set((a.get('class') or '').split())
        if padre is not None:
            padre.hijos.append(self)


def _arbol(html: str):
    from html.parser import HTMLParser
    vacios = {'br', 'img', 'input', 'meta', 'link', 'source', 'hr', 'wbr', 'path', 'circle', 'rect', 'line', 'polyline',
              'polygon', 'ellipse', 'use', 'stop'}
    raiz = _Nodo('html', [], None)
    body = _Nodo('body', [], raiz)
    pg = _Nodo('div', [('class', 'met-pg redondeado apple')], body)
    nodos = [raiz, body, pg]

    class P(HTMLParser):
        pila = [pg]

        def handle_starttag(self, tag, attrs):
            n = _Nodo(tag, attrs, self.pila[-1])
            nodos.append(n)
            if tag not in vacios:
                self.pila.append(n)

        def handle_startendtag(self, tag, attrs):
            nodos.append(_Nodo(tag, attrs, self.pila[-1]))

        def handle_endtag(self, tag):
            for i in range(len(self.pila) - 1, 0, -1):
                if self.pila[i].tag == tag:
                    del self.pila[i:]
                    break
    P(convert_charrefs=True).feed(html)
    return nodos


def _compuesto_ok(comp: str, n: '_Nodo') -> bool:
    comp = re.sub(r'\[[^\]]*\]', '', comp)
    m = re.match(r'^([a-zA-Z][\w-]*|\*)?', comp)
    tag = m.group(1) if m else None
    if tag and tag != '*' and tag.lower() != n.tag:
        return False
    for t, v in re.findall(r'([.#])([\w-]+)', comp):
        if t == '.' and v not in n.clases:
            return False
        if t == '#' and v != n.id:
            return False
    return True


def _selector_toca(sel: str, nodos) -> bool:
    sel = re.sub(r'::?-?[\w-]+\((?:[^()]|\([^()]*\))*\)', '', sel)   # :not(…), :has(…), :is(…), :nth-child(…)
    sel = re.sub(r'::?-?[\w-]+', '', sel)                             # :hover, ::before, ::-webkit-…
    sel = re.sub(r'\[[^\]]*\]', '', sel)
    comps, combs = [], []
    for tok in re.sub(r'\s*([>+~])\s*', r' \1 ', sel).split():
        if tok in ('>', '+', '~'):
            combs.append(tok)
        else:
            if len(comps) > len(combs):
                combs.append(' ')
            comps.append(tok)
    if not comps:
        return True
    if len(comps) != len(combs) + 1:
        return True  # no lo entendí: se queda

    def baja(n, i):
        if not _compuesto_ok(comps[i] or '*', n):
            return False
        if i == 0:
            return True
        c = combs[i - 1]
        if c == '>':
            return n.padre is not None and baja(n.padre, i - 1)
        if c in '+~':
            if n.padre is None:
                return False
            hermanos = n.padre.hijos[:n.padre.hijos.index(n)]
            return any(baja(h, i - 1) for h in (hermanos[-1:] if c == '+' else hermanos))
        a = n.padre
        while a is not None:
            if baja(a, i - 1):
                return True
            a = a.padre
        return False
    return any(baja(n, len(comps) - 1) for n in nodos)


def css_critico(css: str, html: str, js: str = '') -> str:
    nodos = _arbol(html)
    # Las clases que pone el JS (hero--loaded, visible, s-active…) no están en el HTML: se quitan de los selectores para
    # que sus reglas entren (si no, el texto del hero se quedaba en opacity:0 hasta que llegara met-pagina.css).
    de_js = set(re.findall(r"classList\.(?:add|toggle|replace)\(\s*'([\w-]+)'", js))
    usadas, ks = set(), []

    def filtra(texto):
        out = []
        for cab, cuerpo in bloques(texto):
            if cuerpo is None:
                continue
            if cab.startswith(('@keyframes', '@-webkit-keyframes')):
                ks.append((cab.split()[-1], f'{cab}{{{cuerpo.strip()}}}'))
            elif cab.startswith('@font-face'):
                out.append(f'{cab}{{{cuerpo.strip()}}}')
            elif cab.startswith(('@media', '@supports', '@container', '@layer')):
                dentro = filtra(cuerpo)
                if dentro:
                    out.append(f'{cab}{{' + '\n'.join(dentro) + '}')
            elif cab.startswith('@'):
                continue
            elif any(_selector_toca(re.sub(r'\.(' + '|'.join(map(re.escape, de_js)) + r')(?![\w-])', '', x) if de_js else x, nodos)
                     for x in partir_selectores(cab)):
                usadas.update(re.findall(r'animation(?:-name)?\s*:\s*([\w-]+)', cuerpo))
                out.append(f'{cab}{{{cuerpo.strip()}}}')
        return out
    reglas = filtra(re.sub(r'/\*.*?\*/', '', css, flags=re.S))
    reglas += [k for nombre, k in ks if nombre in usadas]
    return re.sub(r'\n\s+', '\n', '\n'.join(reglas))

# ── JS ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def js_pie() -> str:
    pie = (RAIZ / 'pie.js').read_text()
    partes = re.split(r'\n(?=// \d\. )', pie)
    quedan = [p for p in partes if re.match(r'// (1|4|5)\. ', p)]
    js = '\n'.join(quedan)
    js = js.replace("s.src = 'mapa-pie.js';", "s.src = window.metPg && window.metPg.mapa;")
    return js


def js_main() -> str:
    js = (RAIZ / 'main.js').read_text()
    # El encabezado es el del tema: lo propio del nav de la página no aplica.
    stub = ("// En el tema el encabezado es de Horizon: lo del nav de la página corre sobre un nav vacío y oculto.\n"
            "if (!document.getElementById('site-nav')) { const n = document.createElement('nav'); n.id = 'site-nav'; n.hidden = true;"
            " document.body.appendChild(n); }\n"
            "if (!document.getElementById('hamburger')) { const h = document.createElement('button'); h.id = 'hamburger'; h.hidden = true;"
            " document.body.appendChild(h); const d = document.createElement('div'); d.id = 'nav-drawer'; d.hidden = true; document.body.appendChild(d); }\n")
    viejo = "    v.src = v.dataset.base + (vertical ? '-movil' : '-1080') + (av1 ? '.av1' : '') + '.mp4';"
    assert viejo in js
    js = js.replace(viejo, "    v.src = v.dataset[(vertical ? 'movil' : 'h1080') + (av1 ? 'av1' : '')];")
    js = js.replace("if (!v || !v.dataset.base) return;", "if (!v || !v.dataset.h1080) return;")
    js = js.replace("const top = t.getBoundingClientRect().top + window.scrollY - 68;",
                    "const top = t.getBoundingClientRect().top + window.scrollY - (document.querySelector('header, .header')?.offsetHeight || 68);")
    return stub + js


def js_mapa() -> str:
    js = (RAIZ / 'mapa-pie.js').read_text()
    return js.replace('src="images/web/met-positivo-03.webp"', 'src="\' + (window.metPg && window.metPg.pin) + \'"')


# ── Secciones ────────────────────────────────────────────────────────────────────────────────────────────────────
def seccion(nombre: str, titulo: str, html: str, extra_head: str = '') -> str:
    esquema = json.dumps({'name': f'MET · {titulo}'[:25], 'tag': 'div', 'settings': []}, ensure_ascii=False, indent=2)
    return (f"{{%- comment -%}} Generado por exportar-tema.py desde la página (met-clinic, rama rendimiento). "
            f"No lo edites aquí: cambia la página y vuelve a correr el script. {{%- endcomment -%}}\n"
            f"{extra_head}<div class=\"{ENVOLTURA}\">\n{html.strip()}\n</div>\n\n{{% schema %}}\n{esquema}\n{{% endschema %}}\n")


def recursos(css_asset: str, js_principal: str, critico: str = '') -> str:
    pin = url_asset('images/web/met-positivo-03.webp')
    datos = (f"<script>window.metPg = {{ mapa: {{{{ 'met-mapa-pie.js' | asset_url | json }}}}, pin: \"{pin}\" }};</script>\n")
    if not critico:
        return seccion('recursos', 'Recursos página', '', f"{{{{ '{css_asset}' | asset_url | stylesheet_tag }}}}\n" + datos +
                       f"<script src=\"{{{{ '{js_principal}' | asset_url }}}}\" defer></script>\n")
    # Portada: el CSS de la primera pantalla en línea; el resto baja con prioridad alta sin bloquear el pintado
    # (preload → stylesheet). El JS de la página corre cuando ya está ese CSS: mide carruseles y no debe medir
    # contenido sin estilo. La vuelta arriba al recargar (JS_RECARGA) va en línea porque tiene que correr antes de pageshow.
    return seccion('recursos', 'Recursos página', '',
                   f"<style>{critico}</style>\n" + datos +
                   "<script>window.metPgCss = function (l) { if (l) l.rel = 'stylesheet'; if (window.metPgJs) return; "
                   "window.metPgJs = 1; var s = document.createElement('script'); "
                   f"s.src = {{{{ '{js_principal}' | asset_url | json }}}}; document.head.appendChild(s); }};</script>\n"
                   f"<link rel=\"preload\" as=\"style\" href=\"{{{{ '{css_asset}' | asset_url }}}}\" onload=\"metPgCss(this)\">\n"
                   f"<noscript>{{{{ '{css_asset}' | asset_url | stylesheet_tag }}}}</noscript>\n"
                   # Respaldo por si el navegador no dispara onload del preload (o ya estaba en caché antes de definirlo).
                   "<script>addEventListener('load', function () { var l = document.querySelector('link[rel=preload][as=style][onload]'); "
                   "if (l) metPgCss(l); else metPgCss(); });</script>\n"
                   f"<script>{JS_RECARGA}</script>\n")


def entre(html: str, ini: str, fin: str) -> str:
    a = html.index(ini)
    b = html.index(fin, a) + len(fin)
    return html[a:b]


def ld_json(html: str) -> str:
    cab = html[:html.index('<body')]
    return '\n'.join(re.findall(r'<script type="application/ld\+json">.*?</script>', cab, re.S))


def escribir(ruta: str, texto: str):
    p = SALIDA / ruta
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto)


def plantilla(orden: list[str]) -> str:
    return json.dumps({'sections': {k: {'type': f'met-pg-{k}', 'settings': {}} for k in orden}, 'order': orden},
                      ensure_ascii=False, indent=2)


def main():
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    idx = (RAIZ / 'index.html').read_text()
    # Las maquetas sin aprobar (bloques CSS «/* ══ MAQUETA …») no van al tema: hoy, «Tecnología» con ?tec=a|b.
    idx = re.sub(r'\n    /\* ══ MAQUETA.*?(?=\n    /\* ══|\n  </style>)', '', idx, flags=re.S)

    # CSS de la portada: el <style> en línea + estilo-apple.css; el de las internas: pilares.css + estilo-apple.css.
    estilo = re.search(r'<style>(.*?)</style>', idx, re.S).group(1)
    apple = (RAIZ / 'estilo-apple.css').read_text()
    escribir('assets/met-pagina.css.liquid', '/* Generado por exportar-tema.py: no editar */\n' + css_a_tema(estilo + '\n' + apple) + AJUSTES_TEMA)
    escribir('assets/met-pilares.css.liquid', '/* Generado por exportar-tema.py: no editar */\n' +
             css_a_tema((RAIZ / 'pilares.css').read_text() + '\n' + apple) + AJUSTES_TEMA)

    # JS
    escribir('assets/met-pagina.js', '/* Generado por exportar-tema.py: no editar */\n' + js_main() + JS_MENU_TEMA)
    escribir('assets/met-pilares.js', '/* Generado por exportar-tema.py: no editar */\n' + (RAIZ / 'pilares.js').read_text() + JS_MENU_TEMA)
    escribir('assets/met-mapa-pie.js', js_mapa())

    # Portada
    cuerpo = idx[idx.index('<body'):]
    bloques_idx = {
        'portada': entre(cuerpo, '<div class="portada">', '\n  </div>\n\n'),
        'servicios': entre(cuerpo, '<section id="servicios">', '</section>'),
        'especialistas': entre(cuerpo, '<section id="especialistas">', '</section>'),
        'testimonios': entre(cuerpo, '<section id="testimonios">', '</section>'),
        'preguntas': entre(cuerpo, '<section id="preguntas"', '</section>'),
        'contacto': entre(cuerpo, '<section id="contacto">', '</section>'),
    }
    pie = entre(cuerpo, '<footer class="pie3"', '</footer>')
    barra = entre(cuerpo, '<nav class="barra-movil', '</nav>')
    css_pagina = css_a_tema(estilo + '\n' + apple) + AJUSTES_TEMA
    # + AJUSTES_TEMA entero: son pocas reglas y varias apuntan al encabezado del tema (#header-group), que no está en el árbol.
    critico = css_critico(css_pagina, bloques_idx['portada'], js_main()) + AJUSTES_TEMA
    escribir('sections/met-pg-recursos.liquid', recursos('met-pagina.css', 'met-pagina.js', critico))
    escribir('sections/met-pg-recursos-pilares.liquid', recursos('met-pilares.css', 'met-pilares.js'))
    # Los bloques de la portada llevan «inicio-» para no chocar con las páginas internas (preguntas ≠ inicio-preguntas).
    for k, h in bloques_idx.items():
        # El póster del hero se precarga desde la propia sección (el <head> es del tema): sin esperar a met-pagina.css.
        precargas = '\n'.join(re.findall(r'<link rel="preload" as="image"[^>]*>', idx.split('</head>')[0]))
        extra = precargas + '\n' + ld_json(idx) + '\n' if k == 'portada' else ''
        if k == 'portada':
            # La entrada del texto del hero (hero--loaded) no espera a met-pagina.js, que ahora llega después de su CSS.
            h += ("\n<script>requestAnimationFrame(function () { var h = document.querySelector('.met-pg .hero');"
                  " if (h) h.classList.add('hero--loaded'); });</script>")
        escribir(f'sections/met-pg-inicio-{k}.liquid', seccion(k, 'Inicio ' + k, html_a_liquid(extra + h)))
    escribir('templates/index.json', plantilla(['recursos'] + ['inicio-' + k for k in bloques_idx]))
    # Un solo pie en todo el sitio (Hermes 13:03): va en footer-group con su CSS y JS mínimos.
    escribir('assets/met-pie.css.liquid', '/* Generado por exportar-tema.py: no editar. Solo el pie y la barra del teléfono. */\n'
             + css_a_tema(estilo + '\n' + apple, solo_pie=True)
             + '\n/* Con el cajón del menú abierto no se ve la barra fija del teléfono (claude-1, 18:4x) */\n'
             + 'body:has(details#Details-menu-drawer-container[open]) .met-pg .barra-movil{visibility:hidden}\n')
    escribir('assets/met-pie.js', '/* Generado por exportar-tema.py: no editar */\n' + js_pie())
    pin = url_asset('images/web/met-positivo-03.webp')
    escribir('sections/met-pg-pie-global.liquid', seccion('pie-global', 'Pie MET', html_a_liquid(pie + '\n' + barra),
             "{{ 'met-pie.css' | asset_url | stylesheet_tag }}\n"
             f"<script>window.metPg = Object.assign(window.metPg || {{}}, {{ mapa: {{{{ 'met-mapa-pie.js' | asset_url | json }}}}, pin: \"{pin}\" }});</script>\n"
             "<script src=\"{{ 'met-pie.js' | asset_url }}\" defer></script>\n"
             + (RAIZ / 'burbuja/burbuja.liquid').read_text()))
    # Burbuja «Pregúntale a la Dra. Melina» (Sebas 17:23): va con el pie global, fuera de .met-pg, y solo se pinta en la tienda.
    escribir('assets/met-burbuja.css', '/* Generado por exportar-tema.py desde burbuja/: no editar */\n' + (RAIZ / 'burbuja/burbuja.css').read_text())
    escribir('assets/met-burbuja.js', '/* Generado por exportar-tema.py desde burbuja/: no editar */\n' + (RAIZ / 'burbuja/burbuja.js').read_text())

    # Páginas internas: una sección con su cabecera y su contenido.
    for archivo, (nombre, titulo) in PAGINAS.items():
        h = (RAIZ / archivo).read_text()
        c = h[h.index('<body'):]
        ini = c.index('<header class="pilar-hero')
        fin = c.index('</main>') + len('</main>')
        escribir(f'sections/met-pg-{nombre}.liquid', seccion(nombre, titulo, html_a_liquid(ld_json(h) + '\n' + c[ini:fin])))
        orden = ['recursos-pilares', nombre]
        escribir(f'templates/page.met-{nombre}.json', plantilla(orden))

    # Assets binarios
    for linea in sorted(assets):
        origen, destino = linea.split('\t')
        o = RAIZ / origen
        if o.exists():
            (SALIDA / 'assets').mkdir(parents=True, exist_ok=True)
            shutil.copy2(o, SALIDA / 'assets' / destino)
        else:
            print('FALTA', origen)
    archivos = sorted(str(p.relative_to(SALIDA)) for p in SALIDA.rglob('*') if p.is_file())
    (SALIDA / 'ARCHIVOS.txt').write_text('\n'.join(archivos) + '\n')
    peso = sum((SALIDA / a).stat().st_size for a in archivos)
    print(f'{len(archivos)} archivos, {peso / 1e6:.1f} MB en {SALIDA}')


if __name__ == '__main__':
    main()


def prueba_local():
    """Arma tema-shopify/_prueba/*.html: las secciones con un encabezado falso de 68 px, para revisar el CSS con
    alcance sin subir nada. Sirve con la vista previa (127.0.0.1:8411/tema-shopify/_prueba/index.html)."""
    import json as _j
    d = SALIDA / '_prueba'
    d.mkdir(exist_ok=True)
    falso = ('<header style="position:sticky;top:0;z-index:50;height:68px;background:#F2F2ED;border-bottom:1px solid #ccc;'
             'display:flex;align-items:center;justify-content:center;font:500 13px/1 sans-serif;letter-spacing:.12em">'
             'ENCABEZADO DEL TEMA (Horizon)</header>')
    fuentes = ('<style>@font-face{font-family:Metropolis;src:url(../../BRANDING/webfonts/metropolis-200.woff2);font-weight:200}'
               '@font-face{font-family:Metropolis;src:url(../../BRANDING/webfonts/metropolis-300.woff2);font-weight:300}'
               '@font-face{font-family:Metropolis;src:url(../../BRANDING/webfonts/metropolis-400.woff2);font-weight:400}'
               '@font-face{font-family:Metropolis;src:url(../../BRANDING/webfonts/metropolis-500.woff2);font-weight:500}'
               '@font-face{font-family:Metropolis;src:url(../../BRANDING/webfonts/metropolis-600.woff2);font-weight:600}'
               '@font-face{font-family:Larken;src:url(../../BRANDING/webfonts/larken-300.woff2);font-weight:300}'
               'body{margin:0;background:#fff}</style>')
    def liquid(t):
        t = re.sub(r"\{\{ '([^']+)' \| asset_url \| stylesheet_tag \}\}", r'<link rel="stylesheet" href="../assets/\1">', t)
        t = re.sub(r"\{\{ '([^']+)' \| asset_url \| json \}\}", r'"../assets/\1"', t)
        t = re.sub(r"\{\{ '([^']+)' \| asset_url \}\}", r'../assets/\1', t)
        t = re.sub(r'\{%-? comment -?%\}.*?\{%-? endcomment -?%\}', '', t, flags=re.S)
        return re.sub(r'\{% schema %\}.*?\{% endschema %\}', '', t, flags=re.S)
    for css in ('met-pagina', 'met-pilares', 'met-pie'):
        (SALIDA / 'assets' / f'{css}.css').write_text(liquid((SALIDA / 'assets' / f'{css}.css.liquid').read_text()))
    (d / 'solo-pie.html').write_text(
        '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'{fuentes}</head><body><div style="height:400px;padding:40px;font:20px sans-serif">Página de tienda (solo el pie global)</div>'
        + liquid((SALIDA / 'sections' / 'met-pg-pie-global.liquid').read_text()) + '</body></html>')
    for tpl in (SALIDA / 'templates').glob('*.json'):
        orden = _j.loads(tpl.read_text())['order']
        cuerpo = ''.join(liquid((SALIDA / 'sections' / f'met-pg-{k}.liquid').read_text()) for k in orden + ['pie-global'])
        (d / (tpl.stem.replace('page.met-', '') + '.html')).write_text(
            f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'{fuentes}</head><body>{falso}{cuerpo}</body></html>')


if __name__ == '__main__':
    prueba_local()
