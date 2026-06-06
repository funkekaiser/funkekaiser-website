# Funke-Kaiser Personal Landing

A simple single-page personal landing for Jonathan Funke-Kaiser. The hero shows a name, tagline, and four links — email, GitHub, LinkedIn, and CV — over a signature cursor-following gradient spotlight (a soft purple→teal field revealed by a radial mask that trails the mouse).

## Features
- **Cursor-following spotlight** – A blurred purple/teal gradient field is masked to a soft circle that smoothly trails the pointer; degrades gracefully under `prefers-reduced-motion`.
- **Theme-aware styling** – Matches the visitor's system light/dark preference via CSS custom properties and `prefers-color-scheme`.
- **Email with copy fallback** – The email row opens the default mail client (subject prefilled) and offers a copy-to-clipboard button with a "Copied" toast for webmail users.
- **Self-contained** – A single `index.html` with inlined CSS/JS and no runtime dependencies beyond Google Fonts.

## Build
There is no build step. The site is a single static `index.html` — edit it and refresh.

## Local development
Open `index.html` directly in a browser, or serve the folder with any static server:

```bash
npx serve .
```

Then open the reported URL (typically <http://localhost:3000>).

## Project structure
- `index.html` – The entire page: structure, inlined styles, and the spotlight + copy scripts.
- `Jonathan-Funke-Kaiser-CV.pdf` – CV linked from the page (opens in a new tab).
- `images/` – Favicons and the social-share card (`og-card.png`).
- `CNAME` – Custom domain (`funkekaiser.com`) for GitHub Pages.

## Deployment
The repository deploys to static hosting (e.g., GitHub Pages). Keep the `CNAME` file in the root so the custom domain stays active.
