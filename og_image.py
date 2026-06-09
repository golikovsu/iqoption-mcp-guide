#!/usr/bin/env python3
"""Generate a 1200x630 Open Graph / Twitter social card (assets/img/og.png).
Run once; re-run if the headline/brand changes."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
BG = (12, 19, 38)        # --bg-app #0C1326
ORANGE = (255, 138, 0)
GOLD = (255, 209, 102)
WHITE = (244, 248, 250)
MUTE = (150, 165, 176)

img = Image.new("RGB", (W, H), BG)

# --- ambient glows (match the hero) ---
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-260, -320, 560, 360], fill=(255, 138, 0, 90))      # orange top-left
gd.ellipse([820, 360, 1400, 900], fill=(0, 179, 112, 70))       # green bottom-right
glow = glow.filter(ImageFilter.GaussianBlur(150))
img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))

# --- subtle grid ---
grid = ImageDraw.Draw(img)
for x in range(0, W, 60):
    grid.line([(x, 0), (x, H)], fill=(255, 255, 255, 6), width=1)
for y in range(0, H, 60):
    grid.line([(0, y), (W, y)], fill=(255, 255, 255, 6), width=1)

d = ImageDraw.Draw(img)

def font(size, bold=True):
    for p in ([
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

PAD = 80

# logo
try:
    logo = Image.open("assets/img/logo.png").convert("RGBA")
    logo.thumbnail((104, 104))
    img.paste(logo, (PAD, PAD), logo)
except Exception:
    pass

# eyebrow
eb = font(26)
d.text((PAD + 124, PAD + 14), "IQ OPTION · AI INTEGRATIONS", font=eb, fill=ORANGE)
d.text((PAD + 124, PAD + 52), "Model Context Protocol", font=font(24, False), fill=MUTE)

# headline (two lines; accent the brand)
h1 = font(78)
d.text((PAD, 250), "Connect any AI assistant", font=h1, fill=WHITE)
y2 = 348
pre = "to your "
d.text((PAD, y2), pre, font=h1, fill=WHITE)
w_pre = d.textlength(pre, font=h1)
d.text((PAD + w_pre, y2), "IQ Option", font=h1, fill=ORANGE)

# subtitle
d.text((PAD, 470), "One token · 4 markets · 13 AI assistants · no code, 3 steps",
       font=font(30, False), fill=(213, 221, 226))

# domain pill
dom = font(28)
dtext = "iqoptionmcp.com"
dw = d.textlength(dtext, font=dom)
d.rounded_rectangle([PAD, 540, PAD + dw + 44, 590], radius=25, fill=(26, 37, 69))
d.text((PAD + 22, 550), dtext, font=dom, fill=GOLD)

# bottom accent bar
d.rectangle([0, H - 8, W, H], fill=ORANGE)

img.save("assets/img/og.png", "PNG", optimize=True)
print("wrote assets/img/og.png", img.size)
