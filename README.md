# IQ Option · AI Integrations — MCP Connection Guide

A single-page guide that walks IQ Option users through connecting any
[Model Context Protocol](https://modelcontextprotocol.io) (MCP)–capable AI assistant — Claude,
ChatGPT, Cursor and 12+ others — to their trading account. One Bearer token, four market servers,
ready-made configs, permissions matrix, safety notes and an FAQ.

**Live site:** https://iqoptionmcp.com/

---

## Highlights

- **Localized into 7 languages.** English (default) + Arabic (RTL), Thai, Portuguese, Spanish,
  Tagalog and Indonesian. Each language is a server-rendered static page with its own URL,
  `hreflang` alternates, localized `<title>`/meta and JSON-LD, and an accessible language switcher.
- **Static, zero-build, zero-dependency.** Plain HTML/CSS/JS — open `index.html` and it works.
- **Design system.** Built on the [QEDS](https://gnezdilovdenis.github.io/qeds/) (Quadcode
  Enterprise Design System) dark theme, with QEDS-aligned design tokens.
- **Accessible.** WAI-ARIA tabs with full keyboard navigation, accessible checkboxes,
  `:focus-visible` rings, a skip link, live-region copy feedback, and `prefers-reduced-motion`
  support throughout.
- **Animated, tastefully.** Ambient hero gradient, staggered scroll reveals, a scroll-progress
  bar and a back-to-top control — all motion gated behind reduced-motion preferences.
- **Optimized for AI search (GEO).** Schema.org JSON-LD (`FAQPage`, `HowTo`, `TechArticle`,
  `Organization`, `WebSite`), Open Graph / Twitter cards, an [`llms.txt`](./llms.txt) +
  [`llms-full.txt`](./llms-full.txt), a `sitemap.xml`, and a `robots.txt` that explicitly welcomes
  AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, …).

## Project structure

```
iqoption-mcp-guide/
├── index.html              # English (default, canonical)
├── ar/ th/ pt/ es/ tl/ id/ # Localized pages (one index.html each)
├── assets/
│   ├── css/tokens.css      # QEDS-aligned design tokens
│   ├── css/styles.css      # Components, layout, motion, a11y + language switcher
│   ├── css/rtl.css         # Right-to-left overrides (Arabic)
│   ├── js/main.js          # Tabs, copy, reveal, scroll chrome, language switcher
│   └── img/logo.png        # Logo (extracted from inline base64)
├── i18n/
│   ├── en.json … id.json   # Per-language translation dictionaries
│   └── _map.json           # FAQ/HowTo key map for localized JSON-LD
├── template.html           # Generated template (placeholders) — input to the generator
├── llms.txt                # Concise LLM-facing site map (+ localized URLs)
├── llms-full.txt           # Full guide content as plain markdown for LLMs
├── robots.txt              # Crawl policy (AI crawlers explicitly allowed)
├── sitemap.xml             # All locales with hreflang alternates
├── .nojekyll               # Serve files as-is on GitHub Pages
├── build_from_source.py    # One-shot transform from the original monolithic file (provenance)
└── build_i18n.py           # i18n pipeline: extract strings → generate per-language pages
```

## Run locally

No runtime build step. Either open `index.html` directly, or serve it (recommended, so the
clipboard API and relative asset paths behave like production):

```bash
python3 -m http.server 8000
# then open http://localhost:8000  ·  /ar/  /th/  /pt/  /es/  /tl/  /id/
```

## Regenerate localized pages

The localized pages are generated from `template.html` + `i18n/<lang>.json`:

```bash
python3 build_i18n.py extract    # English index.html → template.html + i18n/en.json
# (edit/translate i18n/<lang>.json)
python3 build_i18n.py generate   # → per-language pages + sitemap.xml
```

## Deploy

**Production:** [Vercel](https://vercel.com), connected to this GitHub repo and served at
**https://iqoptionmcp.com/** (apex; DNS on Vercel). Every push to `main` triggers an automatic
redeploy. No build step — the static files are served as-is.

**Mirror (optional):** GitHub Pages can also serve the repo at
`https://golikovsu.github.io/iqoption-mcp-guide/` (branch `main`, root, `.nojekyll`). All absolute
URLs (canonical, Open Graph, `hreflang`, JSON-LD, `sitemap.xml`, `robots.txt`, `llms.txt`) point to
the canonical `https://iqoptionmcp.com`, so the mirror is canonicalized to the custom domain.

> If you fork, rename, or change the domain, update `BASE` in `build_i18n.py` and run
> `python3 build_i18n.py generate` to regenerate every page with the new URLs.

## Analytics

Visit + on-site event analytics live in [`assets/js/analytics.js`](assets/js/analytics.js).
It is **privacy-first and cookieless** (Plausible) — no consent banner required — and is fully
decoupled from the rest of the JS.

**Status: live.** It uses a Plausible site-specific script (`CONFIG.plausibleScript`). To point at
a different Plausible site, swap that URL; to turn analytics off, set `CONFIG.provider = 'none'`.
Set `CONFIG.respectDNT = true` to skip tracking for visitors with Do-Not-Track / Global Privacy
Control enabled. Every event is also mirrored to `window.__analytics` for in-console debugging.

**Tracked events** (each with useful properties):

| Event | When | Properties |
|-------|------|-----------|
| *(pageview)* | every page load | path encodes language (`/ar/`, `/th/`, …) |
| `Select Assistant` | assistant tab clicked | `assistant` |
| `Copy: Config` | a config snippet copied | `assistant` |
| `Copy: Server URL` | a server URL copied | `server` |
| `CTA: Click` | hero / step CTA clicked | `cta`, `lang` |
| `Switch Language` | language switcher used | `from`, `to` |
| `FAQ: Open` | an FAQ item expanded | `q` |
| `Outbound Link: Click` | external link clicked | `url` |
| `Scroll Depth` | 25 / 50 / 75 / 100 % reached | `percent` |

**Swap provider:** set `CONFIG.provider` to `'ga4'` (add `ga4Id` — note: GA4 uses cookies and needs a
consent banner in the EU/KSA) or `'umami'` (add `umami.src` + `umami.websiteId`). The event layer is
provider-agnostic — only the one `send()` shim changes.

## Credits

- Design system: [QEDS](https://gnezdilovdenis.github.io/qeds/) by Denis Gnezdilov.
- Fonts: [Inter](https://rsms.me/inter/) and [JetBrains Mono](https://www.jetbrains.com/lp/mono/).
