# Guía de estilo MET Clinic · página y tienda

Versión 1 · 13-nov-2026. Regla de Sebas (13-nov, 13:30): **un solo estilo para la página y la tienda**. Esta
guía es la referencia y todo agente diseña con ella. Si algo no cabe aquí, **no lo inventes**: propónselo a Sebas
como excepción y, cuando lo apruebe, se agrega a esta guía.

**De dónde salen los valores.** Todo lo de abajo ya estaba aprobado:
- página: rama `rendimiento` de `met-clinic`, es decir `index.html`, `estilo-apple.css`, `pilares.css` y `pie.js`;
- tienda: `met-tienda.css` y `met-apple.css` del tema «MET · Cosmo (apple)», con los fondos crema/salvia
  restaurados el 13-nov.

Copias:
- `met-clinic/docs/estilo-met.md`, que es la que manda;
- `~/hermes-workspace/met-clinic/estilo-met.md`.

Cuando dos fuentes no coincidían, se tomó la más reciente que aprobó Sebas. Esos casos van en «Pendientes de
alinear», al final.

---

## 1. Principios

1. **Claro, cálido y con aire, al estilo Apple sin copiarlo.** Fondos crema, mucho espacio, una sola idea por
   bloque, sombras apenas visibles y nada de adornos.
2. **Ancho completo.** Las secciones van de orilla a orilla con margen lateral `--margen`. No hay cajas centradas
   de 1100 a 1328 px.
3. **Cada bloque cabe en una pantalla:** 1280×680, 1440×900, 1920×1080, iPad e iPhone, descontando los 68 px de
   la barra.
4. **Un solo botón principal a la vista.** En la página es «Agendar consulta» y en la tienda «Agregar».
5. **Fotos de producto grandes y parejas.** El producto llena ~80 % del alto de su loseta en todas las tarjetas.
6. **Nada de blanco como fondo** de sección, de loseta de producto ni de tarjeta (ver § 2).

## 2. Color

| Token | Valor | Uso |
|---|---|---|
| `--tranquil` | `#F2F2ED` | Fondo base: `body`, barra superior y la mitad de las secciones |
| `--confort` | `#F7EDDC` | Fondo alterno de sección, cajas destacadas y texto sobre oscuro |
| `--sage` | `#82867F` | Títulos grandes, acento en Larken, líneas, íconos e indicador del menú. **Nunca para texto chico** (3.2:1) |
| `--sage-mid` | `rgba(130,134,127,.25)` | Bordes y divisores |
| `--sage-light` | `rgba(130,134,127,.10)` | Rellenos muy tenues (chips inactivos, hover de filas) |
| `--dark` | `#262626` | Texto principal, botón principal y fondo del pie |
| `--texto-suave` | `#515151` | Texto chico secundario: marca, cejas y notas (6.8:1) |
| `--loseta` | `#ECEBE4` | **Loseta de producto, salvia claro.** Es la que se usa por defecto |
| `--loseta-crema` | `#EFE3CF` | Loseta alterna, solo para destacar una tarjeta (la del centro en un trío) |
| `--crema-boton` | `#FBF7EF` | Botón principal sobre video o foto |
| `--existencia` | `#6E8B5E` / `#8A4B2A` | Punto «en existencia» / «quedan pocas» |

Reglas:
- Las secciones alternan **solo** `--tranquil` y `--confort`. No hay secciones blancas y en la tienda nunca se
  deja el blanco de Horizon (`#FFFFFF`, `rgb(255,255,255)`).
- La loseta de producto es siempre `--loseta` y la foto va con `mix-blend-mode:multiply`, para que el fondo
  blanco de los JPG tome el tono. Se permite `#FFFFFF` únicamente:
  - dentro de un campo de formulario o del buscador;
  - en la píldora «+» de agregar;
  - en el cajón del carrito.
- El texto oscuro translúcido nunca baja de alfa 0.75. Úsalo para texto de párrafo: `rgba(38,38,38,.78)`.
- Sobre `--sage` solo va texto grande. Una etiqueta chica sobre salvia usa `#111`.
- Revisa con axe-core antes de entregar cualquier cambio de color.

## 3. Tipografía

**Familias:**
- **Metropolis** (WOFF2 100–700) para todo;
- **Larken 300** solo para la palabra de acento dentro de un título, en `--sage` y sin cursiva sintética
  (`font-synthesis:none`);
- **TTCommons** no se usa en pantallas nuevas.

