#!/usr/bin/env python3
"""Generate the 1200x630 Open Graph / social card (assets/img/og.png).
Design intelligence (UI/UX Pro Max): Dark Mode (OLED) — deep midnight, high contrast,
minimal glow, Inter, cinematic/premium. Rendered at 2x then downscaled for crisp type."""
import os, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2                                   # supersample factor (render @2x, downscale)
W, H = 1200 * S, 630 * S
BG_TOP, BG_BOT = (10, 15, 30), (12, 19, 38)
ORANGE, GOLD = (255, 138, 0), (255, 209, 102)
GREEN, CYAN = (0, 230, 139), (94, 218, 255)
WHITE, MUTE, FAINT = (244, 248, 250), (150, 165, 176), (110, 124, 138)

INTER = "/tmp/Inter.ttf"
if not os.path.exists(INTER):
    urllib.request.urlretrieve(
        "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf", INTER)

def f(size, weight="Regular"):
    ft = ImageFont.truetype(INTER, size * S)
    try: ft.set_variation_by_name(weight)
    except Exception: pass
    return ft

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ── background: vertical gradient + soft radial glows ───────────────────
img = Image.new("RGB", (W, H))
px = img.load()
for y in range(H):
    c = lerp(BG_TOP, BG_BOT, y / H)
    for x in range(W):
        px[x, y] = c

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-340*S, -380*S, 560*S, 320*S], fill=(255, 138, 0, 78))     # orange, top-left
gd.ellipse([820*S, 380*S, 1380*S, 900*S], fill=(255, 176, 0, 30))      # warm, bottom-right
gd.ellipse([520*S, -160*S, 1100*S, 240*S], fill=(94, 218, 255, 14))    # faint cyan, top
glow = glow.filter(ImageFilter.GaussianBlur(150 * S))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
d = ImageDraw.Draw(img)

PAD = 76 * S

def text(xy, s, font, fill):
    d.text(xy, s, font=font, fill=fill)

def grad_word(xy, s, font, c1, c2, glow_color=None):
    """Draw text with a left→right gradient and an optional soft glow behind it."""
    w = int(d.textlength(s, font=font))
    asc, desc = font.getmetrics(); h = asc + desc
    if glow_color:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).text(xy, s, font=font, fill=glow_color + (200,))
        gl = gl.filter(ImageFilter.GaussianBlur(14 * S))
        img.paste(Image.alpha_composite(img.convert("RGBA"), gl).convert("RGB"), (0, 0))
        d2 = ImageDraw.Draw(img)
    else:
        d2 = d
    row = Image.new("RGB", (max(1, w), 1))
    for x in range(w):
        row.putpixel((x, 0), lerp(c1, c2, x / max(1, w - 1)))
    grad = row.resize((max(1, w), h))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text(xy, s, font=font, fill=255)
    img.paste(grad.crop((0, 0, w, h)), (xy[0], xy[1]), mask.crop((xy[0], xy[1], xy[0] + w, xy[1] + h)))
    return w

def pill(x, y, label, dot):
    fnt = f(20, "SemiBold")
    tw = d.textlength(label, font=fnt)
    pw = int(tw + 58 * S); ph = 50 * S
    d.rounded_rectangle([x, y, x + pw, y + ph], radius=ph // 2,
                        fill=(255, 255, 255, 0), outline=(46, 61, 92), width=max(1, S))
    d.ellipse([x + 20*S, y + ph//2 - 6*S, x + 32*S, y + ph//2 + 6*S], fill=dot)
    d.text((x + 40*S, y + ph//2 - (fnt.getmetrics()[0]+fnt.getmetrics()[1])//2), label, font=fnt, fill=(213, 221, 226))
    return pw

# ── header: logo + wordmark + LIVE pill ─────────────────────────────────
try:
    logo = Image.open(os.path.join(os.path.dirname(__file__), "assets/img/logo.png")).convert("RGBA")
    logo = logo.resize((92 * S, 92 * S))
    img.paste(logo, (PAD, 60 * S), logo)
except Exception:
    pass
text((PAD + 116*S, 70*S), "IQ OPTION", f(28, "Bold"), WHITE)
wlen = d.textlength("IQ OPTION", font=f(28, "Bold"))
text((PAD + 116*S + int(wlen) + 14*S, 73*S), "· AI INTEGRATIONS", f(24, "Medium"), MUTE)
text((PAD + 116*S, 112*S), "Model Context Protocol", f(22, "Regular"), FAINT)
# LIVE pill (top-right)
lp = f(20, "Bold"); lw = d.textlength("LIVE", font=lp)
lx = W - PAD - int(lw) - 62*S
d.rounded_rectangle([lx, 70*S, W - PAD, 70*S + 46*S], radius=23*S, outline=(255,138,0,120), width=max(1,S))
d.ellipse([lx + 22*S, 70*S + 17*S, lx + 34*S, 70*S + 29*S], fill=ORANGE)
d.text((lx + 42*S, 70*S + 23*S - (lp.getmetrics()[0]+lp.getmetrics()[1])//2), "LIVE", font=lp, fill=ORANGE)

# ── headline ────────────────────────────────────────────────────────────
hf = f(82, "ExtraBold")
text((PAD, 196*S), "Connect any AI assistant", hf, WHITE)
y2 = 300 * S
pre = "to your "
text((PAD, y2), pre, hf, WHITE)
grad_word((PAD + int(d.textlength(pre, font=hf)), y2), "IQ Option", hf, ORANGE, GOLD, glow_color=ORANGE)

# ── subtitle ────────────────────────────────────────────────────────────
text((PAD, 430*S), "One token · four markets · 13 AI assistants — no code, in 3 steps",
     f(29, "Medium"), (200, 211, 219))

# ── market chips ────────────────────────────────────────────────────────
cx = PAD; cy = 498 * S
for label, dot in [("Digital Options", ORANGE), ("Margin CFD", GREEN), ("Margin Crypto", CYAN), ("Margin Forex", GOLD)]:
    cx += pill(cx, cy, label, dot) + 14 * S

# ── domain (bottom) + hairline ──────────────────────────────────────────
d.line([PAD, 566*S, W - PAD, 566*S], fill=(34, 47, 71), width=max(1, S))
df = f(26, "SemiBold")
d.ellipse([PAD, 588*S, PAD + 13*S, 601*S], fill=ORANGE)
text((PAD + 26*S, 583*S), "iqoptionmcp.com", df, GOLD)

# downscale for crisp anti-aliased type
img = img.resize((1200, 630), Image.LANCZOS)
img.save(os.path.join(os.path.dirname(__file__), "assets/img/og.png"), "PNG", optimize=True)
print("wrote assets/img/og.png", img.size)
