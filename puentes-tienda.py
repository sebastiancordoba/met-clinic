"""Fila «Para tu cuidado en casa» en cada página de tratamiento, con productos reales de la tienda.

Estrategia de Sebas (26-oct-2026): la página es para agendar y la tienda para comprar, pero se sienten como una
sola. Este es el puente de la página hacia la tienda; del lado de Shopify, el agente de la tienda pone el bloque
«Agenda una valoración».

Lee Shopify en SOLO LECTURA con el cliente de met-clinic-system (acuña y renueva su propio token; nunca lo
imprime), baja la foto principal de cada producto a images/web/tienda/<handle>.webp y escribe la fila entre las
marcas `puentes-tienda:inicio` y `puentes-tienda:fin` de cada pilar-*.html, al final de la sección Tratamientos.
Nombre y foto quedan fijos hasta la siguiente corrida (sin precios: en la página solo va el de la consulta): córrelo de nuevo si cambian o antes de publicar.

    cd ~/code/met-clinic-system && poetry run python ~/code/met-clinic/puentes-tienda.py

QUÉ PRODUCTOS: los que llevan la etiqueta curada `pilar:<tratamiento>` en Shopify. La curó el agente de la tienda
con OK de Sebas (26-oct, ~18:55), por venta en mostrador y existencias; se cambia desde el admin de Shopify, no aquí.
Primero los `met:mas-elegido` y luego por existencias, hasta 4. Se saltan los que no estén activos, publicados en la
tienda en línea, con foto y con existencias. Nunca LUXMETIQUE (COFEPRIS) ni medicamentos (no están en Shopify).
Si a un pilar le quedan menos de 2, no se pinta la fila (hoy Longevidad).

PORTADA (26-oct, Sebas): franja chica «Lo más elegido por nuestras pacientes» al final de #preguntas, justo antes de
Contacto, con 4 productos de la etiqueta `met:mas-elegido` (8+ pacientes en mostrador; por eso no dice «lo que
usamos en consulta»). Uno por tratamiento, para que no salgan cuatro del mismo tipo: de los «más elegidos» que tienen
`pilar:*`, el de más existencias de cada pilar. Sin precios ni carrito: la portada es para agendar.
"""
import html
import io
import re
import sys
from pathlib import Path

import httpx
from PIL import Image

from met_clinic_system.services.shopify import client

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "images/web/tienda"

# Base de la tienda. El día del lanzamiento pasa a https://tienda.metclinic.com.mx (ver el checklist de dominio).
TIENDA = "https://met-clinic.myshopify.com"

PILARES = {
    "pilar-ginecologia.html": "ginecologia",
    "pilar-facial.html": "facial",
    "pilar-piel.html": "piel",
    "pilar-corporal.html": "corporal",
    "pilar-capilar.html": "capilar",
    "pilar-depilacion.html": "depilacion",
    "pilar-longevidad.html": "longevidad",
}
MAXIMO = 4

CONSULTA = """query($q: String!) {
  products(first: 50, query: $q) {
    nodes {
      handle title vendor status totalInventory tags
      featuredImage { url }
      resourcePublicationsV2(first: 5) { nodes { isPublished publication { name } } }
    }
  }
}"""

INICIO, FIN = "<!-- puentes-tienda:inicio", "<!-- puentes-tienda:fin -->"
P_INICIO, P_FIN = "<!-- puentes-portada:inicio", "<!-- puentes-portada:fin -->"


def vendible(p: dict) -> bool:
    if p["status"] != "ACTIVE" or (p["totalInventory"] or 0) < 1 or not p["featuredImage"]:
        return False
    if "LUXMETIQUE" in (p["vendor"] or "").upper():
        return False
    # Publicado en la tienda en línea. No sirve `onlineStoreUrl`: viene vacío mientras la tienda tenga
    # contraseña, aunque el producto esté publicado (lo vio el agente de la tienda el 26-oct).
    canales = p["resourcePublicationsV2"]["nodes"]
    return any(c["isPublished"] and c["publication"]["name"] == "Online Store" for c in canales)


def leer(pilar: str) -> list[dict]:
    nodos = client.execute(CONSULTA, {"q": f"status:active tag:'pilar:{pilar}'"})["products"]["nodes"]
    nodos = [p for p in nodos if vendible(p)]
    nodos.sort(key=lambda p: ("met:mas-elegido" not in p["tags"], -(p["totalInventory"] or 0)))
    return nodos[:MAXIMO]


def mas_elegidos() -> list[dict]:
    nodos = client.execute(CONSULTA, {"q": "status:active tag:'met:mas-elegido'"})["products"]["nodes"]
    nodos = sorted((p for p in nodos if vendible(p)), key=lambda p: -(p["totalInventory"] or 0))
    elegidos, pilares = [], set()
    for p in nodos:
        suyos = {t for t in p["tags"] if t.startswith("pilar:")}
        if suyos and not suyos & pilares:
            elegidos.append(p)
            pilares |= suyos
        if len(elegidos) == MAXIMO:
            break
    return elegidos


def franja_portada(productos: list[dict]) -> str:
    tarjetas = "".join(f"""            <a class="elegido" href="{TIENDA}/products/{p['handle']}">
              <span class="elegido__foto"><img src="{foto(p)}" alt="" width="480" height="480" loading="lazy" decoding="async"></span>
              <span class="elegido__marca">{html.escape(p['vendor'])}</span>
              <span class="elegido__nombre">{html.escape(nombre(p))}</span>
            </a>
""" for p in productos)
    return f"""    {P_INICIO} — lo escribe puentes-tienda.py; no lo edites a mano -->
    <div class="section-inner elegidos reveal">
      <div class="elegidos__texto">
        <p class="eyebrow">Boutique de la clínica</p>
        <h2 class="elegidos__titulo">Lo más elegido<br><em>por nuestras pacientes.</em></h2>
        <a class="elegidos__ver" href="{TIENDA}">Ver tienda →</a>
      </div>
      <div class="elegidos__fila">
{tarjetas}      </div>
    </div>
    {P_FIN}
"""


