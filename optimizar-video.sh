#!/usr/bin/env bash
# Genera el video del hero y su póster a partir del original.
#
#   ./optimizar-video.sh ~/Downloads/video.mov
#
# El original (15 MB, 1920x1080 con audio) NO va al repo: GitHub Pages lo
# serviría tal cual y la portada pesaría quince veces más que el resto del
# sitio junto. Lo que sí va:
#
#   video/hero.mp4               1280x720, H.264, sin audio, ~1.2 MB
#   images/web/hero-poster.webp  un cuadro del propio video, ~75 KB
#
# Por qué estos valores:
#
# - SIN AUDIO. El hero arranca en silencio (los navegadores no dejan hacer
#   autoplay con sonido) y la pista de audio pesaba lo mismo para nada.
# - 1280 de ancho. El video va detrás de un velo crema; 1080p no se distingue
#   ahí y pesa casi el doble.
# - CRF 32. Probados 26 (2.3 MB), 29 (1.6 MB) y 32 (1.2 MB) sobre el cuadro más
#   difícil —el follaje del jardín—, y detrás del velo la diferencia no se ve.
#   El follaje y los cortes cada medio segundo son lo que más cuesta comprimir.
# - +faststart. Mueve el índice al principio para que empiece a reproducir
#   antes de terminar de bajar.
# - El póster es el cuadro del segundo 4: la recepción con el logo iluminado.
#   Es lo que se ve mientras carga y lo que ve quien pidió menos movimiento,
#   así que tiene que poder sostenerse solo.
set -euo pipefail

SRC="${1:?uso: ./optimizar-video.sh <video original>}"
cd "$(dirname "$0")"
mkdir -p video images/web

ffmpeg -v error -y -i "$SRC" -an \
  -vf "scale=1280:-2:flags=lanczos,format=yuv420p" \
  -c:v libx264 -preset slower -crf 32 -profile:v high -movflags +faststart \
  video/hero.mp4

TMP="$(mktemp -t poster).png"
ffmpeg -v error -y -ss 4.0 -i "$SRC" -frames:v 1 -vf "scale=1600:-2" "$TMP"
python3 -c "
from PIL import Image
Image.open('$TMP').convert('RGB').save('images/web/hero-poster.webp', 'WEBP', quality=78, method=6)"
rm -f "$TMP"

for f in video/hero.mp4 images/web/hero-poster.webp; do
  printf '%6d KB  %s\n' $(( $(stat -f%z "$f") / 1024 )) "$f"
done
