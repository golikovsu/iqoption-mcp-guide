# IQ Option · AI Integrations — MCP Connection Guide

A single-page guide that walks IQ Option users through connecting any
[Model Context Protocol](https://modelcontextprotocol.io) (MCP)–capable AI assistant — Claude,
ChatGPT, Cursor and 12+ others — to their trading account. One Bearer token, four market servers,
ready-made configs, permissions matrix, safety notes and an FAQ.

**Live site:** https://golikovsu.github.io/iqoption-mcp-guide/

---

## Highlights

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
├── index.html              # Semantic markup + JSON-LD structured data
├── assets/
│   ├── css/tokens.css      # QEDS-aligned design tokens
│   ├── css/styles.css      # Components, layout, motion, a11y layer
│   ├── js/main.js          # Tabs, copy, reveal, scroll chrome (progressive enhancement)
│   └── img/logo.png        # Logo (extracted from inline base64)
├── llms.txt                # Concise LLM-facing site map
├── llms-full.txt           # Full guide content as plain markdown for LLMs
├── robots.txt              # Crawl policy (AI crawlers explicitly allowed)
├── sitemap.xml
├── .nojekyll               # Serve files as-is on GitHub Pages
└── build_from_source.py    # One-shot transform from the original monolithic file (provenance)
```

## Run locally

No build step. Either open `index.html` directly, or serve it (recommended, so the clipboard API
and `fetch`-based assets behave like production):

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploy (GitHub Pages)

1. Push this folder to a GitHub repository named `iqoption-mcp-guide`.
2. In **Settings → Pages**, set the source to the `main` branch, root (`/`).
3. The site goes live at https://golikovsu.github.io/iqoption-mcp-guide/.

> Production URLs (canonical, Open Graph, `robots.txt`, `sitemap.xml`, `llms.txt`) are already set
> to `golikovsu.github.io/iqoption-mcp-guide`. If you fork or rename, update those references.

## Credits

- Design system: [QEDS](https://gnezdilovdenis.github.io/qeds/) by Denis Gnezdilov.
- Fonts: [Inter](https://rsms.me/inter/) and [JetBrains Mono](https://www.jetbrains.com/lp/mono/).
