#!/usr/bin/env python3
"""Sube al tema publicado de la tienda los archivos de la página que genera exportar-tema.py (regla de Hermes, 17-nov 13:09:
cada agente sube lo suyo, con respaldo y sin abrir la tienda al público).

Solo toca archivos de la página: sections/met-pg-*, templates/index.json y page.met-*, y los assets met-pagina*, met-pilares*,
met-pie*, met-mapa-pie.js y met-pg-*. Lo del tema (layout, header, footer-group, settings, met-tienda…) es de claude-1.

Antes de escribir:
  1. confirma que la tienda sigue tras la contraseña (met-clinic.myshopify.com → /password);
  2. confirma que el tema publicado es «MET · Cosmo (apple)» (190001086784);
  3. respalda la versión actual de cada archivo de texto en ~/hermes-workspace/reportes/tema-respaldos/<fecha-hora>/.

Uso (con el entorno de met-clinic-system, que trae el cliente de Shopify):
  ~/code/met-clinic-system/.venv/bin/python subir-tema.py --texto          # todos los de texto
  ~/code/met-clinic-system/.venv/bin/python subir-tema.py sections/met-pg-pie-global.liquid assets/met-pie.css.liquid
  … --binarios agrega también los met-pg-* (imágenes, fuentes, video). --prueba solo dice qué haría.
"""
import argparse
import datetime
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
TEMA = RAIZ / 'tema-shopify'
SISTEMA = Path.home() / 'code/met-clinic-system/src'
TEMA_ID = 'gid://shopify/OnlineStoreTheme/190001086784'
PROPIOS = ('sections/met-pg-', 'templates/index.json', 'templates/page.met-', 'assets/met-pagina', 'assets/met-pilares',
           'assets/met-pie', 'assets/met-burbuja', 'assets/met-mapa-pie.js', 'assets/met-pg-')
TEXTO = ('.liquid', '.json', '.js', '.css')


def tras_contrasena() -> bool:
    req = urllib.request.Request('https://met-clinic.myshopify.com/', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.geturl().rstrip('/').endswith('/password')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('archivos', nargs='*')
    ap.add_argument('--texto', action='store_true')
    ap.add_argument('--binarios', action='store_true')
    ap.add_argument('--prueba', action='store_true')
    a = ap.parse_args()

    lista = [l for l in (TEMA / 'ARCHIVOS.txt').read_text().split() if l]
    elegidos = list(a.archivos)
    if a.texto:
        elegidos += [f for f in lista if f.endswith(TEXTO)]
    if a.binarios:
        elegidos += [f for f in lista if not f.endswith(TEXTO)]
    elegidos = sorted(set(elegidos))
    ajenos = [f for f in elegidos if not f.startswith(PROPIOS)]
    if ajenos:
        sys.exit(f'No son archivos de la página (son de claude-1): {ajenos}')
    if not elegidos:
        sys.exit('Nada que subir.')

    if not tras_contrasena():
        sys.exit('ALTO: met-clinic.myshopify.com no cae en /password. No subo nada.')
    sys.path.insert(0, str(SISTEMA))
    from met_clinic_system.services.shopify import tema
    gid, nombre = tema.tema_principal()
    if gid != TEMA_ID:
        sys.exit(f'ALTO: el tema publicado es {nombre} ({gid}), no el esperado. No subo nada.')

    print(f'Tema {nombre} · tienda tras contraseña · {len(elegidos)} archivos')
    if a.prueba:
        print('\n'.join(elegidos))
        return

    respaldo = Path.home() / 'hermes-workspace/reportes/tema-respaldos' / datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
    textos = [f for f in elegidos if f.endswith(TEXTO)]
    for i in range(0, len(textos), 40):
        for f, c in tema.leer(gid, textos[i:i + 40]).items():
            p = respaldo / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(c)
    print(f'Respaldo: {respaldo}')

    subidos = []
    for i in range(0, len(elegidos), 8):
        lote = {}
        for f in elegidos[i:i + 8]:
            ruta = TEMA / f
            lote[f] = ruta.read_text() if f.endswith(TEXTO) else ruta.read_bytes()
        subidos += tema.escribir(gid, lote)
    print(f'Subidos: {len(subidos)}/{len(elegidos)}')
    faltan = set(elegidos) - set(subidos)
    if faltan:
        sys.exit(f'No se subieron: {sorted(faltan)}')


if __name__ == '__main__':
    main()
