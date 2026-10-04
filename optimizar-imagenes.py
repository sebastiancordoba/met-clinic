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
    # Fotos de tratamiento de las páginas de servicio (sesión de septiembre).
    # Quien sale recostada es del equipo haciendo de modelo.
    ("images/servicios/healite-ii.jpg",                 "servicio-healite.webp", 900, 80),
    ("images/servicios/exomind.jpg",                    "servicio-exomind.webp", 900, 80),
    # El equipo en la entrada, para la cabecera de la sección. Vertical.
    ("images/equipo/grupo.jpg",                         "equipo-grupo.webp",  900, 80),
    # Mosaico "La clínica" de la portada (sesión de septiembre). Las verticales
    # se pintan a ~360 px de ancho; 900 cubre retina con margen.
    # Logo de asociación: el PNG original mide 4784 px y se pinta a ~72 px de alto.
    ("images/asoc/solapav.png",                         "asoc-solapav.webp",        480, 90),
    ("images/clinica/recepcion.jpg",                    "clinica-recepcion.webp",   900, 80),
    ("images/clinica/detalle-tratamiento.jpg",          "clinica-detalle.webp",     900, 80),
    ("images/clinica/consultorio-ultrasonido.jpg",      "clinica-consultorio.webp", 900, 80),
    ("images/clinica/boutique.jpg",                     "clinica-boutique.webp",    900, 80),
    ("images/clinica/cabina-exomind.jpg",               "clinica-exomind.webp",     900, 80),
]


# Retratos del equipo. Los originales vienen a 2:3 de cuerpo casi entero, y la
# tarjeta es 4:5: pintados tal cual, las caras salían chicas y cada quien a
# distinta altura. Se recortan a medio cuerpo con EL MISMO tamaño de recorte
# para todas —misma escala— y la cara a la misma altura, para que se lean
# como serie y no como fotos sueltas.
#
# (origen, destino, centro x de la cara, centro y de la cara) en fracciones
# de la foto. Medidos a mano sobre una rejilla: son seis y así quedan a la
# vista y se pueden corregir, en vez de depender de un detector de rostros.
# Los originales en images/equipo/ van reducidos a 3000 px de alto: el doble
# de lo que pide la tarjeta, sin meter 10 MB al repo.
RETRATOS = [
    ("images/equipo/dra-melina.jpg", "equipo-dra-melina.webp", 0.52, 0.39),
]
RETRATO_ALTO = 0.45      # alto del recorte como fracción del alto de la foto
RETRATO_CARA_Y = 0.30    # dónde cae la cara dentro del recorte
RETRATO_SALIDA = (720, 900)   # 4:5, la tarjeta pinta ~300 px de ancho x2


def generar_retratos() -> None:
    for origen, destino, cx, cy in RETRATOS:
        im = Image.open(origen).convert("RGB")
        W, H = im.size
        ch = round(H * RETRATO_ALTO); cw = ch * 4 // 5
        left = min(max(round(cx * W - cw / 2), 0), W - cw)
        top = min(max(round(cy * H - RETRATO_CARA_Y * ch), 0), H - ch)
        im = im.crop((left, top, left + cw, top + ch)).resize(RETRATO_SALIDA, Image.LANCZOS)
        im.save(SALIDA / destino, "WEBP", quality=80, method=6)
        print(f"  {(SALIDA / destino).stat().st_size // 1024:>5} KB  {destino}")


# Favicon y tarjeta para compartir. Se generan aquí y no a mano porque
# dependen de los mismos originales: si cambia el logo o la foto de la
# clínica, estos dos tienen que cambiar con ellos.
LOGO_MARCA = "BRANDING/METCLINIC/LOGOS/MET_POSITIVO_03.png"
LOGO_LOCKUP = "BRANDING/METCLINIC/LOGOS/MET_POSITIVO_04.png"
FOTO_PORTADA = "clinic.png"
TRANQUIL = (242, 242, 237, 255)


def generar_favicon() -> None:
    """El monograma sobre el crema de marca.

    Con fondo y no transparente a propósito: el logo es oscuro y en una
    pestaña con tema oscuro desaparecería.
    """
    logo = Image.open(LOGO_MARCA).convert("RGBA")
    for lado, nombre in [(32, "favicon-32.png"), (180, "favicon-180.png"), (512, "favicon-512.png")]:
        lienzo = Image.new("RGBA", (lado, lado), TRANQUIL)
        margen = round(lado * 0.14)
        marca = logo.copy()
        marca.thumbnail((lado - margen * 2, lado - margen * 2), Image.LANCZOS)
        lienzo.paste(marca, ((lado - marca.width) // 2, (lado - marca.height) // 2), marca)
        lienzo.save(SALIDA / nombre, "PNG", optimize=True)
        print(f"  {(SALIDA / nombre).stat().st_size // 1024:>5} KB  {nombre}")

    # Los navegadores piden /favicon.ico aunque nadie lo declare.
    ico = Image.new("RGBA", (64, 64), TRANQUIL)
    m = logo.copy()
    m.thumbnail((46, 46), Image.LANCZOS)
    ico.paste(m, ((64 - m.width) // 2, (64 - m.height) // 2), m)
    ico.save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"  {Path('favicon.ico').stat().st_size // 1024:>5} KB  favicon.ico")


def generar_og() -> None:
    """La tarjeta de 1200x630 que se ve al pegar la liga en WhatsApp.

    Foto de la clínica con un velo crema encima para que el logotipo se lea.
    Se usa el lockup horizontal y no el monograma: la imagen tiene que
    explicarse sola, y "MET" a secas no dice qué es.
    """
    foto = Image.open(FOTO_PORTADA).convert("RGB")
    escala = max(1200 / foto.width, 630 / foto.height)
    foto = foto.resize((round(foto.width * escala), round(foto.height * escala)), Image.LANCZOS)
    izq, arr = (foto.width - 1200) // 2, (foto.height - 630) // 2
    og = foto.crop((izq, arr, izq + 1200, arr + 630)).convert("RGBA")
    og = Image.alpha_composite(og, Image.new("RGBA", og.size, (242, 242, 237, 175)))

    marca = Image.open(LOGO_LOCKUP).convert("RGBA")
    marca.thumbnail((620, 620), Image.LANCZOS)
    og.paste(marca, ((1200 - marca.width) // 2, (630 - marca.height) // 2), marca)

    d = SALIDA / "og-metclinic.jpg"
    og.convert("RGB").save(d, "JPEG", quality=86, optimize=True, progressive=True)
    print(f"  {d.stat().st_size // 1024:>5} KB  og-metclinic.jpg (1200x630)")


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
          f"ahorro {(antes-despues)/1024/1024:.1f} MB\n")
    generar_favicon()
    generar_og()
    generar_retratos()


if __name__ == "__main__":
    main()
