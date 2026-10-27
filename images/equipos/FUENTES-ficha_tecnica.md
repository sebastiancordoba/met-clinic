# Equipos — fotos oficiales y ficha verificada (24-oct-2026)

Carpeta: `/private/tmp/claude-501/-Users-sebastiancordoba-code-met-clinic-system--claude-worktrees-tickets-plantillas-movil/395c1caf-c3b9-4c18-b4d7-5534c7c9f8be/scratchpad/equipos_fotos/`

Todos los recortes miden **636 × 1100** (igual que `sofwave.webp`), con fondo transparente y un margen del 3 %. Los equipos de piso van apoyados en el margen inferior, con una sombra de contacto suave. Los de mano van centrados y sin sombra. Cada uno tiene `.webp` (q90, 25–58 KB) y `.png`. `preview_<slug>.png` muestra el recorte sobre blanco, gris y negro. Todos se revisaron sin halos.
Los equipos anchos (Emsella, Dioxage, FRAXX, U225) llenan el ancho y quedan más bajos: es el costo de usar el mismo lienzo vertical.

Scripts (reproducibles): `scripts/hacer.py <slug>` llama a `bgmatte.py` (máscara sobre fondo liso, sin modelos externos) y luego a `finalize.py` (descontaminación del borde, sombra y lienzo). Las descargas, sin tocar, están en `descargas/<equipo>/`, cada una con su `fuentes.txt`.

---

## 1. Asirox — `asirox.webp` ✅

- **Título:** Asirox
- **Marca:** Asirox (Asirox Aesthetic, Barcelona, España; ISO 13485)
- **Modelo:** **Asirox EVOLVE**. El distribuidor en México (Odella, odella.mx/asirox) vende la línea con el logotipo «Asirox EVOLVE». La torre negra con pantalla táctil y el portapieza arriba coincide con el render del folleto EVOLVE. El otro equipo actual de Asirox, el INITIA+, es blanco. Conviene confirmar contra la placa del equipo.
- **Especificaciones** (folleto EVOLVE de Lynton Lasers, distribuidor exclusivo de Asirox en Reino Unido): diodo de 800–810 nm, spot de 10×10 mm, 1–40 J/cm², pulso de 10–100 ms, 1–4 Hz en modo estándar y 5/10 Hz en modo Motion, enfriamiento por agua, punta a −8 °C.
- **Consumible:** **no**. Odella: «no requiere consumibles».
- **Contador de disparos:** no está documentado públicamente (ni en el folleto ni en el sitio). No se inventa.
- **Descripción:** Láser de diodo de 810 nm para depilación en todos los fototipos; spot de 10×10 mm, modo Motion de 5–10 Hz y punta enfriada a −8 °C.
- **Imagen:** render frontal del folleto oficial EVOLVE (imagen y smask del PDF): https://lynton.co.uk/wp-content/uploads/2022/06/2023-06-Lynton-Lasers_Evolve-brochure_A4_6pp_V12-1.pdf (Asirox no publica la foto del EVOLVE en asirox.com, que hoy sólo muestra el INITIA+).

## 2. MonaLisa Touch — `monalisa.webp` ✅ (fuente de baja resolución)

