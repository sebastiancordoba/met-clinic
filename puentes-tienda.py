"""Fila «Para tu cuidado en casa» en cada página de tratamiento, con productos reales de la tienda.

Estrategia de Sebas (26-oct-2026): la página es para agendar y la tienda para comprar, pero se sienten como una
sola. Este es el puente de la página hacia la tienda; del lado de Shopify, el agente de la tienda pone el bloque
«Agenda una valoración».

Lee Shopify en SOLO LECTURA con el cliente de met-clinic-system (acuña y renueva su propio token; nunca lo
imprime), baja la foto principal de cada producto a images/web/tienda/<handle>.webp y escribe la fila entre las
marcas `puentes-tienda:inicio` y `puentes-tienda:fin` de cada pilar-*.html, al final de la sección Tratamientos.
Precio, nombre y foto quedan fijos hasta la siguiente corrida: córrelo de nuevo si cambian o antes de publicar.

    cd ~/code/met-clinic-system && poetry run python ~/code/met-clinic/puentes-tienda.py

QUÉ PRODUCTOS: la lista de abajo es PROVISIONAL. Sale del mapa de respaldo del agente de la tienda (etiquetas
`necesidad:*` de Shopify), elegidos a mano por existencias y por que vayan con el tratamiento. Cuando Sebas apruebe
las etiquetas curadas `pilar:*`, esta lista se cambia por esas etiquetas. Nunca: LUXMETIQUE (COFEPRIS) ni
medicamentos. Un producto sin existencias o archivado se salta solo; si a un pilar le quedan menos de 2, no se pinta
la fila.
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

PRODUCTOS = {
    "pilar-ginecologia.html": [
        "cumlaude-higiene-intima-diaria-origyn-500ml",
        "cumlaude-hidratante-interno-5ml",
        "cumlaude-hidratante-externo-crema-30-ml",
        "cumlaude-higiene-intima-deligyn-nf-500ml",
    ],
    "pilar-facial.html": [
        "filorga-hyalu-filler-serum",
        "cumlaude-gel-crema-firming-viderage",
        "filorga-time-filler-eyes-5xp-15ml",
        "svr-sun-secure-blur-protector-solar-en-mousse-fps50-50ml",
    ],
    "pilar-piel.html": [
        "filorga-daily-peel-anti-dark-spot",
        "svr-c20-biotic-crema-regeneradora-para-luminosidad-50ml",
        "rejuvaskin-gel-rejuvasil-15ml",
        "rejuvaskin-stretch-mark-cream-90ml",
    ],
    "pilar-corporal.html": [
        "sensilis-recovery-kit",
        "svr-crema-cicavit-100ml",
        "svr-xerial-10lait-leche-corporalhidratante-200ml",
    ],
    "pilar-capilar.html": [
        "lazartigue-thicker-suero-capilar-anticaida-50ml",
        "lazartigue-stronger-hair-serum-500ml",
        "lazartigue-nourish-shampoo-nutritivo-e-hidratante-250ml",
        "lazartigue-repair-mascarilla-250ml",
    ],
    "pilar-depilacion.html": [
        "svr-crema-cicavit-100ml",
        "svr-spray-cicavit-sos-grattage-40ml",
        "svr-sun-secure-blur-protector-solar-en-mousse-fps50-50ml",
    ],
    # Longevidad: solo hay 2 suplementos con existencias y no van con la página. Sin fila hasta que haya curados.
    "pilar-longevidad.html": [],
}

CONSULTA = """query($handle: String!) {
  productByHandle(handle: $handle) {
    handle title vendor status totalInventory
    featuredImage { url }
    priceRangeV2 { minVariantPrice { amount } }
    resourcePublicationsV2(first: 5) { nodes { isPublished publication { name } } }
  }
}"""

INICIO, FIN = "<!-- puentes-tienda:inicio", "<!-- puentes-tienda:fin -->"


def leer(handle: str) -> dict | None:
    p = client.execute(CONSULTA, {"handle": handle})["productByHandle"]
    if not p or p["status"] != "ACTIVE" or (p["totalInventory"] or 0) < 1 or not p["featuredImage"]:
        return None
    if "LUXMETIQUE" in (p["vendor"] or "").upper():
        return None
    # Publicado en la tienda en línea. No sirve `onlineStoreUrl`: viene vacío mientras la tienda tenga
    # contraseña, aunque el producto esté publicado (lo vio el agente de la tienda el 26-oct).
    canales = p["resourcePublicationsV2"]["nodes"]
    if not any(c["isPublished"] and c["publication"]["name"] == "Online Store" for c in canales):
        return None
    return p


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
    for pagina, handles in PRODUCTOS.items():
        productos = [p for p in (leer(h) for h in handles) if p]
        saltados = len(handles) - len(productos)
        if len(productos) < 2:
            escribir(pagina, "")
            print(f"  {pagina:24} sin fila ({len(productos)} producto(s) disponibles)")
            continue
        escribir(pagina, bloque([tarjeta(p) for p in productos]))
        print(f"  {pagina:24} {len(productos)} productos" + (f" ({saltados} saltados)" if saltados else ""))


if __name__ == "__main__":
    main()
