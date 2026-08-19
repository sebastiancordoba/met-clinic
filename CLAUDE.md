# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Static marketing site for **MET Clinic** (Dra. Melina Trujillo — gynecological aesthetics & antiaging). No build step, no framework: plain HTML + CSS + vanilla JS served directly by GitHub Pages.

## Deployment

GitHub Pages serves from the `gh-pages` branch (not `main`). Deploy is a force push, no CI:

```bash
git push origin main:gh-pages --force
```

Live URL: https://sebastiancordoba.github.io/met-clinic/

There is no build, lint, or test pipeline. To preview locally, just open `index.html` in a browser (or `python3 -m http.server` from the repo root if `file://` blocks fonts/images).

## PDF generation (one-off tool)

`generate-pdf.mjs` is a Puppeteer script that screenshots each `.proposal .mockup` block in `propuestas.html` and assembles them into `propuestas_paletas_colores.pdf`. It is not part of the site — it's a brand-deliverable generator.

```bash
npm install            # installs puppeteer
node generate-pdf.mjs
```

## File map (what each top-level file is for)

- `index.html` — the live site. **All CSS lives inline in `<style>`.** ~1000 lines of HTML + ~1500 lines of CSS in one file is intentional; do not split it unless asked.
- `main.js` — runtime behavior for `index.html` only (nav, carousel, scroll-reveal, counters, hamburger). Loaded as a plain `<script>`, no modules.
- `style.css` + `script.js` — **legacy v1 assets**, no longer referenced by `index.html`. Don't edit them unless explicitly asked; the live site uses inline styles + `main.js`.
- `brand-explorer.html`, `propuestas.html`, `propuestas-print.html` — internal design artifacts (brand exploration, palette/typography proposals). Self-contained pages; not linked from `index.html`.
- `images/web/` — **las versiones que sirve el sitio**: WebP redimensionado desde los originales de `BRANDING/` y de la raíz. Se generan con `optimizar-imagenes.py`; nunca se editan a mano.
- `BRANDING/webfonts/` — las tipografías en WOFF2, generadas con `optimizar-fuentes.py`. El HTML y `pilares.css` cargan éstas, no las OTF.
- `clinic.png`, `foto_jardin.png` — **originales**, no los referencia el sitio. Viven aquí como fuente para regenerar las derivadas.
- `images/servicios/` — the six service-card photos (`01-…` through `06-…`), referenced by `index.html`.
- `BRANDING/` — source brand assets (fonts, palettes, logos). Fonts here are loaded via `@font-face` in the HTML files using their on-disk paths — **the `BRANDING/` directory ships with the site**, so don't rename or move files inside it without updating every `@font-face` and `<img>` src that points to them.
- `Dra Melina Trujillo.pdf` — source of truth for medical bio, credentials, associations, and service names. When the user says "use what's in the PDF," this is the file.

## index.html architecture

Section order (anchors used by nav links and `main.js` smooth-scroll):

```
#hero  →  #sobre-block ( #sobre + #asociaciones )  →  #servicios  →  #cita
       →  #filosofia (.is-dark)  →  #testimonios  →  #contacto  →  <footer>
```

Things worth knowing before editing:

- **Nav offset is 68px.** Fixed nav height is hardcoded; smooth-scroll in `main.js` subtracts 68, and several sections size themselves to `calc(100dvh - 68px)`. If you change nav height, hunt down all three.
- **`.is-dark` sections** flip the nav to a dark theme on scroll. `main.js` measures their offsets on load + resize and toggles `nav.dark-section` based on whether the nav midpoint is inside one. Adding a new dark section is just `class="is-dark"` — no JS change needed.
- **One-screen layout pattern.** `#sobre-block` and `#servicios` are constrained to `height: calc(100dvh - 68px)` and use flex column children with `flex:1 / min-height:0` so content fills exactly one viewport. Be careful with padding/margins inside them — small additions overflow and clip.
- **Brand tokens** live in `:root` (`--sage`, `--tranquil`, `--confort`, `--dark`, `--font`, `--ease`). Use these instead of hex values.

### Services carousel (`#svcCarousel` + IIFE in `main.js`)

The trickiest piece. There are 6 real cards; the IIFE clones 2 in front and 3 behind for seamless looping, then auto-advances every 4s with a snap-back when it reaches the clone of card 0.

- **Desktop:** active card is 10/12 of the container width, with 1/12 peek on each side. Centering uses `translateX(-cur * w + (C - w) / 2)` where `C = container width`, `w = card width`. Edge fades (`::before` / `::after`) are desktop-only (`min-width: 641px`).
- **Mobile (≤640px):** one card at full width, no peek, no fades. The `isDesktop()` check in `cw()` and `render()` switches modes; both must stay in sync.
- Card states: `s-active` (centered), `s-side` (peeking, desktop only), `s-hidden` (everything else). CSS dims/sides accordingly.

### CTAs

The hero and `#contacto` buttons go to Doctoralia (booking) and WhatsApp — these are real production links, not placeholders. Don't replace them with form submissions.

## Peso de la página

Los archivos de `BRANDING/` son de imprenta: `MET_POSITIVO_04.png` mide 11117x4501 px y el nav lo pinta a 40 px. Servidos tal cual, la primera visita costaba **7.9 MB**; con las derivadas de `images/web/` y las WOFF2 baja a **~960 KB**.

Dos scripts, ambos reproducibles y con la lista de tamaños dentro:

```bash
python3 optimizar-imagenes.py   # BRANDING/ + raíz → images/web/*.webp
python3 optimizar-fuentes.py    # OTF → BRANDING/webfonts/*.woff2
```

Si se reemplaza un logo o una foto, se cambia el **original** y se vuelve a correr el script. Las derivadas no se editan: la próxima corrida las sobreescribe.

Los `.webp` van sin fallback a PNG a propósito — lo soportan todos los navegadores desde hace años y un `<picture>` por cada logo no compensa.

## Conventions

- **Spanish UI copy.** Site is in es-MX. Match tone (formal "usted" is avoided; warm clinical voice).
- **Inline styles in `index.html`.** Don't extract to a separate stylesheet — the current setup is deliberate for GitHub Pages simplicity.
- **No frameworks, no bundler, no npm runtime deps.** `package.json` only carries `puppeteer` for the PDF script. Don't add React/Vue/Tailwind/etc.
- **File paths with spaces:** the repo lives under iCloud (`~/Library/Mobile Documents/com~apple~CloudDocs/...`). Always quote paths in shell commands. Note also that the `BRANDING/DRA. MT/` directory has a space and a period in its name and is referenced from `@font-face` URLs — leave it alone.
- **PDF + heavy assets** are gitignored (`.gitignore` excludes `*.pdf`), but `Dra Melina Trujillo.pdf` and `propuestas_paletas_colores.pdf` are tracked historically; check `git status` before committing large binaries.
