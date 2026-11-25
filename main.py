#!/usr/bin/env python3
"""news-image-20261125 r2 — "The World in One Day".

Draws a newspaper poster summing up Wednesday 25 November 2026 in six
panels. Pure Python 3.13 stdlib, no network, fully deterministic.
Renders at 2048x2048 and downscales to 1024x1024, writes
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Stories (all happened or first reported on 25 Nov 2026, verified from
the day's wires on 25 Nov ~10:30 UTC):
  1. Shenzhou-24 launches 00:18 UTC and docks at Tiangong 03:56 UTC,
     carrying Muhammad Zeeshan Ali, the first Pakistani in orbit.
  2. Nikkei closes -2.78% at 57,011.62 in an AI sell-off; S&P 500 -0.5%.
  3. Cartagena supermarket siege ends at dawn: all remaining hostages
     freed, one gunman killed, four detained.
  4. Bangladesh raises garment workers' minimum wage 36% to Tk17,000.
  5. Rescuers recover 3 bodies from a flooded Bogor gold mine;
     26 miners still trapped.
  6. Kilmar Abrego Garcia leaves the US voluntarily for Spain, ending
     a 20-month deportation fight.
Rejected as misdated: Senegal's AFCON title (CAS ruled 24 Nov),
Champions League results (matches played 24 Nov evening).
"""

import os
import struct
import zlib

S = 2048            # supersampled canvas
OUT = 1024          # final size
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

# ---------------------------------------------------------------- canvas

buf = bytearray(S * S * 3)


