#!/usr/bin/env bash
# Genera el video del hero y su póster a partir del original.
#
#   ./optimizar-video.sh ~/Downloads/video.mov
#
# El original (15 MB, 1920x1080 a 11 Mbps, con audio) NO va al repo. Lo que sí:
#
#   video/hero-1080.av1.mp4      1920x1080, AV1,   ~3.4 MB  escritorio, si el navegador decodifica AV1
#   video/hero-1080.mp4          1920x1080, H.264, ~4.5 MB  escritorio, el resto (Safari en Macs sin AV1)
#   video/hero-movil.av1.mp4      720x1080, AV1,   ~1.5 MB  celular vertical
#   video/hero-movil.mp4          720x1080, H.264, ~1.9 MB  celular vertical, el resto (casi todo iPhone)
#   images/web/hero-poster.webp  un cuadro del propio video, ~75 KB
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
# - RECORTE VERTICAL PARA CELULAR. En un teléfono el hero es vertical y
#   object-fit:cover solo enseña la franja central (~550 px de los 1920).
#   Mandar el cuadro completo era pagar por píxeles que nadie ve y, encima,
#   estirar los que sí. El recorte 720x1080 del centro conserva la resolución
#   nativa de esa franja: más nítido y más ligero.
# - +faststart. Mueve el índice al principio para que empiece a reproducir
#   antes de terminar de bajar.
# - El póster es el cuadro del segundo 4: la recepción con el logo iluminado.
#   Es lo que se ve mientras carga y lo que ve quien pidió menos movimiento,
#   así que tiene que poder sostenerse solo.
set -euo pipefail

SRC="${1:?uso: ./optimizar-video.sh <video original>}"
cd "$(dirname "$0")"
mkdir -p video images/web

H264="-c:v libx264 -preset slower -crf 26 -profile:v high -movflags +faststart"
AV1="-c:v libsvtav1 -preset 4 -crf 36 -movflags +faststart"
COMPLETO="scale=1920:-2:flags=lanczos"
VERTICAL="crop=720:1080:(iw-720)/2:0"

# shellcheck disable=SC2086
{
  ffmpeg -v error -y -i "$SRC" -an -vf "$COMPLETO,format=yuv420p"     $H264 video/hero-1080.mp4
  ffmpeg -v error -y -i "$SRC" -an -vf "$COMPLETO,format=yuv420p10le" $AV1  video/hero-1080.av1.mp4 2>/dev/null
  ffmpeg -v error -y -i "$SRC" -an -vf "$VERTICAL,format=yuv420p"     $H264 video/hero-movil.mp4
  ffmpeg -v error -y -i "$SRC" -an -vf "$VERTICAL,format=yuv420p10le" $AV1  video/hero-movil.av1.mp4 2>/dev/null
}

TMP="$(mktemp -t poster).png"
ffmpeg -v error -y -ss 4.0 -i "$SRC" -frames:v 1 -vf "scale=1600:-2" "$TMP"
python3 -c "
from PIL import Image
Image.open('$TMP').convert('RGB').save('images/web/hero-poster.webp', 'WEBP', quality=78, method=6)"
rm -f "$TMP"

for f in video/hero-*.mp4 images/web/hero-poster.webp; do
  printf '%6d KB  %s\n' $(( $(stat -f%z "$f") / 1024 )) "$f"
done
