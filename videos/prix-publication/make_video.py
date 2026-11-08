"""Sketch TikTok « Le prix est sur la publication » – Dispo Sénégal.

Génère une vidéo verticale 1080x1920 (30 i/s), SANS son : la musique / le son
tendance s'ajoute directement dans TikTok au moment de publier.

Usage : python3 make_video.py   ->   dispo-prix-publication.mp4
Modifiez DIALOGUE ci-dessous pour changer le texte ou les prix.
"""
import math
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dispo-prix-publication.mp4")
W, H, FPS = 1080, 1920, 30

RED = (214, 32, 39)
DARK_RED = (150, 15, 20)
WHITE = (255, 255, 255)
INK = (25, 25, 25)
CHAT_BG = (236, 229, 221)
CLIENT_BUBBLE = WHITE
DISPO_BUBBLE = (220, 248, 198)

F = "/usr/share/fonts/truetype/dejavu/"
def font(size, bold=True):
    return ImageFont.truetype(F + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)

# ---------------------------------------------------------------- contenu
# (qui, texte, instant d'apparition en secondes)
DIALOGUE = [
    ("client", "Bonjour c'est combien ?", 3.4),
    ("dispo", "4.000.000", 5.4),
    ("client", "Pourtant c'est écrit 3.500.000 sur la publication", 7.4),
    ("dispo", "Ah… vous avez vu le prix donc 😏", 10.0),
]
PUNCHLINE = "AH… VOUS AVEZ VU\nLE PRIX DONC ?"
T_INTRO_END = 3.0      # fin de la scène « publication »
T_PUNCH = 12.6         # début de la scène lapin clin d'œil
T_OUTRO = 15.8         # début de la carte de fin
T_END = 19.0

# ---------------------------------------------------------------- images
img_post = Image.open(os.path.join(HERE, "images/hp304.png")).convert("RGB")
img_wink = Image.open(os.path.join(HERE, "images/lapin-clin-oeil.png")).convert("RGB")
logo = img_post.crop((40, 0, 400, 112))
wink_face = img_wink.crop((610, 200, 1206, 1600))


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def pop(t):
    """Apparition avec petit rebond (easeOutBack)."""
    t = max(0.0, min(1.0, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def cover(img, w, h, zoom=1.0, fx=0.5, fy=0.5):
    s = max(w / img.width, h / img.height) * zoom
    r = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    x = int((r.width - w) * fx)
    y = int((r.height - h) * fy)
    return r.crop((x, y, x + w, y + h))


def text_center(d, cx, y, txt, fnt, fill, stroke=0, stroke_fill=None, spacing=10):
    d.multiline_text((cx, y), txt, font=fnt, fill=fill, anchor="ma", align="center",
                     spacing=spacing, stroke_width=stroke, stroke_fill=stroke_fill)


def strip_emoji(s):
    # DejaVu n'a pas d'emoji couleur : on les remplace par un dessin à part
    return "".join(ch for ch in s if ord(ch) < 0x2600).strip()


def wrap(txt, fnt, maxw, d):
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if d.textlength(test, font=fnt) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    return lines


def draw_smirk(d, cx, cy, r):
    """Emoji 😏 dessiné à la main."""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 200, 40), outline=(220, 150, 0), width=3)
    e = r * 0.35
    d.line((cx - e - 12, cy - r * 0.25, cx - e + 14, cy - r * 0.2), fill=INK, width=5)
    d.line((cx + e - 14, cy - r * 0.2, cx + e + 12, cy - r * 0.25), fill=INK, width=5)
    d.arc((cx - r * 0.2, cy - r * 0.1, cx + r * 0.6, cy + r * 0.5), 20, 120, fill=INK, width=5)


# ---------------------------------------------------------------- bulles
_m = ImageDraw.Draw(Image.new("RGB", (10, 10)))
BF = font(54, bold=False)
NAMEF = font(30)
bubbles = []
for who, txt, t0 in DIALOGUE:
    has_emoji = strip_emoji(txt) != txt
    lines = wrap(strip_emoji(txt), BF, 760, _m)
    tw = max(_m.textlength(l, font=BF) for l in lines) + (70 if has_emoji else 0)
    bw = int(max(tw, 260) + 70)
    bh = int(len(lines) * 68 + 110)
    b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    color = CLIENT_BUBBLE if who == "client" else DISPO_BUBBLE
    bd.rounded_rectangle((0, 0, bw - 1, bh - 1), 30, fill=color)
    bd.text((35, 18), "Client" if who == "client" else "Dispo.sn", font=NAMEF,
            fill=(30, 120, 200) if who == "client" else RED)
    for i, l in enumerate(lines):
        bd.text((35, 62 + i * 68), l, font=BF, fill=INK)
    if has_emoji:
        lx = 35 + _m.textlength(lines[-1], font=BF) + 40
        draw_smirk(bd, int(lx), 62 + (len(lines) - 1) * 68 + 32, 26)
    bd.text((bw - 110, bh - 38), "23:17" + (" ✓✓" if who == "dispo" else ""), font=font(22, False),
            fill=(120, 120, 120) if who == "client" else (50, 150, 220))
    bubbles.append((who, b, t0))


