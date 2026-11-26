# Logos de marcas: fuentes oficiales (25-nov-2026)

Todos los archivos vienen del sitio del fabricante (o de su filial oficial). Se copiaron **tal cual, byte por byte**:
sin redibujar, sin vectorizar, sin recolorear ni recortar. Los SVG se revisaron y no traen `<script>`,
`foreignObject`, atributos `on*`, `href` externos ni `<image>`. Los PNG tienen transparencia (alfa o tRNS) y sus
esquinas son transparentes.

Lámina de revisión, cada logo sobre #ECE8E2 y sobre blanco: se generó en el scratchpad de la sesión
(`lamina-marcas.png`). No es parte del sitio.

---

## EMSELLA: `emsella.png` ⚠️ (baja resolución)

- **Origen:** https://files.btlnet.com/aest/file_items/0695e25b-e628-477f-b2d5-71ed7f145cdb/Emsella_LOGO_Enterprise-Blue-R_48px_WEB_EN100_1782120130_original.png
- **Página oficial:** https://btlaesthetics.com/en/media. La versión blanca del mismo logo está en https://btlaesthetics.com/en/for-providers/emsella-providers.
- **Formato:** PNG con paleta y transparencia (tRNS), 334 × 48 px, esquinas transparentes.
- **Color:** `#004F91`, muestreado del PNG. BTL lo llama «Enterprise Blue» en el nombre del archivo.
- **Nota:** mide solo 48 px de alto. Sirve hasta unos 24 px de alto en pantallas retina; a más tamaño se ve suave.
  BTL no publica un SVG ni una versión más grande en color. En el sitio solo están esta y las blancas.

## BTL: `btl.png` ✅

- **Origen:** https://files.btlnet.com/logo/logo_BTL_Aesthtics_light-blue_RGB.png
- **Página oficial:** https://btlaesthetics.com/en/for-providers/emsella-providers, la de Exomind y /en/media; el sitio lo carga como logo de la organización.
- **Formato:** PNG RGBA, 3728 × 1286 px, esquinas transparentes. Es el logo de **BTL Aesthetics** (rombos BTL + «AESTHETICS»), con margen transparente amplio alrededor.
- **Color:** `#009AD4` (azul claro), muestreado del PNG; el nombre del archivo dice «light-blue». La otra tinta de la marca es el `#004F91` «Enterprise Blue» de los logos de producto.
- **Nota:** el logo corporativo BTL solo, sin «AESTHETICS», existe en SVG, pero **solo en blanco**: https://files.btlnet.com/corp/file_items/7315584f-f1ce-4850-8a46-e58378679b99/footer_logo_1743697925_original.svg (btlnet.com). No se copió porque no se ve sobre fondos claros.

## MonaLisa Touch: `monalisa-touch.png` ⚠️

- **Origen:** https://www.monalisatouch.com/wp-content/uploads/2022/05/monalisa-touch-logo.png. Se encontró con la API de medios del propio WordPress (`/wp-json/wp/v2/media?search=logo`).
- **Página oficial:** https://www.monalisatouch.com/. La página usa una miniatura de este archivo (`elementor/thumbs/monalisa-touch-logo-…png`).
- **Formato:** PNG RGBA, 761 × 375 px, esquinas transparentes.
- **Colores** (muestreados del PNG): `#494843` (gris de «MonaLisa»), `#7D84BF` (lavanda de «Touch») y `#ECECEC` (el trazo espejado de «touch» detrás).
- **Nota:** por diseño, el trazo espejado es gris muy claro (`#ECECEC`) y casi no se ve sobre #ECE8E2 ni sobre blanco. Así es el logo oficial y no se tocó. Los logos actuales del sitio (`2026/03/monalisatouch-logo.webp`, `Monalisa-Touch-TM.webp`) son **blancos**, para fondo oscuro. No hay SVG público.

## DEKA: `deka.svg` ✅

- **Origen:** https://dekalaser.com/wp-content/uploads/2023/05/logo.svg
- **Página oficial:** https://dekalaser.com/ (logo del encabezado).
- **Formato:** SVG de 160 × 57.6, sin fondo. Sanitizado: no traía nada inseguro y no se cambió.
- **Colores** (del `fill` del SVG): `#1C0D44` (morado oscuro de «DEK»), `#9690B3` (lavanda de la «A») y `#494841` (gris de «Innate Ability»).
- **Extra:** la línea ginecológica se llama «DEKA Intimate». Su logo está en https://www.monalisatouch.com/wp-content/uploads/2026/03/DEKA-Intimate-logo.webp, pero es blanco: no se copió.

## Sofwave: `sofwave.svg` ✅

- **Origen:** https://sofwave.com/logo-sofwave-dark-BemXVl8B.svg
- **Página oficial:** https://sofwave.com/ (logo del encabezado, versión «dark» para fondos claros).
- **Formato:** SVG de 234 × 56. El `<rect>` que trae está dentro de un `<clipPath>`: no es un fondo y no pinta nada.
- **Colores** (del `fill` del SVG): `#000000` (palabra y ondas) y `#437CBF` (el punto azul de la «o»).
- **Nota:** la otra versión oficial, https://api.sofwave.com/app/uploads/2024/08/sofwave.svg, es para fondo oscuro (letras blancas) y su punto es `#377FD5`. Los dos azules son oficiales. En este archivo es `#437CBF`.

## X-Wave: ❌ por confirmar

