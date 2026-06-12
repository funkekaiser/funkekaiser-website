# Funke-Kaiser Personal Landing

A simple single-page personal landing for Jonathan Funke-Kaiser. The hero shows a name, tagline, and four links — email, GitHub, LinkedIn, and CV — over a signature animated background: a rotating gallery of real machine-learning classifiers, trained live in the browser on freshly spawned 2-D data.

## Features
- **Live ML classifier gallery** – A `<canvas>` background cycles through five classifiers trained in real time on freshly generated 2-D point clouds: k-means++, softmax regression, linear SVM (one-vs-rest), k-NN, and a gini decision tree. A small readout names the current algorithm and iteration. Each of the five page links owns one cluster, and hovering a link highlights its cluster (and vice versa). Under `prefers-reduced-motion` it renders a single static, fully-converged frame instead of animating. The engine is its own project — [ml-on-canvas](https://github.com/funkekaiser/ml-on-canvas) — consumed here as a git submodule (`vendor/ml-on-canvas/`) and wired to the page by a small inline adapter in `index.html`.
- **Theme-aware with manual toggle** – Follows the visitor's system light/dark preference via CSS custom properties and `prefers-color-scheme`, plus a toggle button that overrides it. The choice is persisted to `localStorage` (`fk-theme`) and applied before first paint to avoid a flash.
- **Email with copy fallback** – The email row opens the default mail client (subject prefilled) and offers a copy-to-clipboard button with a "Copied" toast for webmail users.
- **Self-contained** – No external CDNs and no runtime dependencies: CSS/JS are inlined per page (plus the self-hosted gallery engine from the submodule), and fonts (Geist, Geist Mono) are served as local `woff2` for speed and EU/GDPR compliance.

## Build
`update.py` manages fonts and CSP hashes:
```
python3 update.py all       # Update fonts + hashes
python3 update.py fonts     # Restore/download fonts only
python3 update.py hashes    # Update CSP hashes only
python3 update.py validate  # Check hashes (read-only)
```

## Local development
Clone with the engine submodule, then serve the folder with any static server (the gallery is loaded as an ES module, so `file://` won't work for `index.html`):

```bash
git clone --recurse-submodules https://github.com/funkekaiser/funkekaiser-website
npx serve .
```

Then open the reported URL (typically <http://localhost:3000>).

### Updating the classifier engine
The gallery engine lives in [ml-on-canvas](https://github.com/funkekaiser/ml-on-canvas). After pushing a change there, pull it into the site with a submodule bump:

```bash
git submodule update --remote vendor/ml-on-canvas
git commit -am "bump ml-on-canvas"
```

## Project structure
- `index.html` – The landing page: structure, inlined styles, the site-chrome script (theme toggle, copy email), and the inline module adapter that mounts the classifier gallery.
- `vendor/ml-on-canvas/` – Git submodule of [ml-on-canvas](https://github.com/funkekaiser/ml-on-canvas), the zero-dependency classifier-gallery engine.
- `impressum.html` – Combined Impressum & Datenschutz (German; §25 MedienG + DSGVO).
- `404.html` – Branded not-found page (Cloudflare Pages serves it for unmatched routes).
- `og-card.html` – Source for the 1200×630 social card; re-render to `images/og-card.png` after edits (see below).
- `Jonathan-Funke-Kaiser-CV.pdf` – CV linked from the page (opens in a new tab). Not tracked in git: the Cloudflare Pages build command downloads it from the [CurriculumVitae](https://github.com/funkekaiser/CurriculumVitae) repo's rolling `latest` release, and that repo's CI pings a deploy hook here after each CV build.
- `fonts/` – Self-hosted Geist / Geist Mono `woff2` subsets (latin + latin-ext).
- `images/` – Favicon set, the social-share card (`og-card.png`), and `noise.svg` texture.
- `_headers` – Cloudflare Pages security headers.
- `robots.txt`, `sitemap.xml` – Crawl rules (AI scrapers disallowed) and the sitemap.
- `CNAME` – Custom domain (`funkekaiser.com`).

> The shared foundation (self-hosted `@font-face` rules, theme tokens, reset, a11y utilities) is inlined into the `<head>` of each HTML page rather than living in a separate stylesheet — this drops the one render-blocking CSS request. The tokens are duplicated across `index.html`, `impressum.html`, and `404.html`; keep them in sync when editing fonts or theme values.

## Re-rendering the social card
After editing `og-card.html`, regenerate the PNG with headless Chrome:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1200,630 --default-background-color=00000000 \
  --screenshot=images/og-card.png "file://$(pwd)/og-card.html"
```

## Deployment
The site deploys to **Cloudflare Pages** (no build step, root output directory). Keep `CNAME` in the root so the custom domain stays active.
