# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npx serve .                  # local dev — MUST use a server, not file://
                             # (index.html loads the gallery as an ES module)
python3 update.py all        # fonts + CSP hashes
python3 update.py hashes     # regenerate CSP hashes in _headers  ← after ANY inline-script edit
python3 update.py validate   # read-only check; same command CI runs
python3 update.py fonts      # restore Geist woff2 from git, else download from unpkg
```

There is no build, no test suite, no linter, and no `node_modules`. `.claude/launch.json` serves the
same static site on port 4321.

## The CSP-hash contract

`_headers` pins every inline `<script>` in `index.html`, `impressum.html`, and `404.html` by SHA-256
so `script-src` needs no `'unsafe-inline'`. **Editing an inline script by even one byte silently
breaks the page in production** — the browser blocks the script. Always run `python3 update.py hashes`
in the same change, and commit `_headers` alongside the HTML.
`.github/workflows/validate-csp-hashes.yml` runs `update.py validate` on every push to `main` that
touches those four files.

`style-src` deliberately keeps `'unsafe-inline'` (the inlined `<style>` blocks are large and churn
often). JSON-LD and `src=` scripts are skipped by the hasher. `static.cloudflareinsights.com` in
`script-src` / `connect-src` is required by Cloudflare Web Analytics.

## Architecture

**Three standalone HTML pages, each fully self-contained.** `index.html` (landing), `impressum.html`
(German Impressum + Datenschutz), `404.html` (Cloudflare Pages serves it for unmatched routes). The
shared foundation — `@font-face` rules, theme tokens, reset, a11y utilities — is *duplicated* into the
`<head>` of each page rather than extracted into a stylesheet, to drop the one render-blocking CSS
request. **Editing fonts or theme values means editing all three pages.** `og-card.html` is a
throwaway source for the 1200×630 social PNG, not a served page.

**Theme is three-state.** Bare `:root` holds the light palette; `@media (prefers-color-scheme: dark)
{ :root:not([data-theme]) { … } }` overrides it for system-dark; `:root[data-theme="light"|"dark"]`
lets the toggle win in both directions. A tiny pre-paint script in `<head>` reads `localStorage`
key `fk-theme` and stamps `data-theme` before first paint to avoid a flash. New color tokens must be
defined in all three blocks or the toggle will half-apply.

**Cluster identity ties the links to the canvas.** Each of the five links carries `data-cluster="0"`–
`"4"` (email, GitHub, LinkedIn, tools, Impressum) and there is a matching `--c0`–`--c4` token pair
(light/dark). The inline `<script type="module">` at the bottom of `index.html` is the adapter
between the page and the engine: it maps `[data-cluster]` elements into an array, drives
`gallery.setHover(k)` on link hover, and paints the hovered link from `gallery`'s `onHover` callback.
Adding or removing a link means updating the index range, the `--cN` tokens, and the `:hover` /
`:focus-within` rules together.

**The classifier engine is a submodule, not site code.** `vendor/ml-on-canvas/` is the
[ml-on-canvas](https://github.com/funkekaiser/ml-on-canvas) repo. Never edit the vendored copy —
change the engine in its own repo, then bump here:

```bash
git submodule update --remote vendor/ml-on-canvas && git commit -am "bump ml-on-canvas"
```

The site touches only its public surface: `createGallery(canvas, opts)` and `ALGORITHMS`. The adapter
passes a `placement` function (keeps the point clouds right of the text column on wide viewports),
`tapIgnore`, `onStatus` (feeds the algorithm readout pill), and `onHover`; it re-calls
`gallery.setTheme()` from a `MutationObserver` on `data-theme` plus a `prefers-color-scheme` listener.
Clone with `--recurse-submodules`.

**No email address in plaintext markup.** Cloudflare's email obfuscation rewrites the `mailto:` href
at runtime; the copy button reads the decoded address back out of the row's `a[href^="mailto:"]` at
click time. Don't "fix" this by hardcoding the address.

## Deployment

Cloudflare Pages, no build step, root output directory. Keep `CNAME` (`funkekaiser.com`) at the root.
`robots.txt` disallows AI scrapers.

The page used to link a CV PDF that the Pages build command pulled from the CurriculumVitae repo's
rolling `latest` release. That repo is private now, so the build broke; the link was replaced with
`https://tools.jof.dev` and `Jonathan-Funke-Kaiser-CV.pdf` stays gitignored. **The build command
itself lives in the Cloudflare Pages dashboard, not in this repo** — it must be cleared there or
deploys keep failing on the release download.

## Re-rendering the social card

After editing `og-card.html`:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1200,630 --default-background-color=00000000 \
  --screenshot=images/og-card.png "file://$(pwd)/og-card.html"
```
