"""Mapa ilustrado de #contacto: un SVG fijo dibujado con datos reales de OpenStreetMap, sin librería de mapas.

Pedido de Sebas (30-oct-2026, con una referencia): minimalista, fondo crema, calles principales en dos grosores,
parques en un tono pálido, sin nombres de calles ni controles. Unas cuantas referencias con punto anillado y un pin
de línea para la clínica. Pesa ~11 KB dentro del HTML y no llama a ningún servicio externo.

    python3 generar-mapa.py               # baja la zona de Overpass y reescribe el mapa en index.html
    python3 generar-mapa.py zona.json     # igual, con una descarga guardada

Solo usa la biblioteca estándar. Escribe entre las marcas `mapa-pie:inicio/fin` del pie de cada página (4-nov: el mismo
mapa con su tarjeta, más chico y con las calles más gruesas) : no edites ese bloque a mano.
El mapa grande de #contacto de la portada se quitó el 4-nov (Sebas: «se queda solo el del pie»). Las calles se comparten en un <g> y hay dos encuadres con sus etiquetas: el ancho de compu
y el vertical de teléfono. Se usa `meet` y las calles se pasan del encuadre: así ninguna etiqueta se corta y el mapa
llena la caja, mida lo que mida. El crédito a OpenStreetMap es obligatorio (licencia ODbL): no lo quites.
"""
import json
import math
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# La clínica (las coordenadas que geocodifica Google para Guty Cárdenas 65) es el origen.
LAT0, LON0 = 19.3580013, -99.1890269
M_LON = 111320 * math.cos(math.radians(LAT0))
M_LAT = 110574
M_POR_U = 4  # 1 unidad del viewBox = 4 m

ZONA = "19.335,-99.215,19.380,-99.165"
CONSULTA = f"""[out:json][timeout:120];
(
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential)$"]({ZONA});
  way["leisure"~"^(park|garden)$"]({ZONA});
  relation["leisure"~"^(park|garden)$"]({ZONA});
);
out body geom;"""

# Las calles gruesas, en orden: de cada una se queda una sola línea aunque tenga dos sentidos o laterales.
GRUESAS = [
    "Avenida Insurgentes Sur", "Avenida Revolución", "Anillo Periférico", "Avenida Barranca del Muerto",
    "Avenida Altavista", "Avenida Santa Catarina", "Avenida Miguel Ángel de Quevedo", "Avenida Río Mixcoac", "Circuito Interior Río Mixcoac",
    "Avenida Universidad",
]
# Las delgadas: secundarias y terciarias, las calles locales largas (dan la trama sin llenar el mapa) y la de la clínica.
DELGADAS_TIPOS = {"primary", "secondary", "tertiary", "motorway", "trunk"}
DELGADAS_NOMBRES = {"Calle Guty Cárdenas"}
LOCAL_MIN_M = 520
SUELTO_MAX_M = 700  # un tramo delgado más corto que esto, con una punta al aire, se quita

PARQUE_MIN_M2 = 7000  # menos que esto son plazas chicas, que ensucian alrededor de San Ángel
CERCA_GRUESA_M, CERCA_DELGADA_M = 55, 38  # a menos de esto, es la misma calle (otro sentido, lateral)
TRAMO_MIN_M = 170
SIMPLIFICA_M = 7

# Encuadres: (x, y, ancho, alto) en unidades, con la clínica en (0, 0).
ANCHO = (-700, -172, 1100, 625)
MOVIL = (-215, -150, 660, 570)
# Hasta dónde se dibuja: de sobra, para que con `meet` la caja nunca muestre el final de las calles.
CORTE = (-1150, -560, 1000, 800)  # x mín, y mín, x máx, y máx

