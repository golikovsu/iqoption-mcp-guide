#!/usr/bin/env python3
"""i18n pipeline for the IQ Option MCP guide.

  python3 build_i18n.py extract     # English index.html -> template.html + i18n/en.json + i18n/_map.json
  python3 build_i18n.py generate    # template + i18n/<lang>.json -> per-language static pages + sitemap/robots/llms

Translation strategy: only TEXT NODES are extracted (each replaced by a ⟦key⟧ placeholder), so inline
tags, code blocks, URLs and the document structure are preserved by construction.
"""
import re, json, html, sys, pathlib
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = pathlib.Path(__file__).parent
SRC  = ROOT / "index.html"
TPL  = ROOT / "template.html"
I18N = ROOT / "i18n"
BASE = "https://iqoptionmcp.com"
DATE = "2026-06-09"   # datePublished / dateModified (bump on content change)

# code, dir, autonym, hreflang, sub-path ('' = site root)
LANGS = [
    ("en", "ltr", "English",          "en",    ""),
    ("ar", "rtl", "العربية",          "ar-SA", "ar/"),
    ("th", "ltr", "ไทย",              "th",    "th/"),
    ("pt", "ltr", "Português",        "pt",    "pt/"),
    ("es", "ltr", "Español",          "es",    "es/"),
    ("tl", "ltr", "Tagalog",          "tl",    "tl/"),
    ("id", "ltr", "Bahasa Indonesia", "id",    "id/"),
]

# English head/meta + structured-data strings (translated via i18n/<lang>.json "meta").
META_EN = {
    "m_title":   "Connect any AI assistant to IQ Option · MCP Integration Guide",
    "m_desc":    "Connect Claude, ChatGPT, Cursor and 12+ AI assistants to your IQ Option account via the Model Context Protocol (MCP). One Bearer token, four market servers — digital options, CFD, crypto, forex. No code, three steps.",
    "m_og_title": "Connect any AI assistant to IQ Option · MCP Integration Guide",
    "m_og_desc":  "One token, four markets, any AI. Connect Claude, ChatGPT or Cursor to IQ Option via MCP in three steps.",
    "m_tw_title": "Connect any AI assistant to IQ Option via MCP",
    "m_tw_desc":  "One token, four markets, any AI. Claude, ChatGPT, Cursor — connected to IQ Option in three steps.",
    "m_article_headline": "Connect any AI assistant to IQ Option via MCP",
    "m_article_desc": "One Bearer token, four market MCP servers (digital options, CFD, crypto, forex). Ready-made configs for Claude, ChatGPT, Cursor and 12+ assistants. No code, three steps.",
    "m_howto_name": "How to connect an AI assistant to IQ Option",
    "m_howto_desc": "Connect any MCP-capable AI assistant to IQ Option in three steps.",
}

SKIP_TAGS    = {"pre", "code", "script", "style", "noscript"}
SKIP_CLASSES = {"srv-url", "pb-path"}          # literal server URLs / file paths — never translate


def in_skip(node):
    for p in node.parents:
        if p.name in SKIP_TAGS:
            return True
        if set(p.get("class", [])) & SKIP_CLASSES:
            return True
    return False


def translatable(s):
    t = s.strip()
    return len(t) >= 2 and re.search(r"[A-Za-z]", t)


def keys_in(el):
    return re.findall(r"⟦(t\d+)⟧", el.get_text())


def segments_of(el):
    """Ordered text segments of an element: translatable {'k': key} placeholders
    AND literal {'lit': text} (e.g. <code>/<a> content skipped from translation).
    Lets JSON-LD reconstruct COMPLETE answer text, not just the translatable parts."""
    segs = []
    if el is None:
        return segs
    for nd in el.descendants:
        if isinstance(nd, NavigableString) and not isinstance(nd, Comment):
            s = str(nd)
            m = re.fullmatch(r"\s*⟦(t\d+)⟧\s*", s)
            if m:
                segs.append({"k": m.group(1)})
            elif s.strip():
                segs.append({"lit": s.strip()})
    return segs