# ---------------------------------------------------------------- scènes
def scene_intro(t):
    # la publication avec zoom lent + légende POV
    frame = Image.new("RGB", (W, H), RED)
    zoom = 1.0 + 0.05 * t
    pw = int(W * zoom)
    ph = int(pw * img_post.height / img_post.width)
    post = img_post.resize((pw, ph), Image.LANCZOS)
    frame.paste(post, ((W - pw) // 2, 330 - (ph - 1260) // 2))
    d = ImageDraw.Draw(frame)
    k = ease(t / 0.5)
    y = int(-260 + 310 * k)
    d.rounded_rectangle((60, y, W - 60, y + 230), 36, fill=WHITE, outline=RED, width=6)
    text_center(d, W // 2, y + 30, "POV : le prix est\nsur la publication…", font(62), INK)
    if t > 1.4:
        k2 = ease((t - 1.4) / 0.4)
        a = int(255 * k2)
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(o)
        od.rounded_rectangle((90, 1640, W - 90, 1840), 40, fill=(0, 0, 0, int(190 * k2)))
        od.text((W // 2, 1680), "…mais le client demande", font=font(56), fill=(255, 255, 255, a), anchor="ma")
        od.text((W // 2, 1755), "QUAND MÊME 😂".replace("😂", ""), font=font(56), fill=(255, 210, 0, a), anchor="ma")
        frame = Image.alpha_composite(frame.convert("RGBA"), o).convert("RGB")
    return frame


def chat_base():
    f = Image.new("RGB", (W, H), CHAT_BG)
    d = ImageDraw.Draw(f)
    # motif discret
    for yy in range(300, H, 120):
        for xx in range((yy // 120 % 2) * 60, W, 120):
            d.ellipse((xx, yy, xx + 10, yy + 10), fill=(225, 216, 205))
    # en-tête façon messagerie
    d.rectangle((0, 0, W, 250), fill=RED)
    d.ellipse((40, 110, 150, 220), fill=WHITE)
    lg = logo.resize((96, 30))
    f.paste(lg, (47, 150))
    d.text((180, 118), "Dispo.sn", font=font(52), fill=WHITE)
    d.text((180, 182), "en ligne", font=font(32, False), fill=(255, 220, 220))
    d.text((40, 40), "23:17", font=font(36), fill=WHITE)
    return f


def scene_chat(t):
    f = chat_base().convert("RGBA")
    d = ImageDraw.Draw(f)
    y = 300
    placed = []
    for who, b, t0 in bubbles:
        lt = t - (t0 - T_INTRO_END)
        if lt < 0:
            # indicateur « écrit… » juste avant chaque message
            if lt > -1.0:
                placed.append(("typing", who, y))
            break
        placed.append(("bubble", who, b, lt, y))
        y += b.height + 40
    # défilement si ça dépasse
    bottom = y + 140
    shift = max(0, bottom - (H - 80))
    for p in placed:
        if p[0] == "typing":
            _, who, yy = p
            yy -= shift
            x = 50 if who == "client" else W - 50 - 200
            d.rounded_rectangle((x, yy, x + 200, yy + 90), 30, fill=CLIENT_BUBBLE if who == "client" else DISPO_BUBBLE)
            for i in range(3):
                ph = math.sin(t * 9 - i * 0.9)
                d.ellipse((x + 45 + i * 45, yy + 35 - ph * 8, x + 65 + i * 45, yy + 55 - ph * 8), fill=(140, 140, 140))
            continue
        _, who, b, lt, yy = p
        yy -= shift
        s = pop(lt / 0.45)
        if s <= 0.01:
            continue
        bw, bh = max(1, int(b.width * s)), max(1, int(b.height * s))
        bs = b.resize((bw, bh), Image.LANCZOS)
        if who == "client":
            x = 50
        else:
            x = W - 50 - bw
        f.alpha_composite(bs, (x, int(yy + (b.height - bh) / 2)))
    f = f.convert("RGB")
    # gros zoom « choc » sur le prix
    for who, b, t0 in bubbles:
        if "4.000.000" in DIALOGUE[1][1] and t0 == DIALOGUE[1][2]:
            lt = t - (t0 - T_INTRO_END)
            if 0.5 < lt < 1.6:
                d = ImageDraw.Draw(f)
                k = ease((lt - 0.5) / 0.25)
                sz = int(60 + 80 * k)
                text_center(d, W // 2, 1450, "4.000.000 ?!", font(sz), (255, 230, 0), stroke=10, stroke_fill=INK)
    return f


def scene_punch(t):
    zoom = 1.25 - 0.15 * ease(t / 0.6)
    f = cover(wink_face, W, H, zoom=zoom, fx=0.5, fy=0.0)
    # léger tremblement au début
    if t < 0.4:
        dx = int(math.sin(t * 80) * 14 * (1 - t / 0.4))
        f = f.transform(f.size, Image.AFFINE, (1, 0, dx, 0, 1, 0), fillcolor=WHITE)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(o)
    od.rectangle((0, 0, W, 560), fill=RED + (235,))
    k = pop(t / 0.5)
    sz = max(10, int(84 * k))
    od.multiline_text((W // 2, 130), PUNCHLINE, font=font(sz), fill=WHITE, anchor="ma",
                      align="center", spacing=18, stroke_width=8, stroke_fill=DARK_RED)
    if t > 0.7:
        draw_smirk(od, W // 2, 440, max(1, int(55 * pop((t - 0.7) / 0.4))))
    return Image.alpha_composite(f.convert("RGBA"), o).convert("RGB")


def scene_outro(t):
    f = Image.new("RGB", (W, H), RED)
    d = ImageDraw.Draw(f)
    # dégradé
    for yy in range(H):
        c = tuple(int(RED[i] + (DARK_RED[i] - RED[i]) * yy / H) for i in range(3))
        d.line((0, yy, W, yy), fill=c)
    # carte blanche avec logo
    d.rounded_rectangle((90, 170, W - 90, 430), 50, fill=WHITE)
    lg = logo.resize((560, 174), Image.LANCZOS)
    f.paste(lg, ((W - 560) // 2, 210))
    k = ease(t / 0.5)
    text_center(d, W // 2, 520 - int(40 * (1 - k)), "Le prix est TOUJOURS\nsur la publication", font(68), WHITE, spacing=16)
    text_center(d, W // 2, 720, "Pas de surprise, pas de négociation.", font(40, False), (255, 220, 220))
    # mini post
    thumb = img_post.resize((520, int(520 * img_post.height / img_post.width)), Image.LANCZOS)
    s = 0.9 + 0.1 * ease((t - 0.2) / 0.5)
    th = thumb.resize((int(thumb.width * s), int(thumb.height * s)), Image.LANCZOS)
    sh = Image.new("RGBA", (th.width + 60, th.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 30, th.width + 30, th.height + 30), 30, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    f.paste(sh, ((W - sh.width) // 2, 830 - 10), sh)
    f.paste(th, ((W - th.width) // 2, 860))
    if t > 0.8:
        k3 = ease((t - 0.8) / 0.4)
        y0 = 1530 + int(60 * (1 - k3))
        d.rounded_rectangle((110, y0, W - 110, y0 + 120), 60, fill=WHITE)
        text_center(d, W // 2, y0 + 33, "Commandez sur www.dispo.sn", font(44), RED)
        text_center(d, W // 2, y0 + 170, "WhatsApp : 78 012 11 10 • 77 661 09 23", font(38), WHITE)
        text_center(d, W // 2, y0 + 230, "Tél : 33 815 41 34", font(38), WHITE)
    return f


def frame_at(t):
    if t < T_INTRO_END:
        f = scene_intro(t)
    elif t < T_PUNCH:
        f = scene_chat(t - T_INTRO_END)
    elif t < T_OUTRO:
        f = scene_punch(t - T_PUNCH)
    else:
        f = scene_outro(t - T_OUTRO)
    # flash blanc aux transitions
    for tc in (T_INTRO_END, T_PUNCH, T_OUTRO):
        dt = t - tc
        if 0 <= dt < 0.18:
            f = Image.blend(f, Image.new("RGB", (W, H), WHITE), 1 - dt / 0.18)
    return f


def main():
    tmp = tempfile.mkdtemp()
    try:
        n = int(T_END * FPS)
        for i in range(n):
            frame_at(i / FPS).save(os.path.join(tmp, f"{i:05d}.png"), compress_level=1)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
            "-i", os.path.join(tmp, "%05d.png"),
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
            "-c:a", "aac", "-movflags", "+faststart", OUT,
        ], check=True)
        print("OK ->", OUT)
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
