#!/usr/bin/env python3
"""Draw the 25 Nov 2026 world-news front page (1024x1024 PNG) with PIL only.
Flat editorial infographic: date header + 6 verified stories, crisp text,
no AI-generated imagery (avoids garbled text). Deterministic output.
Stories were all first reported on Wednesday 25 November 2026 (any timezone),
cross-checked against Just Security Early Edition 25 Nov, the 25 Nov evening
roundup and Principia's 25 Nov digest.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (22, 35, 63)
PAPER = (245, 241, 230)
INK = (22, 35, 63)
GREY = (72, 72, 72)
GOLD = (217, 164, 65)
WHITE = (255, 255, 255)
BORDER = (216, 210, 192)


def font(bold, size):
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def burst(d, cx, cy, s, fill=(255, 120, 0)):
    r_out, r_in, n = s, s * 0.45, 8
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def icon_ship(d, x, y, s, col):
    d.polygon([(x, y + 8), (x + s, y + 8), (x + s - 8, y + 20), (x + 8, y + 20)], fill=col)
    d.rectangle([x + s * 0.35, y - 6, x + s * 0.45, y + 8], fill=col)
    d.rectangle([x + s * 0.55, y - 2, x + s * 0.65, y + 8], fill=col)


def icon_flame(d, x, y, s, col):
    d.polygon(
        [
            (x + s * 0.5, y),
            (x + s * 0.85, y + s * 0.45),
            (x + s, y + s * 0.8),
            (x + s * 0.5, y + s),
            (x, y + s * 0.8),
            (x + s * 0.15, y + s * 0.45),
        ],
        fill=col,
    )


def icon_store(d, x, y, s, col):
    d.rectangle([x, y + 6, x + s, y + s], fill=col)
    d.polygon([(x - 4, y + 8), (x + s + 4, y + 8), (x + s, y - 4), (x, y - 4)], fill=col)
    d.rectangle([x + s * 0.42, y + s * 0.55, x + s * 0.58, y + s], fill=WHITE)


def icon_handshake(d, x, y, s, col):
    # Two interlocking rings: a signed pact.
    d.ellipse([x, y + 4, x + s * 0.55, y + s * 0.75], outline=col, width=5)
    d.ellipse([x + s * 0.45, y + s * 0.25, x + s, y + s], outline=col, width=5)


def icon_chart(d, x, y, s, col):
    bars = [0.5, 0.8, 0.35, 0.6]
    bw = s / 5
    for i, h in enumerate(bars):
        bx = x + i * (bw + 3)
        d.rectangle([bx, y + s - h * s, bx + bw, y + s], fill=col)
    d.line([x, y + 2, x + s, y + s * 0.55], fill=(180, 35, 24), width=4)


def icon_cross(d, x, y, s, col):
    d.rectangle([x + s * 0.4, y, x + s * 0.6, y + s], fill=col)
    d.rectangle([x, y + s * 0.4, x + s, y + s * 0.6], fill=col)


PANELS = [
    dict(
        kicker="MIDDLE EAST  ·  ENERGY",
        accent=(180, 35, 24),
        tint=(253, 236, 234),
        head="TWO TANKERS HIT BY MINES",
        sub="Iran's IRGC says two oil tankers struck naval mines and caught fire in the Strait of Hormuz.",
        icon="burst",
    ),
    dict(
        kicker="MIDDLE EAST  ·  SAUDI ARABIA",
        accent=(181, 71, 8),
        tint=(254, 243, 226),
        head="HOUTHIS SAY THEY HIT REFINERY",
        sub="Yemen's Houthis say they attacked Saudi Arabia's Ras Tanura oil refinery, causing fires.",
        icon="flame",
    ),
    dict(
        kicker="AMERICAS  ·  COLOMBIA",
        accent=(193, 21, 116),
        tint=(253, 237, 245),
        head="CARTAGENA HOSTAGES FREED",
        sub="Colombian forces storm the supermarket siege and free every remaining hostage.",
        icon="store",
    ),
    dict(
        kicker="PACIFIC  ·  SECURITY",
        accent=(11, 74, 111),
        tint=(230, 242, 247),
        head="AUSTRALIA–SOLOMONS PACT SIGNED",
        sub="Treaty signed in Canberra bars any foreign military base on the Solomon Islands.",
        icon="handshake",
    ),
    dict(
        kicker="MARKETS  ·  ASIA",
        accent=(23, 92, 211),
        tint=(234, 241, 254),
        head="ASIAN MARKETS PLUNGE",
        sub="KOSPI falls 6.16%, Nikkei 2.78% as the AI-stock selloff spreads across Asia.",
        icon="chart",
    ),
    dict(
        kicker="AFRICA  ·  SUDAN",
        accent=(105, 65, 198),
        tint=(241, 235, 253),
        head="RSF STRIKES KILL 19 CIVILIANS",
        sub="Drone strikes by Sudan's Rapid Support Forces kill 19 and wound 20 in two cities.",
        icon="cross",
    ),
]

ICONS = {
    "burst": burst,
    "flame": icon_flame,
    "store": icon_store,
    "handshake": icon_handshake,
    "chart": icon_chart,
    "cross": icon_cross,
    "ship": icon_ship,
}


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Header band
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.rectangle([0, 148, W, 154], fill=GOLD)
    d.text((48, 26), "THE WORLD IN ONE DAY", font=font(True, 46), fill=WHITE)
    d.text(
        (48, 88),
        "WEDNESDAY, 25 NOVEMBER 2026",
        font=font(True, 30),
        fill=GOLD,
    )
    d.text(
        (48, 122),
        "Six stories that defined the day",
        font=font(False, 20),
        fill=(200, 205, 220),
    )
    burst(d, 936, 74, 34, fill=GOLD)

    # Panels: 2 columns x 3 rows
    margin, gap = 32, 24
    pw = (W - 2 * margin - gap) // 2
    ph = 236
    top = 178
    for i, p in enumerate(PANELS):
        col, row = i % 2, i // 2
        x0 = margin + col * (pw + gap)
        y0 = top + row * (ph + gap)
        x1, y1 = x0 + pw, y0 + ph
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=p["tint"], outline=BORDER, width=2)
        d.rectangle([x0 + 14, y0 + 14, x0 + 20, y0 + 44], fill=p["accent"])
        d.text((x0 + 32, y0 + 16), p["kicker"], font=font(True, 17), fill=p["accent"])
        # Icon at top right
        ICONS[p["icon"]](d, x1 - 58, y0 + 16, 34, p["accent"])
        lines = wrap(d, p["head"], font(True, 30), pw - 32)
        y = y0 + 52
        for ln in lines[:2]:
            d.text((x0 + 16, y), ln, font=font(True, 30), fill=INK)
            y += 36
        slines = wrap(d, p["sub"], font(False, 19), pw - 32)
        y += 8
        for ln in slines[:3]:
            d.text((x0 + 16, y), ln, font=font(False, 19), fill=GREY)
            y += 25

    # Footer
    fy = top + 3 * ph + 2 * gap + 14
    d.line([margin, fy, W - margin, fy], fill=BORDER, width=2)
    d.text(
        (margin, fy + 12),
        "All six events happened or were first reported on 25 November 2026.",
        font=font(False, 19),
        fill=GREY,
    )
    d.text(
        (margin, fy + 38),
        "Sources: Just Security Early Edition · AP · Reuters · Principia",
        font=font(False, 17),
        fill=(130, 130, 130),
    )

    img.save("entry.png", optimize=True)
    print("wrote entry.png", os.path.getsize("entry.png"), "bytes")


if __name__ == "__main__":
    main()
