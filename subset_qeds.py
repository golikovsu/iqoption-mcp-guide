#!/usr/bin/env python3
"""Subset qeds.css to only the components this site actually uses
(qeds-button + qeds-checkbox), plus :root tokens and @keyframes.
Keeps the full design system at qeds.full.css for future re-subsetting.

  python3 subset_qeds.py
"""
import re, pathlib

CSS = pathlib.Path(__file__).parent / "assets/css/qeds.css"
FULL = pathlib.Path(__file__).parent / "assets/css/qeds.full.css"
KEEP = ("qeds-button", "qeds-checkbox")

src = CSS.read_text(encoding="utf-8")
if not FULL.exists():                      # snapshot the full design system once
    FULL.write_text(src, encoding="utf-8")
else:
    src = FULL.read_text(encoding="utf-8")  # always re-subset from the full source

# Strip block comments to simplify tokenizing.
src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)


def split_top(s):
    """Yield top-level constructs as (prelude, block_or_None).
    block is the inner text between the outermost { } (None for ;-statements)."""
    i, n, start = 0, len(s), 0
    while i < n:
        c = s[i]
        if c == "{":
            depth, j = 1, i + 1
            while j < n and depth:
                if s[j] == "{": depth += 1
                elif s[j] == "}": depth -= 1
                j += 1
            yield s[start:i].strip(), s[i + 1:j - 1]
            i = start = j
        elif c == ";" and s[start:i].strip().startswith("@"):
            yield s[start:i].strip() + ";", None
            i = start = i + 1
        else:
            i += 1
    tail = s[start:].strip()
    if tail:
        yield tail, None


def keep_selector(sel):
    return any(k in sel for k in KEEP)


out = []
for prelude, block in split_top(src):
    if block is None:
        continue                                   # drop @import/@charset/stray
    head = prelude.lstrip()
    if head.startswith("@keyframes"):
        out.append(f"{prelude}{{{block}}}")        # keep all keyframes (tiny)
    elif head.startswith("@media") or head.startswith("@supports"):
        inner = [f"{p}{{{b}}}" for p, b in split_top(block)
                 if b is not None and (p.startswith(":root") or keep_selector(p))]
        if inner:
            out.append(f"{prelude}{{\n  " + "\n  ".join(inner) + "\n}")
    elif head.startswith("@font-face"):
        continue
    elif prelude.startswith(":root") or keep_selector(prelude):
        out.append(f"{prelude}{{{block}}}")

result = ("/* qeds.css — SUBSET (button + checkbox only). "
          "Full design system: qeds.full.css. Regenerate: python3 subset_qeds.py */\n"
          + "\n".join(out) + "\n")
CSS.write_text(result, encoding="utf-8")
print(f"qeds.css: {len(FULL.read_text()):,} -> {len(result):,} bytes  ({len(out)} rules kept)")