# Las referencias, con coordenadas de OpenStreetMap (nodo o centro del lugar).
METRO = (19.36155, -99.18926)
PLAZA_INN = (19.35223, -99.18727)
ALTAVISTA = (19.34888, -99.18974)  # Pabellón Altavista, sobre la avenida
SAN_ANGEL = (19.34464, -99.19241)
# Ruta a pie Metro → clínica (OSRM peatón, 466 m, ~6 min), con el último tramo hasta la puerta.
RUTA = [(19.361545, -99.189188), (19.361514, -99.189192), (19.360622, -99.189305), (19.360269, -99.189348),
        (19.360328, -99.18927), (19.360149, -99.188611), (19.358649, -99.188788), (19.357985, -99.188861), (LAT0, LON0)]

# El del pie (4-nov, Sebas: «haz este mapa más pequeño y mételo así igual al footer», con las calles más gruesas):
# una franja ancha y baja en compu, con la tarjeta encima a la izquierda y la clínica a la derecha de ella.
PIE_ANCHO = (-1100, -150, 1900, 560)

PIE_INICIO, PIE_FIN = "<!-- mapa-pie:inicio", "<!-- mapa-pie:fin -->"
APPLE = "https://maps.apple.com/?q=MET+Clinic&amp;ll=19.3580013,-99.1890269&amp;address=Guty+C%C3%A1rdenas+65,+Guadalupe+Inn,+01020+CDMX"
WAZE = "https://waze.com/ul?ll=19.3580013,-99.1890269&amp;navigate=yes"
BUSCA = "https://www.google.com/maps/search/?api=1&amp;query=Guty+C%C3%A1rdenas+65%2C+Guadalupe+Inn%2C+01020+CDMX"
GOOGLE = "https://www.google.com/maps/dir/?api=1&amp;destination=MET+Clinic%2C+Guty+C%C3%A1rdenas+65%2C+Guadalupe+Inn%2C+01020+CDMX"


def u(lat, lon):
    return (lon - LON0) * M_LON / M_POR_U, (LAT0 - lat) * M_LAT / M_POR_U


def largo(p):
    return sum(math.dist(a, b) for a, b in zip(p, p[1:])) * M_POR_U


def simplifica(p, tol):
    """Douglas-Peucker. Un contorno cerrado se parte en dos: sus puntas coinciden y no habría recta contra qué medir."""
    if len(p) < 3:
        return p
    if p[0] == p[-1]:
        m = len(p) // 2
        return simplifica(p[: m + 1], tol)[:-1] + simplifica(p[m:], tol)
    (x1, y1), (x2, y2) = p[0], p[-1]
    dx, dy = x2 - x1, y2 - y1
    norma = math.hypot(dx, dy) or 1
    i_max, d_max = 0, -1
    for i in range(1, len(p) - 1):
        d = abs(dy * (p[i][0] - x1) - dx * (p[i][1] - y1)) / norma
        if d > d_max:
            i_max, d_max = i, d
    if d_max <= tol:
        return [p[0], p[-1]]
    return simplifica(p[: i_max + 1], tol)[:-1] + simplifica(p[i_max:], tol)


def densa(p, paso=4.0):
    """Puntos cada `paso` unidades, para medir qué tan cerca corre una calle de otra."""
    r = [p[0]]
    for a, b in zip(p, p[1:]):
        n = max(1, int(math.dist(a, b) / paso))
        r += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    return r