def escribir_portada(contenido: str) -> None:
    ruta = RAIZ / "index.html"
    s = ruta.read_text()
    s = re.sub(rf"    {re.escape(P_INICIO)}.*?{re.escape(P_FIN)}\n", "", s, flags=re.S)
    if contenido:
        # Al final de #preguntas, después de su rejilla, para no sumar una séptima sección.
        i = s.index('<section id="preguntas"')
        j = s.index("  </section>", i)
        s = s[:j] + contenido + s[j:]
    ruta.write_text(s)


def foto(p: dict) -> str:
    """Foto principal a 480 px (la tarjeta se pinta a ~220 px), en WebP, centrada en un cuadro blanco."""
    destino = SALIDA / f"{p['handle']}.webp"
    if not destino.exists():
        url = p["featuredImage"]["url"]
        url += ("&" if "?" in url else "?") + "width=600"
        # RGBA y pegado con su propia máscara: varias fotos son PNG transparentes y, convertidas
        # directo a RGB, el fondo salía negro.
        im = Image.open(io.BytesIO(httpx.get(url, timeout=30, follow_redirects=True).content)).convert("RGBA")
        im.thumbnail((440, 440), Image.LANCZOS)
        lienzo = Image.new("RGB", (480, 480), (255, 255, 255))
        lienzo.paste(im, ((480 - im.width) // 2, (480 - im.height) // 2), im)
        lienzo.save(destino, "WEBP", quality=80, method=6)
    return f"images/web/tienda/{p['handle']}.webp"


def nombre(p: dict) -> str:
    """El título sin la marca repetida al inicio (Shopify los guarda como «FILORGA Hyalu…» a veces)."""
    t = p["title"].strip()
    marca = (p["vendor"] or "").strip()
    if marca and t.upper().startswith(marca.upper() + " "):
        t = t[len(marca) + 1:]
    return t


def tarjeta(p: dict) -> str:
    # Sin precio (Sebas, 26-oct 19:30: «deja solo lo de consulta»): el único precio de la página es el de la
    # consulta; el de cada producto se ve en la tienda.
    return f"""          <a class="casa-producto" href="{TIENDA}/products/{p['handle']}">
            <span class="casa-producto__foto"><img src="{foto(p)}" alt="" width="480" height="480" loading="lazy" decoding="async"></span>
            <span class="casa-producto__marca">{html.escape(p['vendor'])}</span>
            <span class="casa-producto__nombre">{html.escape(nombre(p))}</span>
            <span class="casa-producto__ver">Ver en la tienda →</span>
          </a>
"""


def bloque(tarjetas: list[str]) -> str:
    return f"""      {INICIO} — lo escribe puentes-tienda.py; no lo edites a mano -->
      <div class="casa reveal">
        <div class="casa__cabeza">
          <div>
            <p class="pilar-intro__kicker">Cuidado en casa</p>
            <h2>Para tu cuidado <em>en casa.</em></h2>
          </div>
          <p class="casa__nota">Dermocosmética de la boutique de la clínica. En tu valoración te decimos cuál va contigo.</p>
        </div>
        <div class="casa__fila">
{''.join(tarjetas)}        </div>
        <a class="casa__todo" href="{TIENDA}">Ver toda la tienda →</a>
      </div>
      {FIN}
"""


def escribir(pagina: str, contenido: str) -> None:
    ruta = RAIZ / pagina
    s = ruta.read_text()
    s = re.sub(rf"      {re.escape(INICIO)}.*?{re.escape(FIN)}\n", "", s, flags=re.S)
    if contenido:
        # Al final de la sección Tratamientos: su </div> de .wrap y su </section>.
        i = s.index('<section class="treatments">')
        j = s.index("    </div>\n  </section>", i)
        s = s[:j] + contenido + s[j:]
    ruta.write_text(s)


def main() -> None:
    if not client.configurado():
        sys.exit("Falta configurar Shopify en met-clinic-system (.env).")
    SALIDA.mkdir(parents=True, exist_ok=True)
    usadas = set()
    for pagina, pilar in PILARES.items():
        productos = leer(pilar)
        if len(productos) < 2:
            escribir(pagina, "")
            print(f"  {pagina:24} sin fila ({len(productos)} producto(s) con pilar:{pilar})")
            continue
        escribir(pagina, bloque([tarjeta(p) for p in productos]))
        usadas |= {f"{p['handle']}.webp" for p in productos}
        print(f"  {pagina:24} {len(productos)}: " + ", ".join(p["handle"] for p in productos))
    elegidos = mas_elegidos()
    escribir_portada(franja_portada(elegidos) if len(elegidos) >= 2 else "")
    usadas |= {f"{p['handle']}.webp" for p in elegidos}
    print(f"  {'index.html (portada)':24} {len(elegidos)}: " + ", ".join(p["handle"] for p in elegidos))
    # Fotos de productos que ya no salen en ninguna fila.
    for viejo in SALIDA.glob("*.webp"):
        if viejo.name not in usadas:
            viejo.unlink()


if __name__ == "__main__":
    main()
