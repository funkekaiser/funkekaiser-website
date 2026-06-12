# Funke-Kaiser Personal Landing

A simple single-page personal landing for Jonathan Funke-Kaiser. The hero shows a name, tagline, and four links — email, GitHub, LinkedIn, and CV — over a signature animated background: a rotating gallery of real machine-learning classifiers, trained live in the browser on freshly spawned 2-D data.

## Features
- **Live ML classifier gallery** – A `<canvas>` background cycles through five classifiers trained in real time on freshly generated 2-D point clouds: k-means++, softmax regression, linear SVM (one-vs-rest), k-NN, and a gini decision tree. A small readout names the current algorithm and iteration. Each of the five page links owns one cluster, and hovering a link highlights its cluster (and vice versa). Under `prefers-reduced-motion` it renders a single static, fully-converged k-means frame instead of animating.
- **Theme-aware with manual toggle** – Follows the visitor's system light/dark preference via CSS custom properties and `prefers-color-scheme`, plus a toggle button that overrides it. The choice is persisted to `localStorage` (`fk-theme`) and applied before first paint to avoid a flash.
- **Email with copy fallback** – The email row opens the default mail client (subject prefilled) and offers a copy-to-clipboard button with a "Copied" toast for webmail users.
- **Self-contained** – Each page carries its own inlined CSS/JS with no runtime dependencies. Fonts (Geist, Geist Mono) are self-hosted as `woff2` — no external CDN — for speed and EU/GDPR compliance.

## Build
There is no build step. The site is static HTML — edit a file and refresh.

## Local development
Open `index.html` directly in a browser, or serve the folder with any static server:

```bash
npx serve .
```

Then open the reported URL (typically <http://localhost:3000>).

## Project structure
- `index.html` – The landing page: structure, inlined styles, and the classifier-gallery + theme-toggle + copy scripts.
- `impressum.html` – Combined Impressum & Datenschutz (German; §25 MedienG + DSGVO).
- `404.html` – Branded not-found page (Cloudflare Pages serves it for unmatched routes).
- `og-card.html` – Source for the 1200×630 social card; re-render to `images/og-card.png` after edits (see below).
- `Jonathan-Funke-Kaiser-CV.pdf` – CV linked from the page (opens in a new tab).
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