- **Título:** MonaLisa Touch
- **Marca:** DEKA (DEKA M.E.L.A., Calenzano, Italia; grupo El.En.)
- **Modelo:** el equipo es el **SmartXide Touch** (configuración V²LR), un láser de CO₂ RF de 10,600 nm y 0–60 W con escáner HiScan V²LR (8×8 mm). MonaLisa Touch es el procedimiento y la sonda. Ficha técnica: folleto oficial DEKA, rev. 7.1 (https://app.aico.swiss/19871/storage/files/Jg3RwPL2vl8Udktg2lq58eeqX2uEFwSMUxFmizvd.pdf).
- **Consumible:** **parcial**. La sonda vaginal de 360° es **autoclavable**, con versión **desechable opcional**. La sonda de 90° y el aplicador vulvar son opcionales. La pieza de RF Touch (para incontinencia y laxitud) es **de un solo uso**. Todo esto sale del mismo folleto.
- **Contador de disparos:** no está documentado públicamente.
- **Descripción:** Láser de CO₂ fraccionado (10,600 nm) con sonda vaginal de 360° y aplicador vulvar para atrofia vulvovaginal y síndrome genitourinario de la menopausia.
- **Imagen:** https://dekalaser.com/wp-content/uploads/2023/06/SmartXide-touch-V2LR-DEKA.png. Es oficial pero de sólo 800×800, así que el recorte se ve algo suave. La versión de 562×819 corta la base y el folleto trae la torre recortada arriba y abajo. Lynton ya asocia MonaLisa Touch con el equipo nuevo, Tetra Pro: hay que confirmar cuál tiene la clínica.

## 3. Emsella — `emsella.webp` ✅

- **Título:** Emsella
- **Marca:** BTL
- **Modelo:** silla más consola (render oficial «BTL_Emsella_PIC_Unit»).
- **Consumible:** **no**. El ícono «No Consumables» está en la página oficial: https://files.btlnet.com/aest/file_items/78f473a1-22f7-455a-85f0-9ff25c03b293/Emsella_ICON_No-Consumables_WEB_EN100_1782120127_original.png (página https://btlaesthetics.com/en/for-providers/emsella-providers).
- **Contador:** no está documentado públicamente.
- **Descripción:** Silla de campo electromagnético focalizado de alta intensidad (HIFEM) que provoca contracciones supramáximas del suelo pélvico, con la paciente vestida.
- **Imagen:** el color sale de https://files.btlnet.com/corp/file_items/80dae932-5f0e-4132-8b86-e68331ae0ed8/BTL_Emsella_PIC_Unit_1687349563_original.jpeg (2048 px) y el alfa del PNG oficial sin fondo https://files.btlnet.com/corp/file_items/3770ddb1-a8c9-4467-95d1-c1c2ca8f610c/BTL_Emsella_PIC_Unit_1687349563_original-no-bg_1750415015_original.webp. Las dos están en la página corporativa de BTL.

## 4. X-Wave — `xwave.webp` ✅ (fuente de baja resolución)

- **Título:** X-Wave
- **Marca:** BTL (nombre comercial «BTL X-Wave»)
- **Modelo:** el catálogo oficial BTL-X-WAVE_CAT_EN202 trae **tres** versiones: **X-WAVE Expert** (carro, combina ondas acústicas con electroestimulación), **X-WAVE Professional** (estacionario) y **X-WAVE Optimal** (portátil). El anuncio describe un carro blanco y azul con pieza de mano, así que se usó la **Expert**. Hay que confirmar con la clínica: la Professional también puede ir sobre un carro.
- **Especificaciones (Expert):** ondas acústicas radiales generadas por un proyectil de aire comprimido, hasta 22 Hz y 5 bar, pantalla táctil a color de 8.4″.
- **Consumible:** el catálogo no lo dice. Sólo menciona gel de acoplamiento. No se publica la vida útil del transmisor ni del proyectil.
- **Contador de disparos:** no está documentado en el catálogo de X-Wave.
- **Descripción:** Ondas acústicas radiales de proyectil neumático (hasta 22 Hz y 5 bar) para celulitis y laxitud cutánea; la versión Expert suma electroestimulación por la misma punta.
- **Imagen:** imagen y smask del catálogo oficial de BTL alojado por su distribuidor sudafricano: http://logique.co.za/wp-content/uploads/2014/08/BROCHURE-btl-x-wave_cat_en202_preview-englisch.pdf. Sólo mide 368×563 y se amplió 1.9×, por eso se ve suave. El marco naranja de la pantalla es real: así sale en el folleto. BTL ya retiró X-Wave de su sitio actual. Encontré la pieza de mano sola en 472 px (`descargas/xwave/live/x-wave-section-01_209_original.jpg`, files.btlnet.com), pero no el carro en mejor resolución.

## 5. Mesoject Gun — ❌ sin recorte

- **Título:** Mesoject Gun
- **Marca:** Toskani (TKN Mesojectgun, ToskaniMed, España)
- **Qué es:** **no es una pistola de agujas**. Es transdérmico, sin agujas: tecnología Pulse Booster® de pulsos eléctricos modulados que abren microcanales, más ondas de presión de baja frecuencia. Tiene consola de mesa con pantalla táctil y una pieza de mano (https://www.toskani.com/pages/tkn-mesoject-gun).
- **Consumible:** **sí**. Cabezales de **25 canales** (facial y corporal) y **22 canales** (capilar); la propia página dice «consumibles mínimos». Además se usan los activos (ampolletas).
- **Contador:** no está documentado públicamente.
- **Descripción:** Mesoterapia sin agujas: pulsos eléctricos modulados (Pulse Booster®) abren microcanales temporales para que penetren activos en rostro, cuerpo y cuero cabelludo.
- **Imagen:** **no existe una foto oficial del equipo completo sobre fondo liso**. En el sitio de Toskani sólo hay fotos de cabina (consola sobre una mesa, tapada por la paciente y las charolas) y acercamientos de la pieza de mano. El kit de prensa está en brandcenter.toskani.com y pide inicio de sesión. Habría que pedírselo a Toskani o al distribuidor. No se fabricó ninguna imagen.

## 6. U225 EVO — `u225.webp` ✅

- **Título:** U225 EVO
- **Marca:** Needle Concept (Francia). **Mesbio® es su marca de agujas**: la «TIP NEEDLE MESBIO U225» que tiene la clínica es del mismo fabricante.
- **Modelo:** U225® EVO, inyector intradérmico en versión **ginecológica** (zona vulvo-perineal y vaginal: vestíbulo, introito e intravaginal). Clase IIa, CE0459, ISO 13485, armado a mano en Francia. Profundidad ajustable de 1 a 10 mm, aguja separada de la jeringa. Fuente: https://www.needleconcept.fr/U225_EVO
- **Consumible:** **sí**. Agujas Mesbio (27G–34G, Luer Lock) y jeringas.
- **Contador:** no está documentado públicamente.
- **Descripción:** Inyector intradérmico para microinyecciones en la zona genital femenina, con profundidad ajustable de 1 a 10 mm y bloqueo que limita la pérdida de producto.
- **Imagen:** PNG oficial con transparencia: https://lirp.cdn-website.com/f8544de8/dms3rep/multi/opt/U225_EVO_by-_Needle_Concept-1920w.png. Se quitó el logotipo «U225 evo» que trae encima.

## 7. Dioxage — `dioxage.webp` ✅

- **Título:** Dioxage
- **Marca:** Skymedic (el fabricante legal es **HANS BIOMED S.L.**, Terrassa, Barcelona, que usa la marca Skymedic). Así lo dice el manual oficial de uso, V1 22/06/2026.
- **Modelo:** equipo de carboxiterapia con CO₂ calentado, 2 salidas simultáneas (A/B), flujo de 50 a 280 ml/min (máximo 150 ml/min con las dos salidas) y 3 programas automáticos. Hay versión de mesa y versión con pedestal: **el recorte es la de mesa**. Falta confirmar cuál tiene la clínica.
- **Consumible:** **sí**. **Cilindros de CO₂ médico** (99 % de pureza), **filtros estériles de 0.22 µm de un solo uso** (uno por salida, con aviso de cambio en pantalla) y agujas 30G.
- **Contador:** **sí, de volumen de gas, no de disparos**. Tiene un contador total y uno parcial que se reinicia con RESET. Lo dice el manual: https://skymedic.eu/storage/2026/07/USERS-MANUAL-V1-MDR-22-06-2026.pdf
- **Descripción:** Carboxiterapia: insufla CO₂ médico calentado por vía subcutánea, con flujo y presión controlados digitalmente (50–280 ml/min) y dos salidas simultáneas.
- **Imagen:** https://skymedic.eu/storage/2026/07/dioxage_1.png (página oficial https://skymedic.eu/en/carboxitherapy-device-dioxage/). Es un render sobreexpuesto: el contorno se reconstruyó con bordes. Se quitó la marca CE 1639 de la esquina.
- **Ojo regulatorio:** dioxage.com dice «certified by notified body 0476 for only the treatment of skin ulcers», mientras que la imagen nueva muestra CE 1639.

## 8. FRAXX — `fraxx.webp` ⚠️ el modelo puede NO coincidir con el de la clínica

- **Título:** FRAXX
- **Marca:** Loktal (Loktal Medical Electronics, São Paulo, Brasil). **No es un láser**: es **radiofrecuencia fraccionada (alta frecuencia) de 4 MHz**.
- **Modelo:** hay dos presentaciones oficiales:
  - **FRAXX System**: módulos apilados, con el **Megapulse HF FRAXX** arriba, la unidad electroquirúrgica **Wavetronic 6000 Touch** en medio y el evacuador de humo **Wavevac Dual** abajo. **Esto coincide con el «carro modular apilado» del anuncio.** La única imagen oficial es un volante de 624×871 (https://loktal.com/media/products/2020/08/27/fraxx-system.png) donde la torre mide unos 250 px. Es demasiado chica para un recorte digno, así que no se hizo. La página oficial del conjunto da 404.
  - **New FRAXX All in One**: un solo gabinete de mesa. Es el que se recortó, desde la lámina oficial de Loktal en alta resolución: https://loktal.com/media/products/product_246/7e656b471dfd8478494d463eccafce44.jpg (página https://loktal.com/acmp0005-megapulse-hf-fraxx).
- **Especificaciones** (loktal.com): 4.0 MHz, 100 W máximo. La energía se reparte en **64 micropuntos de 100 µm** con secuencia y tiempo de disparo ajustables, con control de impedancia de la piel (SIC). Además tiene modos de corte, coagulación y bipolar.
- **Consumible:** **sí**. Electrodos o puntas FRAXX (p. ej. la punta curva de 24 puntos; Loktal tiene una categoría «Eletrodos para FRAXX»). No se publica si son de un solo uso o reesterilizables.
- **Contador:** no está documentado públicamente.
- **Descripción:** Radiofrecuencia fraccionada de 4 MHz que deposita energía en 64 micropuntos para atrofia vaginal, laxitud y cicatrices, con control de impedancia de la piel.
- **Recomendación:** si la clínica tiene el FRAXX System apilado, **no uses `fraxx.webp`**. Pídele a Loktal (o a G&P / Loktal-GYP en México) el render del conjunto.

---

## Pendientes y dudas

1. **FRAXX**: falta confirmar si la clínica tiene el sistema apilado o el All in One (ver arriba).
2. **X-Wave**: falta confirmar Expert o Professional. Además el recorte sale de una fuente de 368 px y se ve suave.
3. **MonaLisa Touch**: falta confirmar SmartXide Touch o Tetra Pro. El recorte sale de una fuente de 800 px.
4. **Asirox**: falta confirmar EVOLVE contra la placa del equipo.
5. **Dioxage**: falta confirmar versión de mesa o de pedestal.
6. **Mesoject Gun**: no hay imagen. Hay que pedir el kit de prensa a Toskani.
7. **Contadores**: sólo Dioxage documenta un contador (de ml de CO₂). En ninguno de los demás encontré fuente pública de un contador de disparos ni de vida útil del consumible, así que no se afirmó.
