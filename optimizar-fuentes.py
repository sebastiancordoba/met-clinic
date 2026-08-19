#!/usr/bin/env python3
"""Genera las WOFF2 de las tipografías de marca en `BRANDING/webfonts/`.

Los archivos de `BRANDING/` son OTF de escritorio: pesan el triple de lo
necesario y ningún navegador los prefiere. Las tres familias suman 702 KB en
OTF y 240 KB en WOFF2.

Se convierten TODOS los pesos que el CSS declara —los siete de Metropolis se
usan de verdad, del 100 al 700— así que aquí no hay nada que podar.

Requiere fontTools con soporte woff2 (necesita brotli).
Uso: python3 optimizar-fuentes.py
"""
from pathlib import Path
from fontTools.ttLib import TTFont

SALIDA = Path("BRANDING/webfonts")
MET = Path("BRANDING/METCLINIC/TIPOGRAFIAS")
DRA = Path("BRANDING/DRA. MT/02 Tipografía")

TRABAJOS = [
    (MET / "METROPOLIS-THIN.OTF",       "metropolis-100.woff2"),
    (MET / "METROPOLIS-EXTRALIGHT.OTF", "metropolis-200.woff2"),
    (MET / "METROPOLIS-LIGHT.OTF",      "metropolis-300.woff2"),
    (MET / "METROPOLIS-REGULAR.OTF",    "metropolis-400.woff2"),
    (MET / "METROPOLIS-MEDIUM.OTF",     "metropolis-500.woff2"),
    (MET / "METROPOLIS-SEMIBOLD.OTF",   "metropolis-600.woff2"),
    (MET / "METROPOLIS-BOLD.OTF",       "metropolis-700.woff2"),
    (DRA / "01 Primaria/Larken - Display Serif/Larken-Light.otf", "larken-300.woff2"),
    (DRA / "02 Secundaria/TT Commons/TT Commons Light.otf",   "ttcommons-300.woff2"),
    (DRA / "02 Secundaria/TT Commons/TT Commons Regular.otf", "ttcommons-400.woff2"),
    (DRA / "02 Secundaria/TT Commons/TT Commons Medium.otf",  "ttcommons-500.woff2"),
]


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    antes = despues = 0
    for origen, destino in TRABAJOS:
        if not origen.exists():
            print(f"  ✗ falta {origen}")
            continue
        f = TTFont(str(origen))
        f.flavor = "woff2"
        d = SALIDA / destino
        f.save(str(d))
        a, b = origen.stat().st_size, d.stat().st_size
        antes += a; despues += b
        print(f"  {a//1024:>4} KB → {b//1024:>3} KB  (−{100 - b*100//a:>2}%)  {destino}")
    print(f"\n  {antes//1024} KB → {despues//1024} KB   ahorro {(antes-despues)//1024} KB")


if __name__ == "__main__":
    main()
