"""Mème « chatons qui dansent » version Dispo : le client qui demande le prix.

Reprend la vidéo des chatons (fond orange), remplace les textes anglais par le
sketch Dispo et met le son de la vidéo sénégalaise.

Usage :
  python3 make_video.py CHATONS.mp4 SON.mp4 DOSSIER_EMOJIS
-> dispo-chatons-prix.mp4 (1080x1920)
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dispo-chatons-prix.mp4")
W, H, FPS = 1080, 1920, 30
DUR = 13.75            # le son s'arrête là (après : écran de fin TikTok)
SX = W / 576           # vidéo source en 576x1024

ORANGE = (253, 87, 0)
RED = (214, 32, 39)
INK = (20, 20, 20)
WHITE = (255, 255, 255)

F = "/usr/share/fonts/truetype/dejavu/"
def font(size, bold=True):
    return ImageFont.truetype(F + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)

CAPTION = "Quand le client voit le prix\nsur la publication…\nmais demande quand même"
CAPTION_EMOJI = "1f602"

# (qui, texte, emoji, début, fin)
MESSAGES = [
    ("client", "Bonjour, c'est combien ?", "1f642", 0.6, 3.3),
    ("dispo", "4.000.000", "1f60c", 3.3, 5.8),
    ("client", "Pourtant c'est écrit 3.500.000 sur la publication", "1f928", 5.8, 9.6),
    ("dispo", "Ah… vous avez VU le prix donc", "1f602", 9.6, DUR),
]


def ease_back(t):
    t = max(0.0, min(1.0, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def S(v):
    return int(round(v * SX))


def main(kitten, sound, emoji_dir):
    def emoji(code, size):
        return Image.open(os.path.join(emoji_dir, code + ".png")).convert("RGBA").resize((size, size), Image.LANCZOS)

    logo = Image.open(os.path.join(HERE, "../prix-publication/images/hp304.png")).convert("RGB").crop((40, 0, 400, 112))

    # ---------- calque fixe : cache les textes anglais + nouveaux textes
    static = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(static)
    for x0, y0, x1, y1 in [(40, 150, 536, 222), (400, 272, 460, 308), (96, 333, 233, 374)]:
        d.rectangle((S(x0), S(y0), S(x1), S(y1)), fill=ORANGE)
    d.rectangle((0, 0, W, S(150)), fill=ORANGE)
    cf = font(52)
    d.multiline_text((W // 2, 70), CAPTION, font=cf, fill=WHITE, anchor="ma", align="center",
                     spacing=12, stroke_width=6, stroke_fill=INK)
    last = CAPTION.split("\n")[-1]
    lw = d.textlength(last, font=cf)
    ly = 70 + 2 * (cf.size + 12) + 4
    static.alpha_composite(emoji(CAPTION_EMOJI, 66), (int(W / 2 + lw / 2 + 12), ly))
    # étiquettes
    lf = font(44)
    d.text((S(104), S(340)), "Le client :", font=lf, fill=WHITE, stroke_width=5, stroke_fill=INK)
    pill_w, pill_h = 330, 76
    px, py = S(380), S(268)
    d.rounded_rectangle((px, py, px + pill_w, py + pill_h), 38, fill=WHITE, outline=INK, width=4)
    static.paste(logo.resize((200, 62), Image.LANCZOS), (px + 18, py + 7))
    d.text((px + 228, py + 12), ":", font=lf, fill=INK)

    # ---------- bulles
    bf = font(56)
    def bubble(who, txt, code):
        md = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        maxw = 880
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
        tw = max(md.textlength(l, font=bf) for l in lines)
        lastw = md.textlength(lines[-1], font=bf)
        if lastw + es + 16 > maxw:
            lines.append("")
            lastw = 0
        tw = max(tw, lastw + es + 16)
        bw, bh = int(tw + 80), int(len(lines) * 70 + 110)
        img = Image.new("RGBA", (bw, bh + 40), (0, 0, 0, 0))
        bd = ImageDraw.Draw(img)
        fill = WHITE if who == "client" else (220, 248, 198)
        bd.rounded_rectangle((0, 0, bw - 1, bh - 1), 36, fill=fill, outline=INK, width=5)
        tx = 70 if who == "client" else bw - 70
        bd.polygon([(tx - 30, bh - 6), (tx + 30, bh - 6), (tx + (-25 if who == "client" else 25), bh + 38)], fill=fill)
        bd.line([(tx - 30, bh - 3), (tx + (-25 if who == "client" else 25), bh + 38), (tx + 30, bh - 3)], fill=INK, width=5)
        bd.text((40, 16), "Client" if who == "client" else "Dispo", font=font(32), fill=(30, 110, 200) if who == "client" else RED)
        for i, l in enumerate(lines):
            bd.text((40, 60 + i * 70), l, font=bf, fill=INK)
        img.alpha_composite(emoji(code, es), (int(40 + lastw + 14), 60 + (len(lines) - 1) * 70 - 4))
        return img

    bubbles = [(who, bubble(who, t, e), t0, t1) for who, t, e, t0, t1 in MESSAGES]

    def overlay(t):
        o = static.copy()
        for who, b, t0, t1 in bubbles:
            if t0 <= t < t1:
                k = ease_back((t - t0) / 0.35)
                bw, bh = max(1, int(b.width * k)), max(1, int(b.height * k))
                bs = b.resize((bw, bh), Image.LANCZOS)
                # zone des bulles d'origine (x 180-470, y 530-650 en 576x1024) toujours couverte
                cy = 1110
                if who == "client":
                    x = 60
                else:
                    x = W - 60 - bw
                if t0 >= 9.6:          # punchline : centrée et large
                    x = (W - bw) // 2
                o.alpha_composite(bs, (x, int(cy - bh / 2)))
        # bandeau final
        if t > 11.6:
            k = ease_back((t - 11.6) / 0.4)
            y = int(H - 260 * k)
            bd = ImageDraw.Draw(o)
            bd.rounded_rectangle((60, y, W - 60, y + 170), 40, fill=RED, outline=WHITE, width=5)
            bd.text((W // 2, y + 22), "Le prix est TOUJOURS sur la publication", font=font(38), fill=WHITE, anchor="ma")
            bd.text((W // 2, y + 82), "www.dispo.sn", font=font(60), fill=WHITE, anchor="ma")
        return o

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", kitten, "-t", str(DUR),
                            "-vf", f"scale={W}:{H}:flags=lanczos,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-ss", "0", "-t", str(DUR), "-i", sound,
                            "-map", "0:v", "-map", "1:a", "-af", f"afade=t=out:st={DUR - 0.4}:d=0.4",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                            "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                           stdin=subprocess.PIPE)
    n = 0
    while True:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3:
            break
        fr = Image.frombuffer("RGB", (W, H), raw).convert("RGBA")
        fr.alpha_composite(overlay(n / FPS))
        enc.stdin.write(fr.convert("RGB").tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print("OK ->", OUT, n, "images")


if __name__ == "__main__":
    main(*sys.argv[1:4])
