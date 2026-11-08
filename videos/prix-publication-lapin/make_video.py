"""Mème « vous avez vu le prix donc » avec le lapin Dispo, fond rouge.

Usage : python3 make_video.py SON.mp4   ->  dispo-lapin-prix.mp4 (1080x1920)
Le son est pris au début de SON.mp4 (13,75 s, avant l'écran de fin TikTok).
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dispo-lapin-prix.mp4")
W, H, FPS = 1080, 1920, 30
DUR = 13.75
BPM = 104               # rythme de la danse

RED = (214, 32, 39)
DARK = (120, 10, 15)
INK = (20, 20, 20)
WHITE = (255, 255, 255)
F = "/usr/share/fonts/truetype/dejavu/"


def font(size, bold=True):
    return ImageFont.truetype(F + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def emoji(code, size):
    return Image.open(os.path.join(HERE, "emoji", code + ".png")).convert("RGBA").resize((size, size), Image.LANCZOS)


CAPTION = "Quand le client voit le prix\nsur la publication…\nmais demande quand même"

# (qui, texte, emoji, début, fin)
MESSAGES = [
    ("client", "Bonjour, c'est combien ?", "1f642", 0.6, 5.8),
    ("dispo", "4.000.000", "1f60c", 3.2, 5.8),
    ("client", "Pourtant c'est écrit 3.500.000 sur la publication", "1f928", 5.8, DUR),
    ("dispo", "Ah… vous avez VU le prix donc", "1f602", 9.6, DUR),
]
T_WINK = 9.6            # saut du lapin sur la punchline
T_BANNER = 11.6


def ease_back(t):
    t = max(0.0, min(1.0, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def sticker(img, border=14):
    """Contour blanc autour du personnage détouré (se détache du fond rouge)."""
    pad = border * 2
    big = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    big.paste(img, (pad, pad), img)
    a = big.getchannel("A").point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(border * 2 + 1))
    out = Image.new("RGBA", big.size, WHITE + (0,))
    out.putalpha(a.filter(ImageFilter.GaussianBlur(1.5)))
    out.alpha_composite(big)
    return out


def bubble(who, txt, code):
    bf = font(56)
    md = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    maxw = 900
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if md.textlength(t, font=bf) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    es = 72
    lastw = md.textlength(lines[-1], font=bf)
    if lastw + es + 16 > maxw:
        lines.append("")
        lastw = 0
    tw = max(max(md.textlength(l, font=bf) for l in lines), lastw + es + 16)
    bw, bh = int(tw + 80), int(len(lines) * 70 + 110)
    img = Image.new("RGBA", (bw, bh + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fill = WHITE if who == "client" else (220, 248, 198)
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), 36, fill=fill, outline=INK, width=5)
    # queue : en bas à gauche pour le client, en bas à droite (vers le lapin) pour Dispo
    tx = 80 if who == "client" else bw - 200
    tip = (tx - 30, bh + 46) if who == "client" else (tx + 40, bh + 46)
    d.polygon([(tx - 30, bh - 6), (tx + 30, bh - 6), tip], fill=fill)
    d.line([(tx - 30, bh - 3), tip, (tx + 30, bh - 3)], fill=INK, width=5)
    d.text((40, 16), "Le client" if who == "client" else "Dispo", font=font(32),
           fill=(30, 110, 200) if who == "client" else RED)
    for i, l in enumerate(lines):
        d.text((40, 60 + i * 70), l, font=bf, fill=INK)
    img.alpha_composite(emoji(code, es), (int(40 + lastw + 14), 60 + (len(lines) - 1) * 70 - 4))
    return img


def main(sound):
    # fond rouge avec léger dégradé + halo
    bg = Image.new("RGB", (W, H), RED)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=tuple(int(RED[i] * (1 - 0.25 * k) + DARK[i] * 0.25 * k) for i in range(3)))
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse((80, 900, 1180, 2000), fill=90)
    bg = Image.composite(Image.new("RGB", (W, H), (255, 90, 80)), bg, halo.filter(ImageFilter.GaussianBlur(160)))
    cd = ImageDraw.Draw(bg)
    cf = font(54)
    cd.multiline_text((W // 2, 70), CAPTION, font=cf, fill=WHITE, anchor="ma", align="center",
                      spacing=12, stroke_width=6, stroke_fill=INK)
    lw = cd.textlength(CAPTION.split("\n")[-1], font=cf)
    bg = bg.convert("RGBA")
    bg.alpha_composite(emoji("1f602", 68), (int(W / 2 + lw / 2 + 12), 70 + 2 * (cf.size + 12) + 2))

    def load(name, height):
        im = Image.open(os.path.join(HERE, "images", name)).convert("RGBA")
        im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
        return sticker(im)

    bunny = load("lapin-clin-oeil.png", 1000)
    bubbles = [(who, bubble(who, t, e), t0, t1) for who, t, e, t0, t1 in MESSAGES]

    def frame(t):
        f = bg.copy()
        beat = t * BPM / 60 * math.pi
        # danse : rebond sur le temps + balancement
        bounce = abs(math.sin(beat)) * 60
        sway = math.sin(beat / 2) * 10
        squash = 1 + 0.03 * math.cos(2 * beat)
        if T_WINK <= t < T_WINK + 0.5:                 # petit saut sur la punchline
            bounce += math.sin((t - T_WINK) / 0.5 * math.pi) * 60
        bw = max(1, int(bunny.width * (2 - squash)))
        bh = max(1, int(bunny.height * squash))
        b = bunny.resize((bw, bh), Image.LANCZOS).rotate(sway, resample=Image.BICUBIC, expand=True)
        cx = 640 + math.sin(beat / 2) * 70
        f.alpha_composite(b, (int(cx - b.width / 2), int(H + 30 - b.height - bounce)))

        # bulles : le client en haut à gauche, Dispo juste au-dessus du lapin
        for who, img, t0, t1 in bubbles:
            if not (t0 <= t < t1):
                continue
            k = ease_back((t - t0) / 0.35)
            iw, ih = max(1, int(img.width * k)), max(1, int(img.height * k))
            s = img.resize((iw, ih), Image.LANCZOS)
            if who == "client":
                f.alpha_composite(s, (50, 340 + (img.height - ih) // 2))
            else:
                # sous la bulle du client, au-dessus de la tête du lapin
                y = 640 if t0 < 6 else 700
                f.alpha_composite(s, (W - 40 - iw, y + (img.height - ih) // 2))

        if t > T_BANNER:
            k = ease_back((t - T_BANNER) / 0.4)
            y = int(H - 250 * k)
            dd = ImageDraw.Draw(f)
            dd.rounded_rectangle((60, y, W - 60, y + 170), 40, fill=WHITE, outline=INK, width=5)
            dd.text((W // 2, y + 22), "Le prix est TOUJOURS sur la publication", font=font(38), fill=INK, anchor="ma")
            dd.text((W // 2, y + 80), "www.dispo.sn", font=font(62), fill=RED, anchor="ma")
        return f.convert("RGB")

    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-t", str(DUR), "-i", sound,
                            "-map", "0:v", "-map", "1:a", "-af", f"afade=t=out:st={DUR - 0.4}:d=0.4",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                            "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                           stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        enc.stdin.write(frame(i / FPS).tobytes())
    enc.stdin.close()
    enc.wait()
    print("OK ->", OUT)


if __name__ == "__main__":
    main(sys.argv[1])