| Rol | Tamaño | Peso · interlineado · espaciado |
|---|---|---|
| Titular de portada | `clamp(40px,5vw,76px)` | 200 · 0.95 · −0.035em |
| Título de sección (h2) | `clamp(40px,5.8vw,84px)` | 200 · 0.94 · −0.035em |
| Título mediano (h2 de bloque secundario, h1 de colección) | `clamp(30px,3vw,46px)` | 200 · 1.0 · −0.025em |
| Subtítulo / h3 | `clamp(20px,1.8vw,26px)` | 300 · 1.2 · −0.01em |
| Párrafo de entrada | `clamp(16px,1.3vw,19px)` | 300 · 1.6 · color `rgba(38,38,38,.78)`, máx. 580 px |
| Párrafo | `clamp(16px,1.2vw,18px)` | 300 · 1.75, máx. 540–640 px |
| Nombre de producto | 16px | 400 · 1.3 |
| Precio | 15px (tarjeta) / 24px (ficha) | 400, cifras tabulares |
| Ceja (eyebrow) | 11–12px | 500 · MAYÚSCULAS · 0.22em · `--texto-suave`, con raya salvia de 20–28 px antes |
| Marca en tarjeta | 11px | 500 · MAYÚSCULAS · 0.18em · `--texto-suave` |
| Menú | 14px | 500 · MAYÚSCULAS · 0.12em |
| Botón | 12px | 600 · MAYÚSCULAS · 0.16em |
| Nota / leyenda | 13px | 300–400 · `--texto-suave` |

- Ningún texto que se lea queda debajo de 12 px, y los campos de formulario van a **16 px** para que el iPhone
  no haga zoom.
- **Precios:** `$1,050` (MXN, sin espacio y sin decimales si son ,00). En la tienda el formato sale del tema, no
  del admin.
- **Nombres de marca:** se escriben como la marca: Filorga, SVR, Cumlaude, Lazartigue, Colorescience, TiZO,
  Sensilis, EltaMD, Rejuvaskin. Las MAYÚSCULAS las pone el CSS, no el dato.

## 4. Rejilla, márgenes y aire

- Margen lateral: `--margen: clamp(20px,5vw,96px)`, el mismo en las secciones, el pie y los contenedores de la
  tienda.
- La barra superior usa 56 px en compu y 20 px en teléfono.
- **Aire de sección:** `--aire: clamp(48px,5vw,76px)` arriba y abajo de cada sección; en teléfono son 52 px.
  Entre dos secciones queda ~2 × `--aire`. No hay `padding` fijo de 100 a 150 px.
- Separación entre la cabecera de una sección (ceja + título + enlace) y su contenido: 32–44 px.
- **Cortes de ancho:**
  - ≤ 640: teléfono;
  - 641–1000: tableta;
  - ≥ 1001: compu;
  - la hamburguesa aparece hasta 1120 px.
- **Rejilla de productos:**

  | Ancho | Columnas | Separación |
  |---|---|---|
  | Compu (≥ 1001) | 4 | `clamp(16px,1.6vw,24px)` |
  | Compu ancha (≥ 1600) | 5 | igual |
  | Tableta | 3 | igual |
  | Teléfono | 2 | 12 px horizontal y 28 px vertical |

  Una sola columna de productos en el teléfono no se usa nunca.
- **Escala de espacios:** 4 · 8 · 12 · 16 · 24 · 32 · 48 · `--aire`. No uses valores sueltos.

## 5. Esquinas y sombras

- **Radios:**
  - `--r-sm` 8 px: campos y fotos chicas;
  - `--r-md` 20 px: tarjetas;
  - `--r-lg` 24 px: losetas de producto, fotos grandes y cajas;
  - `--r-pill` 999 px: botones, chips y sellos.
- **Sombra única:** `--sombra-suave: 0 1px 1px rgba(38,38,38,.03), 0 18px 40px -22px rgba(38,38,38,.18)`. Las
  tarjetas no llevan borde, solo esta sombra. Los divisores son líneas de 1 px en `--sage-mid` o
  `rgba(130,134,127,.2)`.

## 6. Botones y controles

| Tipo | Aspecto |
|---|---|
| **Principal** | Píldora `--dark` con texto `--confort`, 12px/600/0.16em en MAYÚSCULAS, relleno 15 × 32 px, alto mínimo 48 px. Brillo de vidrio arriba: `inset 0 1px 0 rgba(255,255,255,.35)` + degradado blanco 18 % → 0. Hover: `#000` y `scale(1.02)`. Al presionar: `scale(.98)` |
| **Principal sobre foto o video** | Igual, pero en `--crema-boton` con texto `--dark` |
| **Secundario** | Texto `--dark` sin borde, con « ›» al final. Hover: `--sage` |
| **Contorno** (CTA del menú, «Agendar consulta») | Píldora con borde `--sage` y fondo `rgba(255,255,255,.45)`; desenfoque solo en compu con mouse. Hover: fondo `--sage` y texto `--confort` |
| **Chip / filtro** | Píldora 12–13px, borde `--sage-mid`, fondo transparente. Activo: fondo `--dark`, texto `--confort`. Alto mínimo 36 px (44 px de área táctil) |
| **Agregar rápido «+»** | Círculo de 40 px abajo a la derecha de la loseta: vidrio (`rgba(255,255,255,.45)` + borde blanco 55 %) en compu y blanco sólido en táctil |
| **Flechas de carrusel** | Círculo de 48 px con borde `--sage` y fondo `--tranquil` |
| **Campo / buscador** | Fondo blanco, borde `--sage-mid`, píldora (buscador) o `--r-sm` (formulario), 16 px |

