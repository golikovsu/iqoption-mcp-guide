#!/usr/bin/env python3
"""One-shot build: transform the monolithic guide into a clean, split, GEO-optimized site.
Run once from the project root. Safe to delete afterwards (kept in repo as build provenance)."""
import re, base64, html, json, os, sys

SRC = "/Users/sergey.golikov/CPO Report/Bi Weekly CPO Report/IQ Option · AI MCP Integration Guide.html"
BASE = "https://USERNAME.github.io/iqoption-mcp-guide"  # patched at deploy time

raw = open(SRC, encoding="utf-8").read()

style = re.search(r"<style>(.*?)</style>", raw, re.S).group(1)
body  = re.search(r"<body>(.*?)</body>", raw, re.S).group(1)

# ---- 1. logo: decode base64 -> file ----
m = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", raw)
png = base64.b64decode(m.group(1))
os.makedirs("assets/img", exist_ok=True)
open("assets/img/logo.png", "wb").write(png)

# ---- 2. split CSS into tokens + styles ----
root = re.search(r"(:root\s*\{.*?\})", style, re.S).group(1)
styles_body = style.replace(root, "", 1).strip()
tokens_body = root.strip()

# ---- 3. FAQ pairs -> FAQPage JSON-LD ----
def clean(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()

faq = [(clean(q), clean(a)) for q, a in
       re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", body, re.S)]

steps = [
    ("Create a token",
     "In the IQ Option mobile app or web: open Settings → AI integrations, tap + Add integration, "
     "name the token and set an expiry, tick which markets may trade (read is always on), then copy the "
     "token immediately — it is shown only once."),
    ("Pick your assistant",
     "Choose an AI client with native MCP support: Claude Desktop, Claude Code, Cursor, Windsurf, Zed, "
     "OpenAI Codex, ChatGPT Desktop, Cline, Continue.dev, Goose, Cherry Studio or LibreChat."),
    ("Paste the config",
     "Copy the ready-made snippet for your assistant. Each entry needs the server URL, an "
     "'Authorization: Bearer <token>' header, and a restart of the assistant."),
]

graph = [
    {"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/",
     "name": "IQ Option · AI Integrations",
     "description": "Connect any AI assistant to your IQ Option account via the Model Context Protocol.",
     "inLanguage": "en", "publisher": {"@id": f"{BASE}/#org"}},
    {"@type": "Organization", "@id": f"{BASE}/#org", "name": "IQ Option",
     "url": "https://iqoption.com", "logo": f"{BASE}/assets/img/logo.png"},
    {"@type": "TechArticle", "@id": f"{BASE}/#article",
     "headline": "Connect any AI assistant to IQ Option via MCP",
     "description": "One Bearer token, four market MCP servers (digital options, CFD, crypto, forex). "
                    "Ready-made configs for Claude, ChatGPT, Cursor and 12+ assistants. No code, three steps.",
     "inLanguage": "en", "isPartOf": {"@id": f"{BASE}/#website"},
     "author": {"@id": f"{BASE}/#org"}, "publisher": {"@id": f"{BASE}/#org"},
     "keywords": "IQ Option, MCP, Model Context Protocol, Claude, ChatGPT, Cursor, AI trading, "
                 "digital options, forex, crypto, CFD"},
    {"@type": "HowTo", "@id": f"{BASE}/#howto",
     "name": "How to connect an AI assistant to IQ Option",
     "description": "Connect any MCP-capable AI assistant to IQ Option in three steps.",
     "totalTime": "PT3M",
     "step": [{"@type": "HowToStep", "position": i + 1, "name": n, "text": t}
              for i, (n, t) in enumerate(steps)]},
    {"@type": "FAQPage", "@id": f"{BASE}/#faq",
     "mainEntity": [{"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
]
jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                    ensure_ascii=False, indent=2)

# ---- 4. new <head> ----
DESC = ("Connect Claude, ChatGPT, Cursor and 12+ AI assistants to your IQ Option account via the "
        "Model Context Protocol (MCP). One Bearer token, four market servers — digital options, "
        "CFD, crypto, forex. No code, three steps.")
head = f"""<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Connect any AI assistant to IQ Option · MCP Integration Guide</title>
<meta name="description" content="{DESC}">
<meta name="keywords" content="IQ Option, MCP, Model Context Protocol, Claude, ChatGPT, Cursor, AI trading assistant, digital options, forex, crypto, CFD, Bearer token">
<meta name="author" content="IQ Option">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#0C1326">
<link rel="canonical" href="{BASE}/">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="IQ Option · AI Integrations">
<meta property="og:title" content="Connect any AI assistant to IQ Option · MCP Integration Guide">
<meta property="og:description" content="One token, four markets, any AI. Connect Claude, ChatGPT or Cursor to IQ Option via MCP in three steps.">
<meta property="og:url" content="{BASE}/">
<meta property="og:image" content="{BASE}/assets/img/logo.png">
<meta property="og:locale" content="en_US">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Connect any AI assistant to IQ Option via MCP">
<meta name="twitter:description" content="One token, four markets, any AI. Claude, ChatGPT, Cursor — connected to IQ Option in three steps.">
<meta name="twitter:image" content="{BASE}/assets/img/logo.png">

<link rel="icon" type="image/png" href="assets/img/logo.png">
<link rel="apple-touch-icon" href="assets/img/logo.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<!-- QEDS · Quadcode Enterprise Design System (v1.2-pilot, dark) -->
<link rel="stylesheet" href="https://gnezdilovdenis.github.io/qeds/dist/v1/qeds.css">
<link rel="stylesheet" href="assets/css/tokens.css">
<link rel="stylesheet" href="assets/css/styles.css">

<!-- Structured data for AI answer engines & search -->
<script type="application/ld+json">
{jsonld}
</script>"""

# ---- 5. transform body ----
body = re.sub(r"<script>.*?</script>", "", body, flags=re.S)
body = re.sub(r'src="data:image/png;base64,[^"]*"', 'src="assets/img/logo.png"', body)
body = body.replace(' onclick="togglePerm(this)"', "")
body = body.replace('<nav class="nav">', '<nav class="nav" aria-label="Primary">')
body = body.replace('<div class="toast" id="toast">✓ Copied to clipboard</div>',
                    '<div class="toast" id="toast" role="status" aria-live="polite"></div>')
body = body.replace('<div class="hero-shell">',
                    '<a class="skip-link" href="#main">Skip to content</a>\n<main id="main">\n<div class="hero-shell">', 1)
body = body.replace("<footer>", "</main>\n<footer>", 1)
body = body.rstrip() + '\n\n<script src="assets/js/main.js"></script>\n'

doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head}
</head>
<body>
{body}</body>
</html>
"""

os.makedirs("assets/css", exist_ok=True)
open("index.html", "w", encoding="utf-8").write(doc)
open("assets/css/tokens.css", "w", encoding="utf-8").write(
    "/* QEDS-aligned design tokens — IQ Option AI Integrations */\n" + tokens_body + "\n")
open("assets/css/styles.css", "w", encoding="utf-8").write(styles_body + "\n")

# ---- 6. contrast report (WCAG) for text tokens on --bg-app ----
def lum(hexc):
    r, g, b = (int(hexc[i:i+2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def ratio(a, b):
    la, lb = lum(a), lum(b)
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 2)
bg = "#0C1326"
toks = dict(re.findall(r"(--text-[\w-]+):\s*(#[0-9A-Fa-f]{6})", tokens_body))
print("=== build ok ===")
print(f"logo.png bytes: {len(png)}  |  base64 left in body: {body.count('base64')}")
print(f"FAQ pairs -> JSON-LD: {len(faq)}  |  HowTo steps: {len(steps)}")
print("contrast vs --bg-app (#0C1326), AA normal>=4.5, large>=3.0:")
for k, v in toks.items():
    print(f"  {k:14} {v}  ratio {ratio(v, bg)}")