class Malla:
    """Puntos ya dibujados, por cuadros, para buscar el más cercano sin recorrerlos todos."""

    def __init__(self, celda=20):
        self.celda, self.d = celda, defaultdict(list)

    def agrega(self, puntos):
        for q in puntos:
            self.d[(int(q[0] // self.celda), int(q[1] // self.celda))].append(q)

    def cercano(self, q, radio, salvo=()):
        cx, cy, n = int(q[0] // self.celda), int(q[1] // self.celda), int(radio // self.celda) + 1
        mejor, d_mejor = None, radio
        for i in range(cx - n, cx + n + 1):
            for j in range(cy - n, cy + n + 1):
                for o in self.d.get((i, j), ()):
                    d = math.dist(q, o)
                    if d < d_mejor and o not in salvo:
                        mejor, d_mejor = o, d
        return mejor


def encadena(vias):
    """Une los tramos de una misma calle que se tocan en sus puntas (respeta el sentido si es de un sentido)."""
    libres = {v["id"]: v for v in vias}
    por_inicio, por_fin = defaultdict(list), defaultdict(list)
    for v in vias:
        por_inicio[v["nodes"][0]].append(v["id"])
        por_fin[v["nodes"][-1]].append(v["id"])
    cadenas = []
    while libres:
        _, v = libres.popitem()
        nodos, geo = list(v["nodes"]), list(v["geo"])
        while True:
            sig = next((i for i in por_inicio[nodos[-1]] if i in libres), None)
            if sig is None:
                break
            w = libres.pop(sig)
            nodos += w["nodes"][1:]
            geo += w["geo"][1:]
        while True:
            ant = next((i for i in por_fin[nodos[0]] if i in libres), None)
            if ant is None:
                break
            w = libres.pop(ant)
            nodos = w["nodes"][:-1] + nodos
            geo = w["geo"][:-1] + geo
        cadenas.append(geo)
    return cadenas


def fuera(q):
    return not (CORTE[0] <= q[0] <= CORTE[2] and CORTE[1] <= q[1] <= CORTE[3])


def tramos_nuevos(cadena, malla, cerca_m):
    """Lo que la calle agrega a lo ya dibujado. Cada punta que se corta por cercanía se pega a la calle vecina."""
    radio = cerca_m / M_POR_U
    salida, actual, previo = [], [], None
    for q in densa(cadena):
        vecino = malla.cercano(q, radio)
        if vecino is None and not fuera(q):
            if not actual and previo is not None:
                actual.append(previo)
            actual.append(q)
            previo = None
        else:
            if actual:
                if vecino is not None:
                    actual.append(vecino)
                salida.append(actual)
                actual = []
            previo = vecino
    if actual:
        salida.append(actual)
    return [t for t in salida if largo(t) >= TRAMO_MIN_M]


def pega_puntas(tramos, contra, radio_m):
    """Si una punta queda a un paso de otra calle, la alarga hasta tocarla: en el mapa no deben quedar rayas al aire."""
    radio = radio_m / M_POR_U
    salida = []
    for t in tramos:
        cuerpo = set(densa(t))
        malla = Malla()
        for o in contra:
            if o is not t:
                malla.agrega(densa(o))
        t = list(t)
        for lado in (0, -1):
            punta = t[lado]
            # Solo si la calle ya iba hacia allá: pegarla hacia atrás deja un gancho.
            atras = next((q for q in (t[1:] if lado == 0 else t[-2::-1]) if math.dist(q, punta) > 8), None)
            vecino = malla.cercano(punta, radio, cuerpo)
            if vecino is None or atras is None or math.dist(vecino, punta) == 0:
                continue
            ida = (punta[0] - atras[0], punta[1] - atras[1])
            salto = (vecino[0] - punta[0], vecino[1] - punta[1])
            coseno = (ida[0] * salto[0] + ida[1] * salto[1]) / (math.hypot(*ida) * math.hypot(*salto))
            if coseno > 0.6:
                t = [vecino] + t if lado == 0 else t + [vecino]
        salida.append(t)
    return salida


def sin_sueltos(gruesas, delgadas, guty):
    """Quita los tramos delgados cortos con una punta al aire. La calle de la clínica se queda."""
    radio = 12 / M_POR_U
    while True:
        malla = Malla()
        for t in gruesas + delgadas:
            malla.agrega(densa(t))
        quedan = []
        for t in delgadas:
            cuerpo = set(densa(t))
            pegada = all(malla.cercano(q, radio, cuerpo) is not None for q in (t[0], t[-1]))
            if t in guty or largo(t) >= SUELTO_MAX_M or pegada:
                quedan.append(t)
        if len(quedan) == len(delgadas):
            return quedan
        delgadas = quedan


def num(v):
    return str(int(round(v)))


def curva(p):
    """Trazo suave: cuadráticas entre puntos medios, con enteros relativos para que pese poco."""
    enteros = [(int(round(x)), int(round(y))) for x, y in p]
    limpios = [enteros[0]]
    for q in enteros[1:]:
        if q != limpios[-1]:
            limpios.append(q)
    if len(limpios) < 2:
        return ""
    if len(limpios) == 2:
        (x0, y0), (x1, y1) = limpios
        return f"M{x0} {y0}l{x1 - x0} {y1 - y0}"
    d = [f"M{limpios[0][0]} {limpios[0][1]}"]
    cx, cy = limpios[0]
    for i in range(1, len(limpios) - 1):
        a, b = limpios[i], limpios[i + 1]
        mx, my = int(round((a[0] + b[0]) / 2)), int(round((a[1] + b[1]) / 2))
        d.append(f"q{a[0] - cx} {a[1] - cy} {mx - cx} {my - cy}")
        cx, cy = mx, my
    fin = limpios[-1]
    d.append(f"l{fin[0] - cx} {fin[1] - cy}")
    return re.sub(r" -", "-", "".join(d))


def anillos(el):
    """Contornos exteriores de un parque: el del way, o los de la relación ya unidos."""
    if el["type"] == "way":
        return [[(g["lat"], g["lon"]) for g in el["geometry"]]] if el.get("geometry") else []
    trozos = [[(g["lat"], g["lon"]) for g in m["geometry"]] for m in el.get("members", []) if m.get("role") == "outer" and m.get("geometry")]
    salida = []
    while trozos:
        a = trozos.pop()
        cambio = True
        while cambio and a[0] != a[-1]:
            cambio = False
            for i, b in enumerate(trozos):
                if b[0] == a[-1]:
                    a += b[1:]
                elif b[-1] == a[-1]:
                    a += b[-2::-1]
                elif b[-1] == a[0]:
                    a = b[:-1] + a
                elif b[0] == a[0]:
                    a = b[:0:-1] + a
                else:
                    continue
                trozos.pop(i)
                cambio = True
                break
        salida.append(a)
    return salida


def area_m2(p):
    a = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(p, p[1:] + p[:1]))
    return abs(a) / 2 * M_POR_U * M_POR_U


def base(datos):
    """El <g> con parques y calles."""
    vias = defaultdict(list)
    parques = []
    for el in datos["elements"]:
        t = el.get("tags", {})
        if t.get("leisure") in ("park", "garden"):
            for anillo in anillos(el):
                p = [u(*q) for q in anillo]
                if len(p) >= 4 and area_m2(p) >= PARQUE_MIN_M2 and not all(fuera(q) for q in p):
                    parques.append(simplifica(p, 5 / M_POR_U))
        elif el["type"] == "way" and "highway" in t and el.get("geometry"):
            nombre = t.get("name", "")
            if t["highway"] == "residential" and not nombre:
                continue
            if el["tags"].get("tunnel") == "yes":
                continue
            vias[nombre or f"_{el['id']}"].append({
                "id": el["id"], "nodes": el["nodes"], "tipo": t["highway"],
                "geo": [u(g["lat"], g["lon"]) for g in el["geometry"]],
            })

    malla = Malla()
    gruesas, delgadas = [], []
    for nombre in GRUESAS:
        tramos = [v for v in vias.get(nombre, []) if v["tipo"] != "residential"]
        for cadena in sorted(encadena(tramos), key=largo, reverse=True):
            nuevos = tramos_nuevos(cadena, malla, CERCA_GRUESA_M)
            for t in nuevos:
                malla.agrega(t)
            gruesas += nuevos
    resto, de_la_clinica = [], []
    for nombre, tramos in vias.items():
        if nombre in GRUESAS:
            continue
        principales = [v for v in tramos if v["tipo"] in DELGADAS_TIPOS or nombre in DELGADAS_NOMBRES]
        cadenas = encadena(principales)
        resto += cadenas
        if nombre in DELGADAS_NOMBRES:
            de_la_clinica += cadenas
        locales = [v for v in tramos if v["tipo"] == "residential" and nombre not in DELGADAS_NOMBRES]
        resto += [c for c in encadena(locales) if largo(c) >= LOCAL_MIN_M]
    guty = []
    # La calle de la clínica primero, para que ninguna otra se la coma.
    for cadena in de_la_clinica + sorted((c for c in resto if c not in de_la_clinica), key=largo, reverse=True):
        nuevos = tramos_nuevos(cadena, malla, CERCA_DELGADA_M)
        for t in nuevos:
            malla.agrega(t)
        delgadas += nuevos
        if cadena in de_la_clinica:
            guty += nuevos
    gruesas = pega_puntas(gruesas, gruesas, 200)
    n_guty = len(guty)
    delgadas_pegadas = pega_puntas(delgadas, gruesas + delgadas, 110)
    guty = [n for o, n in zip(delgadas, delgadas_pegadas) if o in guty]
    assert len(guty) == n_guty >= 1, "no salió la calle de la clínica"
    delgadas = sin_sueltos(gruesas, delgadas_pegadas, guty)

    tol = SIMPLIFICA_M / M_POR_U
    d_gruesas = "".join(curva(simplifica(t, tol)) for t in gruesas)
    d_delgadas = "".join(curva(simplifica(t, tol)) for t in delgadas)
    d_parques = "".join(curva(p) + "z" for p in parques)
    print(f"  {len(gruesas)} tramos gruesos, {len(delgadas)} delgados, {len(parques)} parques")
    return (f'<g id="mapaBase" fill="none" stroke-linecap="round" stroke-linejoin="round">'
            f'<path class="mp" d="{d_parques}"/><path class="md" d="{d_delgadas}"/><path class="mg" d="{d_gruesas}"/></g>')


def punto(q, r_fuera, r_dentro):
    x, y = u(*q)
    return (f'<circle class="mr" cx="{num(x)}" cy="{num(y)}" r="{r_fuera}"/>'
            f'<circle class="mn" cx="{num(x)}" cy="{num(y)}" r="{r_dentro}"/>')


def etiqueta(q, nombre, alto, separa):
    """Nombre a la derecha del punto."""
    x, y = u(*q)
    return f'<text class="mt" x="{num(x + separa)}" y="{num(y + alto * 0.36)}" font-size="{alto}">{nombre}</text>'


def pin(escala):
    """Pin de línea delgada con la punta en la clínica y el monograma adentro."""
    a, h = 26 * escala, 62 * escala
    r = a
    d = (f"M0 0C{num(-a * .35)} {num(-h * .28)} {num(-a)} {num(-h * .46)} {num(-a)} {num(-h + r)}"
         f"A{num(r)} {num(r)} 0 1 1 {num(a)} {num(-h + r)}C{num(a)} {num(-h * .46)} {num(a * .35)} {num(-h * .28)} 0 0z")
    lado = a * 1.34
    return (f'<g class="mapa__pin"><path class="mpin" d="{d}"/>'
            f'<image href="images/web/met-positivo-03.webp" x="{num(-lado / 2)}" y="{num(-h + r - lado * .41)}" '
            f'width="{num(lado)}" height="{num(lado * .82)}"/></g>')


def ruta():
    return '<path class="mru" d="M' + "L".join(f"{num(x)} {num(y)}" for x, y in (u(*q) for q in RUTA)) + '"/>'


def encuadre(clase, caja, capas):
    return (f'<svg class="mapa__svg {clase}" viewBox="{caja[0]} {caja[1]} {caja[2]} {caja[3]}" '
            f'preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false">'
            f'<use href="#mapaBase"/>{capas}</svg>')


def capas(alto, r_fuera, r_dentro, separa, escala_pin, alto_clinica):
    refs = "".join(punto(q, r_fuera, r_dentro) + etiqueta(q, n, alto, separa=separa)
                   for q, n in ((METRO, "METRO BARRANCA DEL MUERTO"), (PLAZA_INN, "PLAZA INN"), (ALTAVISTA, "ALTAVISTA"), (SAN_ANGEL, "SAN ÁNGEL")))
    x = round(36 * escala_pin)
    return ruta() + refs + pin(escala_pin) + f'<text class="mt mt--clinica" x="{x}" y="-30" font-size="{alto_clinica}">MET CLINIC</text>'


def bloque_pie(datos):
    """El del pie: el mismo mapa y la misma tarjeta, más chicos y con las calles más gruesas (lo pone el CSS de .pie-mapa)."""
    return f"""    {PIE_INICIO} — lo escribe generar-mapa.py; no lo edites a mano -->
    <div class="pie-mapa">
      <div class="pie-mapa__tarjeta">
        <img class="mapa__logo" src="images/web/met-positivo-03.webp" alt="" width="64" height="26" loading="lazy">
        <p class="mapa__eyebrow">Cómo llegar</p>
        <p class="mapa__dir">Guty Cárdenas 65<br>Guadalupe Inn, Álvaro Obregón<br>CDMX 01020</p>
        <ul class="mapa__refs">
          <li><span class="mapa__m" aria-hidden="true">M</span>6 min a pie del Metro Barranca del Muerto · Línea 7</li>
          <li><svg class="mapa__i" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3 5 21M16 3l3 18M12 4v3M12 10.5v3M12 17v3"/></svg>A una calle de Av. Revolución</li>
          <li><svg class="mapa__i" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg><a href="tel:+525540099923">55 4009 9923</a></li>
        </ul>
        <a class="btn-primary mapa__ir js-mapa-ir" target="_blank" rel="noopener" href="{GOOGLE}">Cómo llegar</a>
        <p class="mapa__apps">Abrir en
          <a target="_blank" rel="noopener" href="{BUSCA}">Google Maps</a> ·
          <a target="_blank" rel="noopener" href="{APPLE}">Apple Maps</a> ·
          <a target="_blank" rel="noopener" href="{WAZE}">Waze</a>
        </p>
      </div>
      <a class="mapa__enlace pie-mapa__enlace js-mapa-ir" target="_blank" rel="noopener" href="{GOOGLE}" aria-label="Mapa: cómo llegar a MET Clinic, Guty Cárdenas 65, Guadalupe Inn">
        <svg class="mapa__defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>{base(datos)}</defs></svg>
        {encuadre("mapa__svg--ancho", PIE_ANCHO, capas(25, 10, 4.5, 26, 1.3, 38))}
        {encuadre("mapa__svg--movil", MOVIL, capas(21, 11, 5, 22, 1.3, 36))}
        <span class="mapa__credito">© OpenStreetMap</span>
      </a>
    </div>
    {PIE_FIN}
"""


def reemplaza(s, inicio, fin, nuevo, sangria):
    a, b = s.index(sangria + inicio), s.index(fin) + len(fin) + 1
    return s[:a] + nuevo + s[b:]


def main():
    if len(sys.argv) > 1:
        datos = json.loads(Path(sys.argv[1]).read_text())
    else:
        pedido = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=urllib.parse.urlencode({"data": CONSULTA}).encode(),
            headers={"User-Agent": "metclinic-mapa/1.0"},
        )
        with urllib.request.urlopen(pedido, timeout=180) as r:
            datos = json.load(r)
    pie = bloque_pie(datos)
    for ruta_html in sorted(RAIZ.glob("*.html")):
        s = ruta_html.read_text(encoding="utf-8")
        if PIE_INICIO not in s:
            continue
        s = reemplaza(s, PIE_INICIO, PIE_FIN, pie, "    ")
        ruta_html.write_text(s, encoding="utf-8")
        print(f"  {ruta_html.name}: mapa del pie {len(pie.encode()) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