Debe haber un solo botón principal por pantalla. Los textos de botón son verbos cortos en español: «Agregar»,
«Agendar consulta», «Ver todo», «Pagar». Nada en inglés.

## 7. Tarjeta de producto (una sola, igual en la página y en la tienda)

```
┌──────────────────────┐  loseta --loseta, 1:1, --r-lg, --sombra-suave, sin borde
│ [Sello]              │  sello opcional: píldora blanca 11px arriba a la izquierda («Nuevo», «Lo más elegido»)
│       ▢ producto     │  el producto llena ~80 % del alto (recorte por foto: snippet met-recorte), centrado, multiply
│                 (+)  │  agregar rápido
└──────────────────────┘
MARCA                      11px · .18em · --texto-suave
Nombre del producto        16px · 400 · máx. 2 renglones (line-clamp)
$1,050        Quedan 3     15px · existencia 12px en #8A4B2A solo si hay ≤ 3
```

- Hover (solo con mouse): la loseta sube 3 px con `scale(1.01)` y la sombra crece; el producto escala 1.04. El
  movimiento dura .5 s con `cubic-bezier(.2,.8,.2,1)`.
- Agotado: la foto queda al 55 % de opacidad, «Agotado» va en lugar de «Quedan» y no aparece el «+».
- Toda la tarjeta es un solo enlace a la ficha y el «+» es un botón aparte, con `aria-label="Agregar <nombre>"`.
- Las fotos llevan `width` y `height`, `loading="lazy"` salvo las primeras 4, y `alt` = nombre del producto.

## 8. Fotos

- **Producto:** loseta + multiply + recorte al ~80 % del alto. Nunca se dejan las fotos con su blanco de origen.
  Si una foto trae fondo gris (Rejuvaskin, Sensilis), se recorta la fuente; no se tapa con CSS.
- **Personas y lugares:** `--r-lg` + `--sombra-suave`, `filter:saturate(1.04) contrast(1.02)`, enfocadas en la
  cara y con alto máximo de `100svh - 68px`.
- Las fotos se sirven en WebP del tamaño que se pinta: en la tienda `image_url: width:` con `srcset`, y en la
  página los derivados de `images/web/`.

## 9. Encabezado

- 68 px de alto en las dos, fijo, en rejilla `1fr auto 1fr`: logo a la izquierda, menú centrado de verdad y
  acciones a la derecha.
- **Logo** de 54 px de alto, con **destello**: un gradiente que barre por dentro de la silueta durante 2.4 s
  (`cubic-bezier(.4,0,.2,1)`). Se dispara al pasar el mouse y cada 10–12 s solo, con mínimo 2 s entre brillos; se
  pausa al desplazar y con `prefers-reduced-motion`.
- **Menú:** Servicios · Equipo · Opiniones · Contacto · Tienda, a 14px/500/0.12em en `--texto-suave`.
  - El activo va en `--dark`, con una **línea de 2 px en `--sage` que se desliza** bajo el ítem de la sección
    visible (*scroll-spy*). En páginas internas y en la tienda la línea queda fija en el ítem actual
    (`aria-current="page"`).
  - El hover lleva un subrayado de 1 px que crece de izquierda a derecha.
- **Acciones:** «Agendar consulta» (contorno) + bolsa de 40 px sin contador.
- **Con hamburguesa (≤ 1120):** hamburguesa a la izquierda, logo al centro y bolsa a la derecha.
- **Fondo:** `--tranquil` opaco con borde inferior `rgba(255,255,255,.45)` y brillo de vidrio. El desenfoque
  (`blur(20px) saturate(180%)` sobre `rgba(242,242,237,.72)`) va **solo en compu con mouse (> 1000 px)**; en
  teléfono y pantallas táctiles el fondo es crema sólido, porque el desenfoque hace lento el scroll en iPhone.

## 10. Pie

- Fondo `--dark` con línea superior de 2 px `--sage`, `padding-top: --aire` y texto `--confort`.
- **Compu: 3 columnas** (`1fr 1fr 1.35fr`):
  1. marca y datos: logo crema de 260 px, dirección y horario;
  2. contacto y redes: un título de 12px/500/0.16em y botones redondos;
  3. mapa ilustrado con la tarjeta «Cómo llegar» abajo.

  Debajo va la barra legal a todo el ancho.