def px(x, y, rgb):
    if 0 <= x < S and 0 <= y < S:
        i = (y * S + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = rgb


def rect(x0, y0, x1, y1, rgb):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(S, x1)
    y1 = min(S, y1)
    for y in range(y0, y1):
        base = (y * S + x0) * 3
        r, g, b = rgb
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            buf[i], buf[i + 1], buf[i + 2] = r, g, b


def disc(cx, cy, r, rgb):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                px(x, y, rgb)


def ellipse(cx, cy, rx, ry, rgb):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                px(x, y, rgb)


def poly(points, rgb):
    """Scanline-filled polygon, points = list of (x, y)."""
    if not points:
        return
    ys = [p[1] for p in points]
    y0, y1 = min(ys), max(ys)
    n = len(points)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, ya = points[i]
            x2, yb = points[(i + 1) % n]
            if ya == yb:
                continue
            if (ya <= y < yb) or (yb <= y < ya):
                t = (y - ya) / (yb - ya)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                px(x, y, rgb)


def thick_line(x0, y0, x1, y1, rgb, w):
    dx, dy = x1 - x0, y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    r = max(1, w // 2)
    for s in range(steps + 1):
        t = s / steps
        disc(int(x0 + dx * t), int(y0 + dy * t), r, rgb)


def thin_line(x0, y0, x1, y1, rgb):
    dx, dy = x1 - x0, y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    for s in range(steps + 1):
        t = s / steps
        px(int(x0 + dx * t), int(y0 + dy * t), rgb)


# ---------------------------------------------------------------- font
# 5x7 bitmap font, uppercase + digits + punctuation used by this poster.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "•": ("00000", "00100", "01110", "01110", "01110", "00100", "00000"),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, rgb):
    for ch in s:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    rect(x + col * scale, y + row * scale,
                         x + (col + 1) * scale, y + (row + 1) * scale, rgb)
        x += 6 * scale


def draw_text_centered(cx, y, s, scale, rgb):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, rgb)


def wrap(s, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- colours

PAPER = (246, 241, 231)
INK = (22, 22, 34)
NAVY = (20, 38, 77)
NAVY_D = (11, 26, 54)
RED = (178, 44, 36)
GOLD = (214, 164, 48)
WHITE = (255, 255, 255)
CREAM = (250, 246, 238)
GREY = (120, 120, 128)
SKY = (126, 178, 214)
SKY_D = (70, 120, 170)

# ---------------------------------------------------------------- scenes
# Each scene draws inside (sx, sy, sw, sh). All coordinates are in the
# 2048 canvas; scenes are simple bold shapes so they read at 300 px.


def scene_space(sx, sy, sw, sh):
    rect(sx, sy, sx + sw, sy + sh, NAVY_D)
    # deterministic stars
    for i in range(46):
        x = sx + (i * 173 + 41) % sw
        y = sy + (i * 97 + 23) % (sh - 30)
        r = 2 + (i * 7) % 4
        disc(x, y, r, WHITE if i % 3 else GOLD)
    # Earth arc at the bottom (a dome that stays inside the scene)
    import math
    _ecx, _ecy, _er = sx + sw // 2, sy + sh, 170
    _arc = [(_ecx + int(_er * math.cos(math.radians(a))),
             _ecy + int(_er * math.sin(math.radians(a))))
            for a in range(180, 361, 6)]
    poly(_arc + [(_ecx + _er, _ecy), (_ecx - _er, _ecy)], (46, 120, 92))
    disc(_ecx - 60, _ecy - 62, 34, (86, 160, 110))
    disc(_ecx + 80, _ecy - 40, 26, (86, 160, 110))
    # space station: hub + solar panels
    cx, cy = sx + sw - 190, sy + 62
    rect(cx - 150, cy - 16, cx - 60, cy + 16, (90, 130, 190))
    rect(cx + 60, cy - 16, cx + 150, cy + 16, (90, 130, 190))
    rect(cx - 60, cy - 22, cx + 60, cy + 22, (200, 205, 210))
    disc(cx, cy, 26, (150, 155, 165))
    # rocket climbing, flame below
    rx, ry = sx + 200, sy + 60
    poly([(rx, ry - 52), (rx + 26, ry), (rx - 26, ry)], RED)
    rect(rx - 26, ry, rx + 26, ry + 96, WHITE)
    rect(rx - 26, ry + 40, rx + 26, ry + 58, (30, 90, 160))
    poly([(rx - 26, ry + 96), (rx + 26, ry + 96), (rx, ry + 150)], GOLD)
    poly([(rx - 12, ry + 96), (rx + 12, ry + 96), (rx, ry + 128)], (240, 120, 40))
    poly([(rx - 40, ry + 70), (rx - 26, ry + 60), (rx - 26, ry + 96)], RED)
    poly([(rx + 40, ry + 70), (rx + 26, ry + 60), (rx + 26, ry + 96)], RED)


def scene_markets(sx, sy, sw, sh):
    rect(sx, sy, sx + sw, sy + sh, (253, 243, 231))
    # faint grid
    for gx in range(sx + 60, sx + sw, 110):
        thin_line(gx, sy + 10, gx, sy + sh - 10, (225, 215, 200))
    for gy in range(sy + 30, sy + sh, 48):
        thin_line(sx + 10, gy, sx + sw - 10, gy, (225, 215, 200))
    # falling candlesticks
    base_y = sy + 34
    bars = [(70, 60), (150, 84), (240, 66), (330, 108), (420, 96),
            (510, 132), (600, 118), (690, 150), (780, 138)]
    for bx, bh in bars:
        rect(sx + bx, base_y + bh - 26, sx + bx + 52, base_y + bh + 26, RED)
        thin_line(sx + bx + 26, base_y + bh - 44, sx + bx + 26,
                  base_y + bh + 44, RED)
    # steep red trend line with arrowhead
    pts = [(sx + 30, sy + 40), (sx + 210, sy + 74), (sx + 400, sy + 66),
           (sx + 580, sy + 118), (sx + 760, sy + 108), (sx + 920, sy + 178)]
    for a, b in zip(pts, pts[1:]):
        thick_line(a[0], a[1], b[0], b[1], RED, 12)
    ex, ey = pts[-1]
    poly([(ex, ey), (ex - 44, ey - 26), (ex - 18, ey + 6)], RED)


def scene_cartagena(sx, sy, sw, sh):
    rect(sx, sy, sx + sw, sy + sh, (232, 178, 120))
    # dusk sky band + sun
    rect(sx, sy, sx + sw, sy + 70, (240, 150, 90))
    disc(sx + sw - 130, sy + 46, 34, (255, 220, 140))
    # supermarket block
    rect(sx + 60, sy + 96, sx + sw - 60, sy + sh - 8, (250, 246, 238))
    rect(sx + 60, sy + 96, sx + sw - 60, sy + 132, (20, 90, 60))
    draw_text(sx + 90, sy + 104, "EXITO", 5, WHITE)
    # shop windows, one lit
    rect(sx + 96, sy + 156, sx + 300, sy + sh - 40, (120, 160, 190))
    rect(sx + 340, sy + 156, sx + 560, sy + sh - 40, (70, 110, 150))
    rect(sx + 600, sy + 156, sx + sw - 96, sy + sh - 40, (120, 160, 190))
    # freed shoppers walking out, arms raised
    for i, fx in enumerate((300, 470, 640)):
        fy = sy + sh - 16
        disc(fx, fy - 52, 16, (40, 40, 60) if i % 2 else (90, 40, 40))
        rect(fx - 16, fy - 36, fx + 16, fy + 8, (40, 40, 60) if i % 2 else (90, 40, 40))
        thick_line(fx - 14, fy - 30, fx - 30, fy - 66, (40, 40, 60), 8)
        thick_line(fx + 14, fy - 30, fx + 30, fy - 66, (40, 40, 60), 8)
    # police officer with raised arm at the door
    ox, oy = sx + sw - 110, sy + sh - 16
    disc(ox, oy - 52, 17, NAVY)
    rect(ox - 18, oy - 36, ox + 18, oy + 8, NAVY)
    thick_line(ox + 16, oy - 30, ox + 44, oy - 78, NAVY, 9)
    disc(ox + 8, oy - 62, 10, NAVY)


def scene_bangladesh(sx, sy, sw, sh):
    rect(sx, sy, sx + sw, sy + sh, (250, 226, 170))
    # factory with sawtooth roof
    rect(sx + 60, sy + 90, sx + sw - 60, sy + sh - 8, (190, 90, 60))
    for i in range(4):
        x0 = sx + 60 + i * 210
        poly([(x0, sy + 90), (x0 + 105, sy + 34), (x0 + 210, sy + 90)],
             (150, 60, 40))
    # windows in a row
    for i in range(5):
        wx = sx + 110 + i * 165
        rect(wx, sy + 130, wx + 90, sy + 178, (255, 240, 190))
    # sewing tables: workers + machines
    for i, wx in enumerate((150, 400, 650)):
        wy = sy + sh - 60
        disc(wx, wy - 74, 17, (40, 60, 90) if i % 2 == 0 else (110, 40, 60))
        rect(wx - 18, wy - 58, wx + 18, wy - 6, (40, 60, 90) if i % 2 == 0 else (110, 40, 60))
        rect(wx - 70, wy - 6, wx + 90, wy + 8, (90, 60, 40))
        rect(wx + 20, wy - 44, wx + 76, wy - 6, (60, 60, 70))
    # fabric rolls
    for i, (fx, fc) in enumerate(((830, (30, 120, 90)), (880, (200, 60, 120)))):
        rect(sx + fx, sy + sh - 120, sx + fx + 34, sy + sh - 30, fc)


def scene_mine(sx, sy, sw, sh):
    rect(sx, sy, sx + sw, sy + sh, (52, 66, 92))
    # rain streaks
    for i in range(34):
        x = sx + (i * 151 + 30) % sw
        y = sy + (i * 89 + 12) % (sh - 40)
        thin_line(x, y, x - 12, y + 34, (140, 170, 210))
    # hillside + dark shaft mouth
    poly([(sx, sy + sh), (sx, sy + 120), (sx + sw, sy + 96), (sx + sw, sy + sh)],
         (38, 52, 40))
    poly([(sx + sw // 2 - 130, sy + sh), (sx + sw // 2 - 84, sy + 128),
          (sx + sw // 2 + 84, sy + 128), (sx + sw // 2 + 130, sy + sh)],
         (12, 12, 16))
    # ropes into the shaft
    thin_line(sx + sw // 2 - 60, sy + 128, sx + sw // 2 - 60, sy + sh - 20, GOLD)
    thin_line(sx + sw // 2 + 60, sy + 128, sx + sw // 2 + 60, sy + sh - 20, GOLD)
    # rescuers in yellow helmets at the rim
    for hx in (sx + 150, sx + sw - 170):
        hy = sy + 132
        disc(hx, hy - 8, 22, (250, 200, 40))
        rect(hx - 24, hy + 12, hx + 24, hy + 78, (220, 90, 40))
        disc(hx + 26, hy + 30, 7, (255, 240, 160))
    # headlamp glow at the shaft
    disc(sx + sw // 2, sy + 168, 12, (255, 240, 160))


def scene_plane(sx, sy, sw, sh):
    rect(sx, sy, sx + sw, sy + sh, SKY)
    for i in range(5):
        cx = sx + (i * 211 + 80) % sw
        cy = sy + 22 + (i * 31) % 46
        ellipse(cx, cy, 74, 20, WHITE)
        ellipse(cx + 44, cy + 8, 56, 16, WHITE)
    # dashed flight path USA -> Spain
    for t in range(0, 101, 6):
        u = t / 100.0
        x = sx + 120 + int(u * (sw - 260))
        y = sy + 170 - int(120 * 4 * u * (1 - u))
        disc(x, y, 6, NAVY)
    draw_text(sx + 60, sy + 176, "USA", 5, NAVY)
    draw_text(sx + sw - 190, sy + 176, "SPAIN", 5, NAVY)
    # airplane silhouette, dark navy so it reads against the sky
    px0, py0 = sx + sw // 2 - 40, sy + 66
    ellipse(px0, py0, 150, 26, NAVY)
    poly([(px0 + 130, py0 - 8), (px0 + 210, py0 - 2), (px0 + 150, py0 + 12)], NAVY)
    poly([(px0 - 30, py0 - 60), (px0 + 30, py0 - 60), (px0 + 60, py0 - 4),
          (px0 - 10, py0 + 6)], NAVY)
    poly([(px0 - 150, py0 - 6), (px0 - 96, py0 - 2), (px0 - 120, py0 + 14)], NAVY)
    rect(px0 + 40, py0 - 22, px0 + 90, py0 - 8, WHITE)
    rect(px0 + 96, py0 - 22, px0 + 120, py0 - 8, WHITE)


# ---------------------------------------------------------------- panels

PANELS = [
    dict(tag="SPACE • CHINA", colour=NAVY, scene=scene_space,
         headline="FIRST PAKISTANI IN ORBIT",
         sub="SHENZHOU-24 DOCKS AT TIANGONG • FIRST FOREIGN VISITOR ABOARD"),
    dict(tag="MARKETS • JAPAN", colour=RED, scene=scene_markets,
         headline="NIKKEI SINKS 2.8% ON AI FEARS",
         sub="NIKKEI CLOSES AT 57,012 • S&P 500 DOWN 0.5% TOO"),
    dict(tag="COLOMBIA • RESCUE", colour=(20, 90, 60), scene=scene_cartagena,
         headline="ALL HOSTAGES FREED IN CARTAGENA",
         sub="SIEGE ENDS AFTER 20 HOURS • ONE GUNMAN KILLED, 4 DETAINED"),
    dict(tag="LABOUR • BANGLADESH", colour=(150, 60, 40), scene=scene_bangladesh,
         headline="BANGLADESH RAISES GARMENT PAY 36%",
         sub="MINIMUM PAY NOW TK17,000 • AFTER WEEKS OF PROTESTS"),
    dict(tag="DISASTER • INDONESIA", colour=(52, 66, 92), scene=scene_mine,
         headline="THREE BODIES FOUND IN FLOODED MINE",
         sub="RESCUERS FIND 3 BODIES • 26 MINERS TRAPPED IN BOGOR"),
    dict(tag="MIGRATION • USA", colour=SKY_D, scene=scene_plane,
         headline="ABREGO GARCIA LEAVES US FOR SPAIN",
         sub="ENDS A 20-MONTH LEGAL FIGHT • DEPARTS VOLUNTARILY FOR SPAIN"),
]


def draw_panel(p, x, y, w, h):
    rect(x, y, x + w, y + h, CREAM)
    # tag strip
    rect(x, y, x + w, y + 56, p["colour"])
    draw_text(x + 28, y + 11, p["tag"], 5, WHITE)
    # scene
    p["scene"](x, y + 56, w, 220)
    # headline, up to 2 lines
    lines = wrap(p["headline"], 8, w - 56)
    hy = y + 56 + 220 + 18
    for ln in lines[:2]:
        draw_text(x + 28, hy, ln, 8, INK)
        hy += 62
    # divider
    thin_line(x + 28, y + 56 + 220 + 150, x + w - 28, y + 56 + 220 + 150, GREY)
    # sub-line, up to 2 lines
    slines = wrap(p["sub"], 5, w - 56)
    sy = y + 56 + 220 + 166
    for ln in slines[:2]:
        draw_text(x + 28, sy, ln, 5, (60, 60, 70))
        sy += 38


# ---------------------------------------------------------------- poster

def build():
    rect(0, 0, S, S, PAPER)
    # masthead
    rect(0, 0, S, 316, NAVY)
    rect(0, 316, S, 324, GOLD)
    draw_text_centered(S // 2, 52, "THE WORLD IN ONE DAY", 5, GOLD)
    draw_text_centered(S // 2, 108, "WEDNESDAY 25 NOVEMBER 2026", 12, WHITE)
    draw_text_centered(S // 2, 236, "SIX STORIES FROM AROUND THE GLOBE", 5, (200, 210, 230))
    # grid: 2 cols x 3 rows
    gx, gy = 48, 348
    pw = (S - 96 - 24) // 2
    ph = 520
    for i, p in enumerate(PANELS):
        col, row = i % 2, i // 2
        draw_panel(p, gx + col * (pw + 24), gy + row * (ph + 24), pw, ph)
    # footer
    fy = gy + 3 * ph + 2 * 24 + 8
    draw_text_centered(S // 2, fy,
                       "EVERY STORY HAPPENED OR WAS FIRST REPORTED ON 25 NOVEMBER 2026", 4, INK)
    draw_text_centered(S // 2, fy + 40,
                       "DRAWN FROM THE DAY'S NEWS WIRES", 4, GREY)


# ---------------------------------------------------------------- png out

def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, small):
    raw = b"".join(b"\x00" + bytes(small[y * OUT * 3:(y + 1) * OUT * 3])
                   for y in range(OUT))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", OUT, OUT, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    build()
    # downscale 2048 -> 1024 by averaging 2x2 blocks
    small = bytearray(OUT * OUT * 3)
    for y in range(OUT):
        for x in range(OUT):
            si = ((2 * y) * S + 2 * x) * 3
            di = (y * OUT + x) * 3
            for c in range(3):
                small[di + c] = (buf[si + c] + buf[si + 3 + c]
                                 + buf[si + S * 3 + c] + buf[si + S * 3 + 3 + c]) // 4
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "entry.png")
    n = write_png(path, small)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
