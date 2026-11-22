#!/usr/bin/env python3
"""The picture that tastes of one ingredient.

Draws one picture of food -- a steaming bowl of ramen -- entirely
programmatically with Pillow. No external images, no network, no
randomness: the same input always produces the same bytes.

Writes /output/entry.png (1024x1024, whole PNG, well under 1 MiB).

Run:  python3 main.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

# Canvas is drawn at 2x and downscaled for smooth anti-aliased curves.
S = 2
W = 1024 * S
H = 1024 * S
CX, CY = W // 2, 560 * S  # bowl centre


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def radial_ellipse(draw, box, inner, outer, steps=48):
    """Fill an ellipse with a radial gradient (inner colour at centre)."""
    x0, y0, x1, y1 = box
    for k in range(steps):
        frac = k / steps
        col = lerp(outer, inner, frac)
        dx = (x1 - x0) * frac / 2.0
        dy = (y1 - y0) * frac / 2.0
        draw.ellipse([x0 + dx, y0 + dy, x1 - dx, y1 - dy], fill=col)


def wavy_circle_points(cx, cy, r, phase, wobble=10, n=140, a0=0.0, a1=2 * math.pi):
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        rr = r + wobble * math.sin(3 * a + phase) + 0.4 * wobble * math.sin(7 * a + phase * 2)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.78))
    return pts


def wavy_vertical_points(x0, y0, y1, amp, phase, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        x = x0 + amp * math.sin(2.2 * math.pi * t + phase) * (0.4 + 0.6 * t)
        pts.append((x, y))
    return pts


def draw_table(base):
    draw = ImageDraw.Draw(base, "RGBA")
    # Warm dark wood: radial glow behind the bowl, darker toward the edges.
    radial_ellipse(draw, [-W * 0.25, -H * 0.25, W * 1.25, H * 1.25],
                   (122, 74, 38), (52, 28, 16), steps=40)
    # Plank seams: soft horizontal bands.
    for k in range(6):
        y = int(H * (0.08 + 0.16 * k))
        draw.line([(0, y), (W, y)], fill=(38, 20, 10, 70), width=3 * S)
        draw.line([(0, y + 5 * S), (W, y + 5 * S)], fill=(150, 96, 50, 45), width=2 * S)
    # Warm light pooling from the top left.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    radial_ellipse(gd, [-W * 0.55, -H * 0.55, W * 0.55, H * 0.45],
                   (255, 196, 120, 52), (255, 196, 120, 0), steps=48)
    base.alpha_composite(glow)
    return draw


def draw_bowl(base):
    draw = ImageDraw.Draw(base, "RGBA")
    # Soft shadow under the bowl.
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([CX - 400 * S, CY + 190 * S, CX + 400 * S, CY + 300 * S],
               fill=(0, 0, 0, 130))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28 * S)))
    draw = ImageDraw.Draw(base, "RGBA")
    # Outer lacquer bowl (deep red, darker at the rim's lower edge).
    radial_ellipse(draw, [CX - 400 * S, CY - 300 * S, CX + 400 * S, CY + 300 * S],
                   (168, 44, 32), (88, 16, 14), steps=36)
    # Bowl foot shadow line and rim highlight.
    draw.arc([CX - 400 * S, CY - 300 * S, CX + 400 * S, CY + 300 * S],
             start=200, end=340, fill=(255, 150, 110, 90), width=10 * S)
    draw.arc([CX - 400 * S, CY - 300 * S, CX + 400 * S, CY + 300 * S],
             start=20, end=160, fill=(30, 5, 5, 110), width=12 * S)
    # Cream inner rim.
    draw.ellipse([CX - 348 * S, CY - 252 * S, CX + 348 * S, CY + 252 * S],
                 fill=(244, 228, 196))
    draw.ellipse([CX - 330 * S, CY - 236 * S, CX + 330 * S, CY + 236 * S],
                 fill=(120, 30, 20))
    # Broth surface: rich amber, lighter and glossier toward the centre.
    radial_ellipse(draw, [CX - 322 * S, CY - 228 * S, CX + 322 * S, CY + 228 * S],
                   (214, 128, 46), (128, 62, 18), steps=36)
    # Broth sheen: two soft glossy arcs.
    draw.arc([CX - 300 * S, CY - 210 * S, CX + 300 * S, CY + 210 * S],
             start=205, end=295, fill=(255, 214, 140, 110), width=16 * S)
    draw.arc([CX - 260 * S, CY - 180 * S, CX + 260 * S, CY + 180 * S],
             start=25, end=115, fill=(255, 190, 110, 70), width=10 * S)


def draw_noodles(base):
    draw = ImageDraw.Draw(base, "RGBA")
    golds = [(232, 178, 74), (214, 152, 46), (244, 198, 102), (198, 134, 38)]
    for k in range(19):
        r = 22 * S + k * 15 * S
        phase = k * 1.7
        pts = wavy_circle_points(CX, CY, r, phase, wobble=9 * S)
        draw.line(pts, fill=golds[k % 4] + (255,), width=11 * S, joint="curve")
    # A few bright highlight strands on top.
    for k, r in enumerate((86 * S, 150 * S, 214 * S, 268 * S)):
        pts = wavy_circle_points(CX, CY, r, 0.9 * k + 0.4, wobble=8 * S,
                                 a0=0.6, a1=4.4)
        draw.line(pts, fill=(255, 224, 150, 200), width=5 * S, joint="curve")


def draw_toppings(base):
    draw = ImageDraw.Draw(base, "RGBA")
    # --- Nori sheet leaning on the back-left rim ---
    nori = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nori)
    nd.rounded_rectangle([CX - 300 * S, CY - 380 * S, CX - 185 * S, CY - 150 * S],
                         radius=14 * S, fill=(24, 46, 30, 255))
    nd.rounded_rectangle([CX - 290 * S, CY - 370 * S, CX - 195 * S, CY - 160 * S],
                         radius=11 * S, outline=(58, 96, 64, 160), width=4 * S)
    base.alpha_composite(nori.rotate(-24, center=(CX - 240 * S, CY - 260 * S),
                                     resample=Image.BICUBIC))
    draw = ImageDraw.Draw(base, "RGBA")

    # --- Chashu slices (left) ---
    for (ex, ey, er) in ((CX - 185 * S, CY - 30 * S, 78 * S),
                         (CX - 130 * S, CY + 55 * S, 72 * S)):
        draw.ellipse([ex - er, ey - er * 0.82, ex + er, ey + er * 0.82],
                     fill=(196, 110, 78))
        draw.ellipse([ex - er * 0.72, ey - er * 0.60, ex + er * 0.72, ey + er * 0.60],
                     fill=(222, 150, 112))
        draw.ellipse([ex - er * 0.40, ey - er * 0.34, ex + er * 0.40, ey + er * 0.34],
                     fill=(238, 178, 140))
        draw.arc([ex - er * 0.55, ey - er * 0.45, ex + er * 0.55, ey + er * 0.45],
                 start=40, end=300, fill=(150, 70, 44, 200), width=5 * S)
        draw.ellipse([ex - er * 0.30, ey - er * 0.55, ex - er * 0.05, ey - er * 0.30],
                     fill=(255, 214, 180, 160))

    # --- Soft egg halves (right) ---
    for (ex, ey, er, tilt) in ((CX + 165 * S, CY - 45 * S, 74 * S, -18),
                               (CX + 205 * S, CY + 60 * S, 68 * S, 14)):
        egg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ed = ImageDraw.Draw(egg)
        ed.ellipse([ex - er, ey - er * 0.80, ex + er, ey + er * 0.80],
                   fill=(252, 246, 232, 255))
        ed.ellipse([ex - er * 0.94, ey - er * 0.74, ex + er * 0.94, ey + er * 0.74],
                   outline=(214, 198, 170, 220), width=3 * S)
        # Jammy yolk: deep orange centre fading to gold.
        for i in range(14, 0, -1):
            t = i / 14
            col = lerp((232, 96, 20), (250, 176, 60), t)
            yr = er * 0.52 * t
            ed.ellipse([ex - yr, ey - yr * 0.82, ex + yr, ey + yr * 0.82],
                       fill=col + (255,))
        ed.ellipse([ex - er * 0.20, ey - er * 0.38, ex + er * 0.08, ey - er * 0.14],
                   fill=(255, 226, 160, 220))
        base.alpha_composite(egg.rotate(tilt, center=(ex, ey),
                                        resample=Image.BICUBIC))
        draw = ImageDraw.Draw(base, "RGBA")

    # --- Spring onion rings scattered on the broth ---
    onion_spots = [(CX - 60 * S, CY - 150 * S), (CX + 40 * S, CY - 170 * S),
                   (CX + 120 * S, CY - 130 * S), (CX - 150 * S, CY + 130 * S),
                   (CX - 40 * S, CY + 165 * S), (CX + 70 * S, CY + 150 * S),
                   (CX + 250 * S, CY - 30 * S), (CX - 260 * S, CY + 20 * S),
                   (CX + 10 * S, CY - 60 * S), (CX - 90 * S, CY + 60 * S),
                   (CX + 250 * S, CY + 90 * S), (CX + 150 * S, CY + 190 * S)]
    for i, (ox, oy) in enumerate(onion_spots):
        r = (13 + (i % 3) * 3) * S
        draw.ellipse([ox - r, oy - r * 0.8, ox + r, oy + r * 0.8],
                     outline=(74, 154, 58, 255), width=5 * S)
        draw.ellipse([ox - r * 0.45, oy - r * 0.36, ox + r * 0.45, oy + r * 0.36],
                     fill=(126, 196, 88, 255))

    # --- Chilli oil drops glistening on the broth ---
    for (ox, oy, r) in ((CX - 200 * S, CY - 120 * S, 13 * S),
                        (CX + 90 * S, CY - 190 * S, 10 * S),
                        (CX + 280 * S, CY + 40 * S, 12 * S),
                        (CX - 30 * S, CY + 200 * S, 9 * S),
                        (CX + 180 * S, CY + 170 * S, 8 * S)):
        draw.ellipse([ox - r, oy - r * 0.8, ox + r, oy + r * 0.8],
                     fill=(196, 44, 16, 235))
        draw.ellipse([ox - r * 0.4, oy - r * 0.55, ox + r * 0.1, oy - r * 0.15],
                     fill=(255, 120, 70, 220))


def draw_chopsticks_and_lift(base):
    draw = ImageDraw.Draw(base, "RGBA")
    # Chopsticks enter from the top right, tips meeting over the broth.
    tip = (CX + 70 * S, CY - 140 * S)
    top1 = (CX + 430 * S, CY - 470 * S)
    top2 = (CX + 470 * S, CY - 420 * S)
    for (tx, ty), shade in ((top1, (122, 66, 30)), (top2, (104, 54, 24))):
        draw.line([tip, (tx, ty)], fill=shade + (255,), width=20 * S)
        draw.line([tip, (tx, ty)], fill=(168, 100, 48, 255), width=8 * S)
    # Noodle bundle lifted by the chopsticks, strands hanging to the broth.
    golds = [(232, 178, 74), (214, 152, 46), (244, 198, 102)]
    for k in range(7):
        x0 = tip[0] - 26 * S + k * 9 * S
        pts = wavy_vertical_points(x0, tip[1] - 6 * S, CY + 10 * S,
                                   amp=16 * S, phase=k * 1.3)
        draw.line(pts, fill=golds[k % 3] + (255,), width=10 * S, joint="curve")
    # Highlight strand.
    pts = wavy_vertical_points(tip[0] - 8 * S, tip[1], CY - 20 * S,
                               amp=14 * S, phase=0.5)
    draw.line(pts, fill=(255, 224, 150, 220), width=4 * S, joint="curve")


def draw_steam(base):
    steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for k, x0 in enumerate((CX - 190 * S, CX - 40 * S, CX + 110 * S, CX + 250 * S)):
        pts = wavy_vertical_points(x0, CY - 240 * S, CY - 480 * S - (k % 2) * 40 * S,
                                   amp=34 * S, phase=k * 1.9)
        sd.line(pts, fill=(255, 250, 240, 120), width=26 * S, joint="curve")
    base.alpha_composite(steam.filter(ImageFilter.GaussianBlur(16 * S)))


def draw_vignette(base):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(24, 0, -1):
        t = i / 24
        a = int(95 * (1.0 - t) ** 2)
        od.ellipse([-W * 0.30 * t, -H * 0.30 * t,
                    W * (1 + 0.30 * t), H * (1 + 0.30 * t)],
                   outline=(0, 0, 0, a), width=90 * S)
    base.alpha_composite(overlay)


def main():
    img = Image.new("RGBA", (W, H), (52, 28, 16, 255))
    draw_table(img)
    draw_bowl(img)
    draw_noodles(img)
    draw_toppings(img)
    draw_chopsticks_and_lift(img)
    draw_steam(img)
    draw_vignette(img)
    img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)

    out = os.environ.get("OUTPUT_PATH", "/output/entry.png")
    try:
        os.makedirs(os.path.dirname(out), exist_ok=True)
    except OSError:
        out = os.path.join(os.getcwd(), "output", "entry.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print(out)


if __name__ == "__main__":
    main()