- **Teléfono:** las 3 columnas se apilan.
- Sin columnas de enlaces y sin líneas divisorias internas.
- Los datos van a 14px/300 en `rgba(247,237,220,.82)` y las notas a 13 px en `.68`.
- El crédito «© OpenStreetMap» es obligatorio.
- El pie de la tienda es el mismo de la página. Si la tienda necesita enlaces legales (envíos, devoluciones,
  privacidad), van en la barra legal, no en columnas.

## 11. Movimiento

- **Curva de la casa:** `cubic-bezier(.2,.8,.2,1)`. Las transiciones cortas de color duran .3 s y las de forma
  .5 s.
- **Aparición al desplazar:** `translateY(28px) scale(.985)` → normal en .9 s, una vez por elemento y sin
  escalonar más de 4.
- **Desplazamiento:**
  - sin *scroll-snap* y sin rebote elástico;
  - el desplazamiento suave descuenta 68 px (con `scroll-padding-top: 76px`);
  - barra de desplazamiento propia: ver `pie.js` (2), nunca `::-webkit-scrollbar`.
- **Cajones** (carrito, filtros, menú): entran desde la orilla en 400–600 ms, con un velo `rgba(38,38,38,.45)`
  que aparece en 600 ms.
- `prefers-reduced-motion: reduce` quita transformaciones y deja solo fundidos de .2 s.
  `prefers-reduced-transparency` quita los vidrios.

## 12. Estados

| Estado | Regla |
|---|---|
| Foco | `outline: 2px solid var(--dark); outline-offset: 3px` en todo lo que se puede enfocar, solo con `:focus-visible`. Nunca `outline:none` sin reemplazo |
| Hover | Solo con `@media (hover:hover)`; en táctil no hay estados pegados |
| Activo / presionado | `scale(.98)` |
| Seleccionado (chip, talla, filtro) | Fondo `--dark` y texto `--confort` |
| Deshabilitado | Opacidad .45, `cursor:not-allowed` y sin hover |
| Cargando | `aria-busy="true"` y opacidad .5. No se usan *spinners* de colores |
| Vacío (búsqueda sin resultados, carrito vacío, colección sin productos) | Título mediano, una frase y **4 productos «Lo más elegido»** + botón secundario «Ver toda la tienda». Nunca una pantalla en blanco |
| Error (formulario) | Texto 13 px en `#8A4B2A` bajo el campo, con borde del campo del mismo color |
| Éxito (agregado al carrito) | Se abre el cajón del carrito, sin alertas ni *toasts* |

## 13. Texto y reglas de contenido

- Español de México, con trato de «tú», en voz cálida y clínica. Ningún texto de interfaz queda en inglés
  («Add to cart», «Sort by», «Filter» y «Sold out» son errores).
- **COFEPRIS:** no se prometen resultados. No se usan «definitiva», «sin tiempo de recuperación» ni «se nota
  desde la primera sesión». Antes/después solo con consentimiento escrito.
- **Precios:**
  - en la página, solo los de la consulta;
  - en la tienda, solo los de producto;
  - en ningún lugar, precios de tratamientos ni de paquetes.
- Nunca se muestran LUXMETIQUE ni medicamentos.

## 14. Rendimiento y accesibilidad (mínimos)

- Fuentes WOFF2 con `font-display:swap` y precarga de Metropolis 200/400.
- LCP ≤ 2.5 s en teléfono 4G y CLS ≤ 0.05. Las imágenes llevan dimensiones; las de abajo del pliegue van con
  `lazy`.
- Sin bibliotecas nuevas. Los scripts de terceros (Doctoralia, mapas, chat) se cargan solo al usarlos.
- axe-core sin violaciones serias ni críticas, contraste AA y áreas táctiles de 44 px.
- Cada página tiene un `h1` y el orden de encabezados no salta niveles.

## 15. Pendientes de alinear (detectados al escribir la guía)

Estos son los lugares donde la página y la tienda no coinciden hoy. Se corrigen hacia esta guía sin pedir permiso,
porque la guía ya recoge lo aprobado:

| Dónde | Hoy | Según la guía |
|---|---|---|
| Página, «Lo más elegido» (`.elegido`) | Tarjeta blanca con borde | Loseta `--loseta` sin borde, igual que la tienda |
| Tienda, contenedores | `max-width: 1328px` y `--met-gutter: 56px` | Ancho completo con `--margen` |
| Tienda, secciones | `padding: 100px` | `--aire` |
| Tienda, tema publicado | Fondos blancos del experimento del 4-nov | `--tranquil`/`--confort` + `--loseta` |
| Tienda, tarjeta | El producto llena ~72–76 % | ~80 % con `met-recorte` |

Cualquier otra diferencia que quieras introducir: **propónsela a Sebas** con captura antes/después y no la apliques
hasta su OK.
