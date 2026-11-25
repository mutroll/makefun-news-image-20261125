#!/usr/bin/env python3
"""News poster for Wednesday 25 November 2026.

Draws a 1024x1024 PNG newspaper front page with six stories from
25 November 2026, rendered supersampled at 2048x2048 and downscaled.
Python 3.13 standard library only, no network, fully deterministic.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- canvas
SUPER = 2048          # supersampled working size
FINAL = 1024          # output size
W = H = SUPER

PAPER = (246, 241, 231)
INK = (20, 20, 22)
NAVY = (20, 36, 62)
GOLD = (198, 158, 74)
CREAM = (246, 241, 231)
WHITE = (255, 255, 255)
GREY = (110, 108, 100)
PANEL_LINE = (190, 184, 170)

# 5x7 bitmap font, drawn from scratch for this poster.
# Each glyph is 7 rows of 5 cells; '#' is on, '.' is off.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

_canvas = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        _canvas[i] = color[0]
        _canvas[i + 1] = color[1]
        _canvas[i + 2] = color[2]


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            _canvas[i] = color[0]
            _canvas[i + 1] = color[1]
            _canvas[i + 2] = color[2]


def fill_circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def draw_line(x0, y0, x1, y1, color, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = thick // 2
    while True:
        fill_rect(x0 - half, y0 - half, thick, thick, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_triangle(p0, p1, p2, color):
    xs = sorted([p0, p1, p2], key=lambda p: p[1])
    (x0, y0), (x1, y1), (x2, y2) = xs
    if y2 == y0:
        return
    for y in range(y0, y2 + 1):
        if y < y1:
            if y1 == y0:
                xa, xb = x0, x0
            else:
                xa = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
                xb = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
        else:
            if y2 == y1:
                xa, xb = x1, x2
            else:
                xa = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                xb = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
        if xa > xb:
            xa, xb = xb, xa
        fill_rect(int(xa), y, int(xb) - int(xa) + 1, 1, color)


def fill_poly(points, color):
    # Simple scanline fill for a convex-ish polygon.
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        if len(xs) >= 2:
            xs.sort()
            fill_rect(int(xs[0]), y, int(xs[-1]) - int(xs[0]) + 1, 1, color)


# ------------------------------------------------------------------- text
def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, color):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch)
        if glyph is None:
            cx += 6 * scale
            continue
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    fill_rect(cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx


def wrap_text(text, scale, max_width):
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(x, y, text, scale, color, max_width, line_h):
    for i, line in enumerate(wrap_text(text, scale, max_width)):
        draw_text(x, y + i * line_h, line, scale, color)
    return y + len(wrap_text(text, scale, max_width)) * line_h


# ------------------------------------------------------------------ icons
def icon_rocket(cx, cy, s, color, flame):
    # body
    fill_rect(cx - 14 * s // 10, cy - 46 * s // 10, 28 * s // 10, 62 * s // 10, color)
    fill_triangle((cx - 14 * s // 10, cy - 46 * s // 10),
                  (cx + 14 * s // 10, cy - 46 * s // 10),
                  (cx, cy - 72 * s // 10), color)
    # window
    fill_circle(cx, cy - 24 * s // 10, 7 * s // 10, CREAM)
    # fins
    fill_triangle((cx - 14 * s // 10, cy + 16 * s // 10),
                  (cx - 30 * s // 10, cy + 34 * s // 10),
                  (cx - 14 * s // 10, cy + 34 * s // 10), color)
    fill_triangle((cx + 14 * s // 10, cy + 16 * s // 10),
                  (cx + 30 * s // 10, cy + 34 * s // 10),
                  (cx + 14 * s // 10, cy + 34 * s // 10), color)
    # flame
    fill_triangle((cx - 10 * s // 10, cy + 16 * s // 10),
                  (cx + 10 * s // 10, cy + 16 * s // 10),
                  (cx, cy + 52 * s // 10), flame)
    # stars
    for sx, sy, r in ((-52, -52, 4), (48, -38, 3), (-44, 8, 3), (52, 30, 4)):
        fill_circle(cx + sx * s // 10, cy + sy * s // 10, r * s // 10, color)


def icon_chart(cx, cy, s, color, accent):
    # axes
    draw_line(cx - 62 * s // 10, cy + 44 * s // 10,
              cx + 62 * s // 10, cy + 44 * s // 10, color, 5 * s // 10)
    draw_line(cx - 62 * s // 10, cy + 44 * s // 10,
              cx - 62 * s // 10, cy - 52 * s // 10, color, 5 * s // 10)
    # falling line
    pts = [(-56, -38), (-28, -18), (-6, -30), (18, 2), (44, 22), (58, 40)]
    for i in range(len(pts) - 1):
        draw_line(cx + pts[i][0] * s // 10, cy + pts[i][1] * s // 10,
                  cx + pts[i + 1][0] * s // 10, cy + pts[i + 1][1] * s // 10,
                  accent, 6 * s // 10)
    for px, py in pts:
        fill_circle(cx + px * s // 10, cy + py * s // 10, 4 * s // 10, accent)
    # arrow head at the end
    fill_triangle((cx + 58 * s // 10, cy + 40 * s // 10),
                  (cx + 38 * s // 10, cy + 40 * s // 10),
                  (cx + 52 * s // 10, cy + 58 * s // 10), accent)


def icon_quake(cx, cy, s, color, accent):
    # seismograph zigzag
    pts = [(-64, 0), (-44, 0), (-36, -26), (-28, 26), (-18, -44),
           (-8, 44), (2, -30), (10, 18), (20, 0), (64, 0)]
    for i in range(len(pts) - 1):
        draw_line(cx + pts[i][0] * s // 10, cy + pts[i][1] * s // 10,
                  cx + pts[i + 1][0] * s // 10, cy + pts[i + 1][1] * s // 10,
                  color, 5 * s // 10)
    # ground cracks
    draw_line(cx - 56 * s // 10, cy + 52 * s // 10,
              cx - 20 * s // 10, cy + 52 * s // 10, accent, 4 * s // 10)
    draw_line(cx - 20 * s // 10, cy + 52 * s // 10,
              cx - 8 * s // 10, cy + 66 * s // 10, accent, 4 * s // 10)
    draw_line(cx + 8 * s // 10, cy + 52 * s // 10,
              cx + 56 * s // 10, cy + 52 * s // 10, accent, 4 * s // 10)
    draw_line(cx + 24 * s // 10, cy + 52 * s // 10,
              cx + 34 * s // 10, cy + 64 * s // 10, accent, 4 * s // 10)


def icon_scales(cx, cy, s, color, accent):
    # pole and beam
    draw_line(cx, cy - 52 * s // 10, cx, cy + 52 * s // 10, color, 6 * s // 10)
    draw_line(cx - 56 * s // 10, cy - 40 * s // 10,
              cx + 56 * s // 10, cy - 40 * s // 10, color, 6 * s // 10)
    fill_circle(cx, cy - 52 * s // 10, 6 * s // 10, accent)
    # pans
    for side in (-1, 1):
        px = cx + side * 48 * s // 10
        draw_line(px, cy - 40 * s // 10, px, cy - 6 * s // 10, color, 4 * s // 10)
        fill_triangle((px - 22 * s // 10, cy - 6 * s // 10),
                      (px + 22 * s // 10, cy - 6 * s // 10),
                      (px, cy + 26 * s // 10), accent)
    # base
    fill_rect(cx - 26 * s // 10, cy + 52 * s // 10, 52 * s // 10, 8 * s // 10, color)


def icon_people(cx, cy, s, color, accent):
    for dx, head_r, body_w, body_h, col in (
            (-46, 13, 34, 34, color), (0, 16, 40, 40, accent), (46, 13, 34, 34, color)):
        fill_circle(cx + dx * s // 10, cy - 26 * s // 10, head_r * s // 10, col)
        fill_rect(cx + dx * s // 10 - body_w * s // 20,
                  cy - 6 * s // 10, body_w * s // 10, body_h * s // 10, col)


def icon_heart(cx, cy, s, color, accent):
    # heart: two circles + triangle
    fill_circle(cx - 16 * s // 10, cy - 14 * s // 10, 20 * s // 10, color)
    fill_circle(cx + 16 * s // 10, cy - 14 * s // 10, 20 * s // 10, color)
    fill_triangle((cx - 36 * s // 10, cy - 8 * s // 10),
                  (cx + 36 * s // 10, cy - 8 * s // 10),
                  (cx, cy + 44 * s // 10), color)
    # pulse line across
    pts = [(-58, 6), (-30, 6), (-18, -14), (-6, 22), (8, -6), (18, 6), (58, 6)]
    for i in range(len(pts) - 1):
        draw_line(cx + pts[i][0] * s // 10, cy + pts[i][1] * s // 10,
                  cx + pts[i + 1][0] * s // 10, cy + pts[i + 1][1] * s // 10,
                  CREAM, 5 * s // 10)


ICONS = {
    'rocket': icon_rocket,
    'chart': icon_chart,
    'quake': icon_quake,
    'scales': icon_scales,
    'people': icon_people,
    'heart': icon_heart,
}

# ---------------------------------------------------------------- stories
# Six stories that happened or were first reported on Wed 25 Nov 2026.
PANELS = [
    {
        'kicker': 'SPACE - CHINA',
        'color': (27, 58, 107),
        'headline': 'CHINA LAUNCHES SHENZHOU-24',
        'sub': 'First Pakistani in orbit; first foreign guest aboard Tiangong station.',
        'icon': 'rocket',
    },
    {
        'kicker': 'MARKETS - JAPAN',
        'color': (140, 47, 47),
        'headline': 'NIKKEI PLUNGES 2.8% IN TOKYO',
        'sub': 'AI sell-off resumes; chipmaker Advantest falls 12%.',
        'icon': 'chart',
    },
    {
        'kicker': 'DISASTER - PHILIPPINES',
        'color': (150, 84, 16),
        'headline': 'M5.1 QUAKE SHAKES PANAY',
        'sub': 'Intensity V in Valderrama; damage and aftershocks expected.',
        'icon': 'quake',
    },
    {
        'kicker': 'POLITICS - AUSTRALIA',
        'color': (47, 93, 58),
        'headline': 'WATCHDOG SLAMS PRISON CULTURE',
        'sub': "NSW ICAC: fix 'misogynistic' culture at Corrective Services.",
        'icon': 'scales',
    },
    {
        'kicker': 'SOCIETY - INDIA',
        'color': (124, 58, 107),
        'headline': 'INDIA LAUNCHES NAYI CHETNA 5.0',
        'sub': 'Gender campaign opens on the UN day against violence on women.',
        'icon': 'people',
    },
    {
        'kicker': 'HEALTH - ENGLAND',
        'color': (14, 107, 107),
        'headline': "ENGLAND'S FRAILTY GAP WIDEST",
        'sub': '31-country study: rich-poor health gap widest in England.',
        'icon': 'heart',
    },
]


def draw_panel(x, y, w, h, panel):
    fill_rect(x, y, w, h, WHITE)
    fill_rect(x, y, w, h, PANEL_LINE)  # border via outline
    fill_rect(x + 3, y + 3, w - 6, h - 6, WHITE)
    # kicker band
    fill_rect(x + 3, y + 3, w - 6, 60, panel['color'])
    draw_text(x + 30, y + 15, panel['kicker'], 4, CREAM)
    # headline (scale 6) and sub-line (scale 5): larger text so both
    # stay legible when the poster is shrunk to ~300 px across.
    inner = w - 60
    draw_text_block(x + 30, y + 82, panel['headline'], 6, INK, inner, 58)
    # sub-line
    draw_text_block(x + 30, y + 82 + 2 * 58 + 14, panel['sub'], 5,
                    (64, 62, 56), inner, 44)
    # pictogram, centred in the lower part of the panel
    icon_cx = x + w // 2
    icon_cy = y + h - 100
    ICONS[panel['icon']](icon_cx, icon_cy, 8, panel['color'], GOLD)


def draw_poster():
    fill_rect(0, 0, W, H, PAPER)
    # masthead
    fill_rect(0, 0, W, 300, NAVY)
    fill_rect(0, 300, W, 8, GOLD)
    small = 'THE WORLD IN ONE DAY'
    draw_text((W - text_width(small, 5)) // 2, 52, small, 5, GOLD)
    big = 'WEDNESDAY 25 NOVEMBER 2026'
    draw_text((W - text_width(big, 11)) // 2, 118, big, 11, CREAM)
    sub = 'SIX STORIES FROM AROUND THE GLOBE'
    draw_text((W - text_width(sub, 4)) // 2, 226, sub, 4, (190, 196, 210))
    # panels: 2 columns x 3 rows
    mx, my = 48, 336
    gap = 28
    pw = (W - 2 * mx - gap) // 2
    ph = (1960 - my - 2 * gap) // 3
    for i, panel in enumerate(PANELS):
        col = i % 2
        row = i // 2
        draw_panel(mx + col * (pw + gap), my + row * (ph + gap),
                   pw, ph, panel)
    # footer
    foot = ('ALL SIX STORIES HAPPENED OR WERE FIRST REPORTED ON '
            'WEDNESDAY 25 NOVEMBER 2026')
    draw_text((W - text_width(foot, 3)) // 2, 1988, foot, 3, GREY)
    src = 'SOURCES: REUTERS - DOW JONES - PHIVOLCS - NSW ICAC - PIB - THE GUARDIAN'
    draw_text((W - text_width(src, 3)) // 2, 2018, src, 3, GREY)


# ------------------------------------------------------------------- png
def downscale():
    out = bytearray(FINAL * FINAL * 3)
    for oy in range(FINAL):
        for ox in range(FINAL):
            r = g = b = 0
            for dy in range(2):
                for dx in range(2):
                    i = (((oy * 2 + dy) * W) + (ox * 2 + dx)) * 3
                    r += _canvas[i]
                    g += _canvas[i + 1]
                    b += _canvas[i + 2]
            j = (oy * FINAL + ox) * 3
            out[j] = (r + 2) // 4
            out[j + 1] = (g + 2) // 4
            out[j + 2] = (b + 2) // 4
    return bytes(out)


def write_png(path, pixels, size):
    def chunk(kind, data):
        c = struct.pack('>I', len(data)) + kind + data
        return c + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = size * 3
    for y in range(size):
        raw.append(0)
        raw += pixels[y * stride:(y + 1) * stride]
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)


def main():
    draw_poster()
    pixels = downscale()
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'entry.png')
    n = write_png(path, pixels, FINAL)
    print('wrote %s (%d bytes)' % (path, n))


if __name__ == '__main__':
    main()
