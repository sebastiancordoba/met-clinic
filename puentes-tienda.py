"""Fila «Para tu cuidado en casa» en cada página de tratamiento, con productos reales de la tienda.

Estrategia de Sebas (26-oct-2026): la página es para agendar y la tienda para comprar, pero se sienten como una
sola. Este es el puente de la página hacia la tienda; del lado de Shopify, el agente de la tienda pone el bloque
«Agenda una valoración».

Lee Shopify en SOLO LECTURA con el cliente de met-clinic-system (acuña y renueva su propio token; nunca lo
imprime), baja la foto principal de cada producto a images/web/tienda/<handle>.webp y escribe la fila entre las
marcas `puentes-tienda:inicio` y `puentes-tienda:fin` de cada pilar-*.html, al final de la sección Tratamientos.
Precio, nombre y foto quedan fijos hasta la siguiente corrida: córrelo de nuevo si cambian o antes de publicar.

    cd ~/code/met-clinic-system && poetry run python ~/code/met-clinic/puentes-tienda.py

QUÉ PRODUCTOS: los que llevan la etiqueta curada `pilar:<tratamiento>` en Shopify. La curó el agente de la tienda
con OK de Sebas (26-oct, ~18:55), por venta en mostrador y existencias; se cambia desde el admin de Shopify, no aquí.
Primero los `met:mas-elegido` y luego por existencias, hasta 4. Se saltan los que no estén activos, publicados en la
tienda en línea, con foto y con existencias. Nunca LUXMETIQUE (COFEPRIS) ni medicamentos (no están en Shopify).
Si a un pilar le quedan menos de 2, no se pinta la fila (hoy Longevidad).
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
      priceRangeV2 { minVariantPrice { amount } }
      resourcePublicationsV2(first: 5) { nodes { isPublished publication { name } } }
    }
  }
}"""

INICIO, FIN = "<!-- puentes-tienda:inicio", "<!-- puentes-tienda:fin -->"


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
    precio = f"${float(p['priceRangeV2']['minVariantPrice']['amount']):,.0f}"
    return f"""          <a class="casa-producto" href="{TIENDA}/products/{p['handle']}">
            <span class="casa-producto__foto"><img src="{foto(p)}" alt="" width="480" height="480" loading="lazy" decoding="async"></span>
            <span class="casa-producto__marca">{html.escape(p['vendor'])}</span>
            <span class="casa-producto__nombre">{html.escape(nombre(p))}</span>
            <span class="casa-producto__precio">{precio} <small>MXN</small></span>
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
    # Fotos de productos que ya no salen en ninguna fila.
    for viejo in SALIDA.glob("*.webp"):
        if viejo.name not in usadas:
            viejo.unlink()


if __name__ == "__main__":
    main()
