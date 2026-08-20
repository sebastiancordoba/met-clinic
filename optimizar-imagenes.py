#!/usr/bin/env python3
"""Genera las versiones web de las imágenes de marca en `images/web/`.

Los archivos de `BRANDING/` son de imprenta: `MET_POSITIVO_04.png` mide
11117x4501 px y el nav lo pinta a 40 px de alto. Servirlos tal cual costaba
7.9 MB en la primera visita, casi todo en PNG que nadie ve a ese tamaño.

Las derivadas viven en `images/web/` y NO en `BRANDING/`, a propósito:
`BRANDING/` es la fuente original de la marca y no debe llenarse de archivos
generados. Si mañana cambia un logo, se reemplaza el de BRANDING y se vuelve
a correr esto.

WebP y no PNG optimizado porque conserva transparencia y pesa una fracción.
Sin fallback a PNG: lo soportan todos los navegadores desde hace años y el
markup con <picture> por cada logo no compensa.

Uso: python3 optimizar-imagenes.py
"""
from pathlib import Path
from PIL import Image

SALIDA = Path("images/web")

# (origen, nombre destino, ancho máximo, calidad)
# Los anchos salen de a qué tamaño se pintan de verdad, x2 para pantallas
# retina. No tiene sentido subir de ahí.
TRABAJOS = [
    ("clinic.png",                                      "clinic.webp",       1920, 78),
    ("foto_jardin.png",                                 "foto-jardin.webp",   900, 82),
    ("BRANDING/METCLINIC/LOGOS/MET_POSITIVO_04.png",    "met-positivo-04.webp", 1200, 88),
    ("BRANDING/METCLINIC/LOGOS/MET_CREMA_05.png",       "met-crema-05.webp",    800, 88),
    ("BRANDING/METCLINIC/LOGOS/MET_NEGATIVO_07.png",    "met-negativo-07.webp", 400, 88),
    ("BRANDING/METCLINIC/LOGOS/MET_POSITIVO_03.png",    "met-positivo-03.webp", 400, 88),
    # Lockup apilado del hero. Se pinta a ~330 px, así que 800 cubre retina.
    ("BRANDING/METCLINIC/LOGOS/MET_POSITIVO_07.png",    "met-positivo-07.webp", 800, 88),
    ("images/servicios/02-oshot-prp-bioestimulacion.jpg", "servicio-oshot-prp.webp", 1200, 80),
]


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    antes = despues = 0
    for origen, destino, ancho, calidad in TRABAJOS:
        o = Path(origen)
        if not o.exists():
            print(f"  ✗ falta {origen}")
            continue
        im = Image.open(o)
        if im.width > ancho:
            im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
        d = SALIDA / destino
        im.save(d, "WEBP", quality=calidad, method=6)
        a, b = o.stat().st_size, d.stat().st_size
        antes += a; despues += b
        print(f"  {a//1024:>5} KB → {b//1024:>4} KB  (−{100 - b*100//a:>2}%)  {destino}")
    print(f"\n  {antes//1024} KB → {despues//1024} KB   "
          f"ahorro {(antes-despues)/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
