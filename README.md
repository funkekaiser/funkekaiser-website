# Funke-Kaiser Personal Landing

A simple single-page personal landing for Jonathan Funke-Kaiser. The hero shows a name, tagline, and four links — email, GitHub, LinkedIn, and CV — over a signature cursor-following gradient spotlight (a soft purple→teal field revealed by a radial mask that trails the mouse).

## Features
- **Cursor-following spotlight** – A blurred purple/teal gradient field is masked to a soft circle that smoothly trails the pointer; degrades gracefully under `prefers-reduced-motion`.
- **Theme-aware styling** – Matches the visitor's system light/dark preference via CSS custom properties and `prefers-color-scheme`.
- **Email with copy fallback** – The email row opens the default mail client (subject prefilled) and offers a copy-to-clipboard button with a "Copied" toast for webmail users.
- **Self-contained** – `index.html` carries its own inlined CSS/JS with no runtime dependencies. Fonts (Geist, Geist Mono) are self-hosted as `woff2` — no external CDN — for speed and EU/GDPR compliance.

## Build
There is no build step. The site is a single static `index.html` — edit it and refresh.

## Local development
Open `index.html` directly in a browser, or serve the folder with any static server:

```bash
npx serve .
```

Then open the reported URL (typically <http://localhost:3000>).

## Project structure
- `index.html` – The landing page: structure, inlined styles, and the spotlight + copy scripts.
- `impressum.html` – Combined Impressum & Datenschutz (German; §25 MedienG + DSGVO).
- `404.html` – Branded not-found page (Cloudflare Pages serves it for unmatched routes).
- `base.css` – Shared foundation: self-hosted `@font-face` rules, theme tokens, reset, a11y utilities.
- `og-card.html` – Source for the 1200×630 social card; re-render to `images/og-card.png` after edits (see below).
- `Jonathan-Funke-Kaiser-CV.pdf` – CV linked from the page (opens in a new tab).
- `fonts/` – Self-hosted Geist / Geist Mono `woff2` subsets.
- `images/` – Favicon set and the social-share card (`og-card.png`).
- `_headers` – Cloudflare Pages security headers.
- `robots.txt`, `sitemap.xml` – Crawl rules (AI scrapers disallowed) and the sitemap.
- `CNAME` – Custom domain (`funkekaiser.com`).

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
