#!/usr/bin/env python3
"""Generate 4 distinct 1200x630 OG card variants -> assets/img/og-1..4.png.
Pick one; it becomes assets/img/og.png. Rendered @2x then downscaled (crisp type)."""
import os, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
W, H = 1200 * S, 630 * S
ORANGE, GOLD, GREEN, CYAN, PURPLE = (255,138,0), (255,209,102), (0,230,139), (94,218,255), (167,139,250)
WHITE, BASE, MUTE, FAINT = (244,248,250), (213,221,226), (150,165,176), (110,124,138)
HERE = os.path.dirname(os.path.abspath(__file__))

INTER, MONO = "/tmp/Inter.ttf", "/tmp/JBMono.ttf"
for path, url in [(INTER, "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"),
                  (MONO, "https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf")]:
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)

def fnt(file, size, weight):
    ft = ImageFont.truetype(file, size * S)
    try: ft.set_variation_by_name(weight)
    except Exception: pass
    return ft
def f(size, weight="Regular"): return fnt(INTER, size, weight)
def m(size, weight="Regular"): return fnt(MONO, size, weight)
def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i]) * t) for i in range(3))

def bg(top, bot):
    col = Image.new("RGB", (1, H))
    for y in range(H): col.putpixel((0, y), lerp(top, bot, y / H))
    return col.resize((W, H))

def add_blobs(img, specs, blur):
    layer = Image.new("RGBA", (W, H), (0,0,0,0)); ld = ImageDraw.Draw(layer)
    for box, rgba in specs: ld.ellipse([c*S for c in box], fill=rgba)
    layer = layer.filter(ImageFilter.GaussianBlur(blur*S))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def tx(img, xy, s, font, fill): ImageDraw.Draw(img).text((xy[0]*S, xy[1]*S), s, font=font, fill=fill)
def tw(s, font): return ImageDraw.Draw(Image.new("RGB",(1,1))).textlength(s, font=font) / S
def center(img, cx, y, s, font, fill): tx(img, (cx - tw(s, font)/2, y), s, font, fill)

def gword(img, xy, s, font, c1, c2, glow=None):
    x, y = int(xy[0]*S), int(xy[1]*S)
    w = int(ImageDraw.Draw(img).textlength(s, font=font)); asc, desc = font.getmetrics(); h = asc+desc
    if glow:
        gl = Image.new("RGBA", (W, H), (0,0,0,0))
        ImageDraw.Draw(gl).text((x, y), s, font=font, fill=glow+(210,))
        gl = gl.filter(ImageFilter.GaussianBlur(15*S))
        out = Image.alpha_composite(img.convert("RGBA"), gl).convert("RGB"); img.paste(out, (0,0))
    row = Image.new("RGB", (max(1,w), 1))
    for i in range(w): row.putpixel((i,0), lerp(c1, c2, i/max(1,w-1)))
    grad = row.resize((max(1,w), h))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).text((x, y), s, font=font, fill=255)
    img.paste(grad, (x, y), mask.crop((x, y, x+w, y+h)))
    return w / S

