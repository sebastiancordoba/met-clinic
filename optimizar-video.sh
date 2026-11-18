#!/usr/bin/env bash
# Genera el video del hero y su póster a partir del original.
#
#   ./optimizar-video.sh ~/Downloads/video.mov
#
# El original (15 MB, 1920x1080 a 11 Mbps, con audio) NO va al repo; está en el Drive de
# la clínica, un .MOV que se llama «video». Lo que sí va:
#
#   video/hero-1080.av1.mp4      1920x1080, AV1,   ~4.1 MB escritorio, si el navegador decodifica AV1
#   video/hero-1080.mp4          1920x1080, H.264, ~5.8 MB  escritorio, el resto (Safari en Macs sin AV1)
#   video/hero-movil.av1.mp4      720x1080, AV1,   ~1.9 MB  celular vertical
#   video/hero-movil.mp4          720x1080, H.264, ~2.5 MB  celular vertical, el resto (casi todo iPhone)
#   images/web/hero-poster.webp  un cuadro del propio video, ~75 KB
#   images/web/hero-poster-movil.webp  el mismo cuadro en vertical 720x1080, ~50 KB
#
# main.js elige cuál bajar; solo se descarga uno.
#
# Por qué estos valores:
#
# - SIN AUDIO. El hero arranca en silencio (los navegadores no dejan hacer
#   autoplay con sonido) y la pista de audio pesaba lo mismo para nada.
# - 1080p y CRF 26 / AV1 36. La primera versión iba a 1280 y CRF 32 (1.2 MB)
#   suponiendo que el velo crema escondía los detalles; cuando el velo se
#   aligeró, la corteza y la hiedra se veían embarradas. Comparando recortes
#   al 100% contra el original, CRF 26 en H.264 y CRF 36 en AV1 quedan
#   prácticamente iguales; AV1 pesa ~25% menos con la misma calidad.
#   Con el FILTRO de abajo, AV1 sube a CRF 39: la textura recuperada le
#   costaba 5 MB a CRF 36 y a 39 se ve igual (a 42 la corteza ya se suaviza).
# - RECORTE VERTICAL PARA CELULAR. En un teléfono el hero es vertical y
#   object-fit:cover solo enseña la franja central (~550 px de los 1920).
#   Mandar el cuadro completo era pagar por píxeles que nadie ve y, encima,
#   estirar los que sí. El recorte 720x1080 del centro conserva la resolución
#   nativa de esa franja: más nítido y más ligero.
# - +faststart. Mueve el índice al principio para que empiece a reproducir
#   antes de terminar de bajar.
# - EMPIEZA CON LA TOMA DEL ÁRBOL (Sebas, 17-nov-2026): el árbol al centro, la
#   hiedra a la izquierda y los ventanales a la derecha. Esa toma empieza en el
#   cuadro 200 (el corte 199 → 200 del montaje, ~7.3 s del original). El video se
#   ROTA: cuadros 200…330 y luego 0…199, así el loop cierra en un corte natural
#   (fin de la toma del aparato → inicio del árbol). La unión vieja 330 → 0 ya era
#   un cambio de toma y queda como un corte más. Si cambia el original, busca el
#   corte otra vez (diferencia entre cuadros seguidos).
# - El póster es ese mismo cuadro 200, para que no haya brinco al arrancar. Es lo
#   que ve quien pidió menos movimiento. La hiedra pesa mucho en WebP: va a 1280 px
#   (600 en vertical), calidad 60 y un desenfoque de 0.6 px (~130 KB y ~95 KB).
set -euo pipefail

SRC="${1:?uso: ./optimizar-video.sh <video original>}"
cd "$(dirname "$0")"
mkdir -p video images/web

H264="-c:v libx264 -preset slower -crf 26 -profile:v high -movflags +faststart"
AV1="-c:v libsvtav1 -preset 4 -crf 39 -movflags +faststart"
# Limpieza ligera + nitidez, ANTES de escalar. El archivo que recibimos ya es
# una exportación comprimida (1080p a 11 Mbps): hqdn3d quita el ruido de esa
# compresión y unsharp devuelve la definición a la corteza y la hiedra.
# Probados contra el actual en recortes al 100% (oct-2026): CAS solo, esto, y
# nlmeans+CAS; éste rescató más sin halos. Si llega un original de mejor
# calidad, probar primero SIN este filtro: puede no hacer falta.
FILTRO="hqdn3d=1.2:1.2:2.5:2.5,unsharp=5:5:0.7:5:5:0"
COMPLETO="$FILTRO,scale=1920:-2:flags=lanczos"
VERTICAL="$FILTRO,crop=720:1080:(iw-720)/2:0"
# Un segundo más lento (Sebas, 30-oct-2026): el original son 331 cuadros en 11.03 s
# y aquí duran 12.03 s. Son los mismos 331 cuadros, a 27.5 por segundo en vez de 30:
# sin -r, ffmpeg los redondea a 30 por segundo y el ritmo sale disparejo. Si cambia
# el original, recalcula los dos valores (duración nueva / duración original).
RITMO="setpts=PTS*361/331"
CUADROS="-r 9930/361"
INICIO=200
ROTAR="split[a][b];[a]trim=start_frame=$INICIO,setpts=PTS-STARTPTS[x];[b]trim=end_frame=$INICIO,setpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=1:a=0"

# shellcheck disable=SC2086
{
  ffmpeg -v error -y -i "$SRC" -an -filter_complex "[0:v]$COMPLETO,$RITMO,$ROTAR,format=yuv420p[o]"     -map '[o]' $CUADROS $H264 video/hero-1080.mp4
  ffmpeg -v error -y -i "$SRC" -an -filter_complex "[0:v]$COMPLETO,$RITMO,$ROTAR,format=yuv420p10le[o]" -map '[o]' $CUADROS $AV1  video/hero-1080.av1.mp4 2>/dev/null
  ffmpeg -v error -y -i "$SRC" -an -filter_complex "[0:v]$VERTICAL,$RITMO,$ROTAR,format=yuv420p[o]"     -map '[o]' $CUADROS $H264 video/hero-movil.mp4
  ffmpeg -v error -y -i "$SRC" -an -filter_complex "[0:v]$VERTICAL,$RITMO,$ROTAR,format=yuv420p10le[o]" -map '[o]' $CUADROS $AV1  video/hero-movil.av1.mp4 2>/dev/null
}

TMP="$(mktemp -t poster).png"
POSTER="select=eq(n\\,$INICIO),$FILTRO"
ffmpeg -v error -y -i "$SRC" -frames:v 1 -vf "$POSTER,scale=1280:-2:flags=lanczos" "$TMP"
python3 -c "
from PIL import Image, ImageFilter
Image.open('$TMP').convert('RGB').filter(ImageFilter.GaussianBlur(0.6)).save('images/web/hero-poster.webp', 'WEBP', quality=60, method=6)"
ffmpeg -v error -y -i "$SRC" -frames:v 1 -vf "$POSTER,crop=720:1080:(iw-720)/2:0,scale=600:-2:flags=lanczos" "$TMP"
python3 -c "
from PIL import Image, ImageFilter
Image.open('$TMP').convert('RGB').filter(ImageFilter.GaussianBlur(0.6)).save('images/web/hero-poster-movil.webp', 'WEBP', quality=60, method=6)"
rm -f "$TMP"

for f in video/hero-*.mp4 images/web/hero-poster*.webp; do
  printf '%6d KB  %s\n' $(( $(stat -f%z "$f") / 1024 )) "$f"
done