def extract():
    raw = SRC.read_text(encoding="utf-8")
    _, body_inner = re.split(r"<body>", raw, 1)
    body_inner = body_inner.rsplit("</body>", 1)[0]
    # <head> source of truth is template.html (clean, pre-substitution head) so re-running
    # extract never bakes the generated hreflang/dir/JSON-LD back in. Fall back to index on first run.
    head_src = TPL.read_text(encoding="utf-8") if TPL.exists() else raw
    head_part = re.split(r"<body>", head_src, 1)[0]
    soup = BeautifulSoup(body_inner, "html.parser")
    for sw in soup.select(".lang-switch"):   # drop generated switcher; re-inserted via ⟦LANG_SWITCH⟧
        sw.decompose()

    targets = [n for n in soup.descendants
               if isinstance(n, NavigableString) and not isinstance(n, Comment)
               and not in_skip(n) and translatable(str(n))]

    strings, n = {}, 0
    for node in targets:
        n += 1
        key = f"t{n:04d}"
        raw_s = str(node)
        lead = raw_s[:len(raw_s) - len(raw_s.lstrip())]
        trail = raw_s[len(raw_s.rstrip()):]
        strings[key] = raw_s.strip()
        node.replace_with(NavigableString(f"{lead}⟦{key}⟧{trail}"))

    # Structural map for JSON-LD (FAQ + HowTo), language-independent.
    # Stored as ordered segments so reconstructed text keeps inline <code>/<a> content.
    faq = [{"q": segments_of(it.summary), "a": segments_of(it.p)}
           for it in soup.select("details.faq-item")]
    howto = []
    for step in soup.select(".steps .step"):
        intro = step.find("p")
        name = segments_of(step.find("h3"))
        text = segments_of(intro) + [s for li in step.find_all("li") for s in segments_of(li)]
        howto.append({"name": name, "text": text})

    body_str = str(soup).replace("</nav>", "⟦LANG_SWITCH⟧</nav>", 1)
    TPL.write_text(head_part + "<body>" + body_str + "</body>\n</html>\n", encoding="utf-8")

    I18N.mkdir(exist_ok=True)
    (I18N / "en.json").write_text(
        json.dumps({"meta": META_EN, "strings": strings}, ensure_ascii=False, indent=2), encoding="utf-8")
    (I18N / "_map.json").write_text(
        json.dumps({"faq": faq, "howto": howto}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"extracted {len(strings)} strings | faq {len(faq)} | howto {len(howto)}")
    print("sample:", json.dumps(dict(list(strings.items())[:6]), ensure_ascii=False))


# ───────────────────────── generate ─────────────────────────
def esc(s):
    return html.escape(s, quote=False)


# Flag (ISO country) per language. pt→Brazil, es→Spain, en→UK (adjust if desired).
FLAG = {"en": "gb", "ar": "sa", "th": "th", "pt": "br", "es": "es", "tl": "ph", "id": "id"}


def lang_switch_html(cur_path, cur_dir):
    """Relative links from the current page to each language home, with flag icons."""
    def flag(code):
        return (f'<img class="lang-flag" src="assets/img/flags/{FLAG[code]}.png" '
                f'alt="" width="22" height="16">')
    items = []
    for code, _d, name, hl, path in LANGS:
        if cur_path:                      # current page is one dir deep
            href = ("../" + path) if path else "../"
        else:                             # current page is site root
            href = path if path else "./"
        cur = ' aria-current="true"' if path == cur_path else ""
        items.append(f'<li><a href="{href}" hreflang="{hl}" lang="{code}"{cur}>'
                     f'<span class="lang-name">{flag(code)}<span class="lang-label">{name}</span></span></a></li>')
    cur_code, cur_name = next((c, n) for c, _d, n, _h, p in LANGS if p == cur_path)
    return (
        '<div class="lang-switch">'
        f'<button class="lang-toggle" type="button" aria-expanded="false" aria-controls="lang-menu" aria-label="Language">'
        f'{flag(cur_code)}<span class="lang-current">{cur_name}</span>'
        '<span class="lang-caret" aria-hidden="true">▾</span></button>'
        f'<ul class="lang-menu" id="lang-menu" hidden>{"".join(items)}</ul>'
        '</div>'
    )


def hreflang_block():
    out = []
    for _c, _d, _n, hl, path in LANGS:
        out.append(f'<link rel="alternate" hreflang="{hl}" href="{BASE}/{path}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/">')
    return "\n".join(out)


def build_jsonld(code, page_url, strings, meta, mp):
    def render(segs):
        parts = [strings.get(s["k"], "") if "k" in s else s["lit"] for s in segs]
        return re.sub(r"\s+", " ", " ".join(p for p in parts if p)).strip()
    graph = [
        {"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/",
         "name": "IQ Option · AI Integrations", "inLanguage": code,
         "publisher": {"@id": f"{BASE}/#org"}},
        {"@type": "Organization", "@id": f"{BASE}/#org", "name": "IQ Option",
         "url": "https://iqoption.com", "logo": f"{BASE}/assets/img/logo.png",
         "sameAs": ["https://iqoption.com"]},
        {"@type": "SoftwareApplication", "@id": f"{BASE}/#app",
         "name": "IQ Option AI Integrations (MCP)", "applicationCategory": "FinanceApplication",
         "operatingSystem": "Web, macOS, Windows, Linux", "inLanguage": code,
         "description": meta["m_article_desc"], "url": f"{BASE}/",
         "publisher": {"@id": f"{BASE}/#org"},
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "featureList": [
             "Read balance, quotes, history and open positions in plain language",
             "Per-market trade permissions (read default, trade opt-in)",
             "Works with Claude, ChatGPT, Cursor and 12+ AI assistants",
             "Four MCP servers: digital options, CFD, crypto, forex"]},
        {"@type": "TechArticle", "@id": f"{page_url}#article",
         "headline": meta["m_article_headline"], "description": meta["m_article_desc"],
         "inLanguage": code, "isPartOf": {"@id": f"{BASE}/#website"},
         "datePublished": DATE, "dateModified": DATE, "image": f"{BASE}/assets/img/og.png",
         "author": {"@id": f"{BASE}/#org"}, "publisher": {"@id": f"{BASE}/#org"},
         "about": {"@type": "Thing", "name": "Model Context Protocol",
                   "sameAs": "https://modelcontextprotocol.io"}},
        {"@type": "HowTo", "@id": f"{page_url}#howto", "inLanguage": code,
         "name": meta["m_howto_name"], "description": meta["m_howto_desc"], "totalTime": "PT3M",
         "step": [{"@type": "HowToStep", "position": i + 1, "url": f"{page_url}#setup",
                   "name": render(s["name"]), "text": render(s["text"])}
                  for i, s in enumerate(mp["howto"])]},
        {"@type": "FAQPage", "@id": f"{page_url}#faq", "inLanguage": code,
         "mainEntity": [{"@type": "Question", "name": render(f["q"]),
                         "acceptedAnswer": {"@type": "Answer", "text": render(f["a"])}}
                        for f in mp["faq"]]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)


def generate():
    tpl = TPL.read_text(encoding="utf-8")
    mp = json.loads((I18N / "_map.json").read_text(encoding="utf-8"))
    en = json.loads((I18N / "en.json").read_text(encoding="utf-8"))

    for code, direction, _name, hl, path in LANGS:
        loc = json.loads((I18N / f"{code}.json").read_text(encoding="utf-8"))
        strings = {**en["strings"], **loc.get("strings", {})}   # fall back to EN for any missing key
        meta = {**en["meta"], **loc.get("meta", {})}
        doc = tpl

        # body placeholders
        for key, val in strings.items():
            doc = doc.replace(f"⟦{key}⟧", esc(val))
        doc = doc.replace("⟦LANG_SWITCH⟧", lang_switch_html(path, direction))

        # <html lang dir>
        doc = re.sub(r'<html lang="en">',
                     f'<html lang="{code}" dir="{direction}">', doc, count=1)

        # head text
        doc = doc.replace("<title>Connect any AI assistant to IQ Option · MCP Integration Guide</title>",
                          f"<title>{esc(meta['m_title'])}</title>", 1)
        doc = doc.replace(META_EN["m_desc"], esc(meta["m_desc"]))
        doc = doc.replace(META_EN["m_og_title"], esc(meta["m_og_title"]))
        doc = doc.replace(META_EN["m_og_desc"], esc(meta["m_og_desc"]))
        doc = doc.replace(META_EN["m_tw_title"], esc(meta["m_tw_title"]))
        doc = doc.replace(META_EN["m_tw_desc"], esc(meta["m_tw_desc"]))

        # canonical + og:url for this locale, then hreflang alternates
        page_url = f"{BASE}/{path}"
        doc = doc.replace(f'<link rel="canonical" href="{BASE}/">',
                          f'<link rel="canonical" href="{page_url}">\n{hreflang_block()}', 1)
        doc = doc.replace(f'<meta property="og:url" content="{BASE}/">',
                          f'<meta property="og:url" content="{page_url}">', 1)
        doc = doc.replace('<meta property="og:locale" content="en_US">',
                          f'<meta property="og:locale" content="{code}">', 1)

        # localized JSON-LD
        doc = re.sub(r'<script type="application/ld\+json">.*?</script>',
                     '<script type="application/ld+json">\n'
                     + build_jsonld(code, page_url, strings, meta, mp) + '\n</script>',
                     doc, count=1, flags=re.S)

        if path:                                   # sub-pages: assets live one level up
            doc = doc.replace('"assets/', '"../assets/')
        if direction == "rtl":                     # Arabic RTL overrides
            prefix = "../" if path else ""
            doc = doc.replace('<link rel="stylesheet" href="' + prefix + 'assets/css/styles.css">',
                              '<link rel="stylesheet" href="' + prefix + 'assets/css/styles.css">\n'
                              '<link rel="stylesheet" href="' + prefix + 'assets/css/rtl.css">', 1)

        out = (ROOT / path / "index.html") if path else (ROOT / "index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print(f"  wrote {out.relative_to(ROOT)}  ({direction}, {len(loc.get('strings', {}))} strings)")

    write_sitemap()
    print("done.")


def write_sitemap():
    urls = []
    for _c, _d, _n, _hl, path in LANGS:
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{hl}" href="{BASE}/{p}"/>'
            for _c2, _d2, _n2, hl, p in LANGS)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}/"/>'
        urls.append(
            f'  <url>\n    <loc>{BASE}/{path}</loc>\n    <lastmod>{DATE}</lastmod>'
            f'\n    <changefreq>monthly</changefreq>\n    <priority>{"1.0" if not path else "0.9"}</priority>'
            f'{alts}\n  </url>')
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    print("  wrote sitemap.xml")


def remap():
    """Rebuild i18n/_map.json (FAQ + HowTo segments) from template.html placeholders,
    without re-running extract (which would overwrite the template head)."""
    soup = BeautifulSoup(TPL.read_text(encoding="utf-8"), "html.parser")
    faq = [{"q": segments_of(it.summary), "a": segments_of(it.p)}
           for it in soup.select("details.faq-item")]
    howto = []
    for step in soup.select(".steps .step"):
        intro = step.find("p")
        name = segments_of(step.find("h3"))
        text = segments_of(intro) + [s for li in step.find_all("li") for s in segments_of(li)]
        howto.append({"name": name, "text": text})
    (I18N / "_map.json").write_text(
        json.dumps({"faq": faq, "howto": howto}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"remapped from template: faq {len(faq)} | howto {len(howto)}")


def migrate():
    """After an extract() that shifted positional keys, re-key each locale's translations
    by matching English source text (preserving existing translations). Requires a snapshot
    of the pre-extract English strings at i18n/_en_prev.json. Prints the new (untranslated)
    strings to fill into i18n/<lang>.json."""
    prev = json.loads((I18N / "_en_prev.json").read_text(encoding="utf-8"))["strings"]
    new_en = json.loads((I18N / "en.json").read_text(encoding="utf-8"))["strings"]
    prev_texts = set(prev.values())
    for code, _d, _n, _hl, _p in LANGS:
        if code == "en":
            continue
        path = I18N / f"{code}.json"
        loc = json.loads(path.read_text(encoding="utf-8"))
        old = loc.get("strings", {})
        text2trans = {}
        for k, t in old.items():
            en_t = prev.get(k)
            if en_t is not None and en_t not in text2trans:
                text2trans[en_t] = t
        loc["strings"] = {nk: text2trans[en_t] for nk, en_t in new_en.items() if en_t in text2trans}
        path.write_text(json.dumps(loc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{code}: rekeyed {len(loc['strings'])}/{len(new_en)}")
    missing = [(nk, en_t) for nk, en_t in new_en.items() if en_t not in prev_texts]
    print(f"\nNEW strings needing translation ({len(missing)}):")
    print(json.dumps({nk: t for nk, t in missing}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "extract"
    {"extract": extract, "generate": generate, "remap": remap, "migrate": migrate}[mode]()