def chip(img, x, y, label, dot, fsize=20):
    d = ImageDraw.Draw(img); fo = f(fsize, "SemiBold")
    w = ImageDraw.Draw(Image.new("RGB",(1,1))).textlength(label, font=fo)
    pw = int(w + 56*S); ph = 48*S; X, Y = x*S, y*S
    d.rounded_rectangle([X, Y, X+pw, Y+ph], radius=ph//2, outline=(54,69,100), width=max(1,S))
    d.ellipse([X+20*S, Y+ph//2-6*S, X+32*S, Y+ph//2+6*S], fill=dot)
    asc, desc = fo.getmetrics(); d.text((X+40*S, Y+ph//2-(asc+desc)//2), label, font=fo, fill=BASE)
    return pw/S + 14

def logo_into(img, x, y, size):
    try:
        lg = Image.open(os.path.join(HERE, "assets/img/logo.png")).convert("RGBA").resize((size*S, size*S))
        img.paste(lg, (int(x*S), int(y*S)), lg)
    except Exception: pass

def save(img, n):
    img.resize((1200, 630), Image.LANCZOS).save(os.path.join(HERE, f"assets/img/og-{n}.png"), "PNG", optimize=True)
    print(f"wrote assets/img/og-{n}.png")

# ── Variant 1 · SPOTLIGHT (left, warm glow) ─────────────────────────────
def v1():
    img = bg((10,15,30), (12,19,38))
    img = add_blobs(img, [((-340,-380,560,320),(255,138,0,82)), ((820,380,1380,900),(255,176,0,30)),
                          ((520,-160,1100,240),(94,218,255,12))], 150)
    logo_into(img, 76, 60, 92)
    tx(img, (192,70), "IQ OPTION", f(28,"Bold"), WHITE)
    tx(img, (192+tw("IQ OPTION",f(28,"Bold"))+14,73), "· AI INTEGRATIONS", f(24,"Medium"), MUTE)
    tx(img, (192,112), "Model Context Protocol", f(22), FAINT)
    d=ImageDraw.Draw(img); lp=f(20,"Bold"); lw=tw("LIVE",lp); lx=(1200-76-lw-62)*S
    d.rounded_rectangle([lx,70*S,(1200-76)*S,116*S], radius=23*S, outline=(255,138,0,130), width=max(1,S))
    d.ellipse([lx+22*S,87*S,lx+34*S,99*S], fill=ORANGE)
    d.text((lx+42*S,93*S-sum(lp.getmetrics())//2),"LIVE",font=lp,fill=ORANGE)
    hf=f(82,"ExtraBold"); tx(img,(76,196),"Connect any AI assistant",hf,WHITE)
    tx(img,(76,300),"to your ",hf,WHITE)
    gword(img,(76+tw("to your ",hf),300),"IQ Option",hf,ORANGE,GOLD,glow=ORANGE)
    tx(img,(76,430),"One token · four markets · 13 AI assistants — no code, in 3 steps",f(29,"Medium"),BASE)
    cx=76
    for lb,dot in [("Digital Options",ORANGE),("Margin CFD",GREEN),("Margin Crypto",CYAN),("Margin Forex",GOLD)]:
        cx+=chip(img,cx,498,lb,dot)
    d.line([76*S,566*S,(1200-76)*S,566*S],fill=(34,47,71),width=max(1,S))
    d.ellipse([76*S,588*S,89*S,601*S],fill=ORANGE); tx(img,(102,583),"iqoptionmcp.com",f(26,"SemiBold"),GOLD)
    save(img,1)

# ── Variant 2 · AURORA MESH (vibrant, framed) ───────────────────────────
def v2():
    img = bg((9,12,26), (11,16,34))
    img = add_blobs(img, [((-260,-260,540,420),(255,138,0,150)), ((760,-200,1300,360),(167,139,250,120)),
                          ((280,360,840,920),(94,218,255,90)), ((860,420,1360,920),(0,230,139,80)),
                          ((420,120,900,560),(255,209,102,50))], 165)
    # dark scrim for legibility
    scrim = Image.new("RGBA",(W,H),(8,11,24,120)); img = Image.alpha_composite(img.convert("RGBA"),scrim).convert("RGB")
    d=ImageDraw.Draw(img)
    # gradient frame
    fr=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(fr).rounded_rectangle([28*S,28*S,(1200-28)*S,(630-28)*S],radius=26*S,outline=(255,255,255,28),width=max(1,S))
    img=Image.alpha_composite(img.convert("RGBA"),fr).convert("RGB"); d=ImageDraw.Draw(img)
    logo_into(img,76,64,84)
    tx(img,(182,84),"IQ OPTION · AI INTEGRATIONS",f(26,"Bold"),WHITE)
    eb=f(22,"Bold"); tx(img,(76,210),"MODEL CONTEXT PROTOCOL",eb,GOLD)
    hf=f(86,"Black"); tx(img,(74,250),"Any AI, your",hf,WHITE)
    tx(img,(74,356),"",hf,WHITE)
    gword(img,(74,356),"IQ Option account",hf,GOLD,ORANGE,glow=ORANGE)
    tx(img,(76,486),"Claude · ChatGPT · Cursor — one token, four markets, no code.",f(28,"Medium"),BASE)
    d.ellipse([76*S,556*S,89*S,569*S],fill=GOLD); tx(img,(102,551),"iqoptionmcp.com",f(26,"SemiBold"),WHITE)
    save(img,2)

# ── Variant 3 · TERMINAL / MCP CONFIG (split) ───────────────────────────
def v3():
    img = bg((10,14,28), (12,19,38))
    img = add_blobs(img, [((-300,-300,420,300),(255,138,0,70)), ((780,360,1360,900),(0,230,139,40))], 150)
    d=ImageDraw.Draw(img)
    logo_into(img,76,60,84); tx(img,(180,80),"IQ OPTION · AI INTEGRATIONS",f(25,"Bold"),WHITE)
    hf=f(72,"ExtraBold"); tx(img,(76,196),"Connect any AI",hf,WHITE)
    tx(img,(76,288),"to ",hf,WHITE); gword(img,(76+tw("to ",hf),288),"IQ Option",hf,ORANGE,GOLD,glow=ORANGE)
    tx(img,(78,402),"One token · 4 markets",f(27,"Medium"),BASE)
    tx(img,(78,442),"No code · 3 steps",f(27,"Medium"),MUTE)
    d.ellipse([78*S,520*S,90*S,532*S],fill=ORANGE); tx(img,(102,515),"iqoptionmcp.com",f(25,"SemiBold"),GOLD)
    # code card right
    cx0,cy0,cx1,cy1 = 660, 150, 1148, 500
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(glow).rounded_rectangle([cx0*S,cy0*S,cx1*S,cy1*S],radius=20*S,fill=(255,138,0,55))
    glow=glow.filter(ImageFilter.GaussianBlur(28*S)); img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB"); d=ImageDraw.Draw(img)
    d.rounded_rectangle([cx0*S,cy0*S,cx1*S,cy1*S],radius=20*S,fill=(10,15,30),outline=(46,61,92),width=max(1,S))
    d.line([cx0*S,(cy0+46)*S,cx1*S,(cy0+46)*S],fill=(34,47,71),width=max(1,S))
    for i,col in enumerate([(255,95,86),(255,189,46),(39,201,63)]):
        d.ellipse([(cx0+22+i*22)*S,(cy0+18)*S,(cx0+34+i*22)*S,(cy0+30)*S],fill=col)
    tx(img,(cx0+150,cy0+14),"claude_desktop_config.json",m(17,"Medium"),MUTE)
    KEY,STR,PUN=CYAN,GOLD,MUTE
    lines=[[('{',PUN)],
           [('  "mcpServers"',KEY),(': {',PUN)],
           [('    "iq-digital-options"',KEY),(': {',PUN)],
           [('      "url"',KEY),(': ',PUN),('"…mcp.iqoption.com"',STR),(',',PUN)],
           [('      "headers"',KEY),(': { ',PUN),('"Authorization"',KEY),(':',PUN)],
           [('        "Bearer ',STR),('YOUR_TOKEN',ORANGE),('" }',STR)],
           [('    }',PUN)],
           [('  }',PUN)],
           [('}',PUN)]]
    mf=m(19,"Medium"); y=cy0+64
    for ln in lines:
        x=cx0+22
        for s,col in ln:
            tx(img,(x,y),s,mf,col); x+=tw(s,mf)
        y+=30
    save(img,3)

# ── Variant 4 · CENTERED MINIMAL CINEMATIC ──────────────────────────────
def v4():
    img = bg((9,13,27), (12,19,38))
    img = add_blobs(img, [((300,40,900,560),(255,138,0,70)), ((360,300,840,760),(255,176,0,26))], 175)
    # vignette
    vig=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(vig).rectangle([0,0,W,H],fill=(6,9,20,0))
    d=ImageDraw.Draw(img); CX=600
    logo_into(img, CX-46, 78, 92)
    center(img, CX, 190, "MODEL CONTEXT PROTOCOL", f(22,"Bold"), ORANGE)
    hf=f(78,"ExtraBold")
    center(img, CX, 236, "Connect any AI assistant", hf, WHITE)
    # centered line2 with gradient word: compose "to your IQ Option"
    pre, brand = "to your ", "IQ Option"
    total = tw(pre,hf)+tw(brand,hf); startx = CX-total/2
    tx(img,(startx,336),pre,hf,WHITE)
    gword(img,(startx+tw(pre,hf),336),brand,hf,ORANGE,GOLD,glow=ORANGE)
    center(img, CX, 460, "One token · four markets · 13 AI assistants · no code", f(28,"Medium"), BASE)
    # centered domain pill
    dl="iqoptionmcp.com"; df=f(26,"SemiBold"); pw=tw(dl,df)+70; X=(CX-pw/2)*S
    d.rounded_rectangle([X,532*S,(CX+pw/2)*S,584*S],radius=26*S,fill=(26,37,69),outline=(54,69,100),width=max(1,S))
    d.ellipse([(CX-pw/2+24)*S,553*S,(CX-pw/2+37)*S,566*S],fill=ORANGE)
    tx(img,(CX-pw/2+48,540),dl,df,GOLD)
    save(img,4)

for v in (v1, v2, v3, v4): v()
print("done")