- No se encontró un logo de X-Wave en ninguna fuente oficial. BTL ya retiró X-Wave de btlaesthetics.com y de btlnet.com.
  Se buscó en las páginas de producto y de medios, en la carpeta `files.btlnet.com/logo/` y en buscadores. Lo único
  que existe es el catálogo `BTL-X-WAVE_CAT_EN202`, en PDF y en raster, alojado por un distribuidor
  (logique.co.za). No es fuente del fabricante y no trae el logo aislado.
- **Fabricante:** no apareció evidencia oficial de otro fabricante. Se mantiene BTL, que es lo que dice la ficha técnica.
- **Mientras tanto:** usar `btl.png`.

## Asirox: `asirox.svg` ⚠️ (solo existe en blanco) y `asirox-evolve.svg` ✅

- **`asirox.svg`**
  - **Origen:** https://framerusercontent.com/images/ut3a5gAHuuV5qmiFOUH1FtOiz0.svg. Framer es el hosting del sitio de Asirox.
  - **Página oficial:** https://asirox.com/ (encabezado y pie).
  - **Formato:** SVG de 1157.78 × 232.09, sin fondo. El único `<rect>` es el trazo de la «i», no un fondo.
  - **Color:** `#FFFFFF` (del `fill` del SVG). Asirox solo publica su logo en blanco. Su favicon para modo claro (https://framerusercontent.com/images/lk6q4aJ6NlZitX5cbl0DmjS57t0.png) es el triángulo «A» en `#030304`, o sea que la marca es monocroma, blanco y negro.
  - **Nota:** **no se ve sobre #ECE8E2 ni sobre blanco.** Para usarlo en fondo claro, una opción es pintarlo de oscuro con CSS (por ejemplo `filter: brightness(0)`) sin tocar el archivo. Eso necesita el OK de Sebas, porque Asirox no publica esa versión.
  - **Variantes blancas** en https://asirox.com/medical: «Asirox medical» (`SYEls9dowPV1GMrKbtc9jABI70.svg`) y «Asirox aesthetic» (`uU3VyUeg4384BNVHdlG5lXU.svg`).
- **`asirox-evolve.svg`**
  - **Origen:** https://framerusercontent.com/images/Cnp0TTvX28efiUrJnl6eKzjQfw4.svg
  - **Página oficial:** https://asirox.com/medical, con alt «EVOLVE, plataforma de depilación láser de diodo de Asirox».
  - **Formato:** SVG de 480.52 × 77.61, sin `fill` explícito, así que se pinta en negro (`#000000`, el valor por defecto de SVG).
  - **Color:** el archivo no declara ninguno. Se ve negro y también acepta `currentColor` si se inserta en línea.

## EXOMIND: `exomind.png` ⚠️ (baja resolución)

- **Origen:** https://files.btlnet.com/aest/file_items/8ee34722-fc34-430b-99ae-99342f82fd3b/Exomind_LOGO_Enterprise-Blue-R_48px_WEB_EN100_1782480570_original.png
- **Página oficial:** https://btlaesthetics.com/en/media. La versión blanca está en https://btlaesthetics.com/en/for-providers/exomind-providers.
- **Formato:** PNG con paleta y transparencia (tRNS), 327 × 48 px.
- **Color:** `#004F91` («Enterprise Blue»), muestreado del PNG.
- **Nota:** igual que Emsella, mide solo 48 px de alto. El recorte va al ras: la «E» toca el borde izquierdo, y por eso dos esquinas no salen 100 % transparentes. No le falta nada al logo. Si se pone junto a otros logos, conviene darle margen con CSS.

## InBody: `inbody.png` ✅

- **Origen:** https://inbodyusa.com/static/assets/logo/inbody_logo.png (InBody USA, filial oficial de InBody Co.).
- **Páginas oficiales:** https://inbodyusa.com/ (encabezado). La casa matriz, https://inbody.com/, usa el mismo logo, pero solo en 107 × 44 px: https://inbody.com/images/logo/logo_inbody.webp.
- **Formato:** PNG RGBA, 1077 × 354 px, esquinas transparentes.
- **Color:** `#9D1C31` (guinda), muestreado del PNG de InBody USA. El webp de inbody.com da `#971B2F`. La diferencia es de compresión o de perfil, y la guía de marca no es pública. Si hay que elegir un solo hex, usar `#9D1C31`, que sale del archivo grande.
- **Descartado:** Wikimedia Commons tiene «Inbody logo.png» y «InBody logo 2.png», pero los subieron usuarios y no son del fabricante.

---

## Por confirmar para Sebas

1. **X-Wave:** no hay logo oficial público, porque BTL ya retiró el producto. Hay que pedírselo a BTL México o al distribuidor, o usar el de BTL.
2. **Asirox:** su logo solo existe en blanco. Hay que decidir entre ponerlo sobre un fondo oscuro, oscurecerlo con CSS (no es una versión oficial) o usar solo el logo «EVOLVE» (`asirox-evolve.svg`, negro y oficial). Sigue pendiente confirmar contra la placa que el equipo es un EVOLVE.
3. **Emsella y Exomind:** BTL solo publica los logos en color a 48 px de alto. Para usarlos más grandes, hay que pedirle a BTL el kit de marca (SVG o EPS).
4. **MonaLisa Touch:** el trazo espejado claro del logo casi no se ve sobre #ECE8E2. Así es el logo oficial. Si se quiere en vector, hay que pedírselo a DEKA.
