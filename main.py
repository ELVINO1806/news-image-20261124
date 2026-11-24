#!/usr/bin/env python3
"""Tuesday 24 November 2026, summed up in one image.

Draws a front-page newspaper (1024x1024 PNG) from the 38 verified
24 November 2026 stories in the news log: 3 lead panels, 5 secondary
mini-panels, a proportional region bar, a numbers strip, an ALSO ON line
and a red NOT 24 NOVEMBER box listing the date traps.

Pure Python standard library, no network, no clock, no randomness:
two runs write byte-identical files. The picture is drawn at 2048x2048
(2x supersampling) and downscaled to 1024x1024. Text uses a built-in
5x7 bitmap font, scaled up; every picture is drawn from simple shapes.
"""
import os
import struct
import zlib
from math import sqrt

SS = 2
W = 1024 * SS
H = 1024 * SS
M = 44
CW = W - 2 * M

PAPER = (247, 242, 231)
WHITE = (255, 255, 255)
INK = (17, 17, 17)
SOFT = (70, 70, 70)
RED = (185, 28, 28)
LIGHTRED = (254, 242, 242)
GREEN = (21, 128, 61)
DARKGREEN = (20, 83, 45)
BLUE = (30, 64, 175)
SKY = (191, 219, 254)
SEA = (30, 58, 138)
AMBER = (180, 83, 9)
PURPLE = (109, 40, 217)
TEAL = (14, 116, 144)
PINK = (190, 24, 93)
GRAY = (55, 65, 81)
LIGHTGRAY = (229, 231, 235)
GOLD = (217, 119, 6)
ORANGE = (234, 88, 12)
NAVY = (15, 23, 42)

# 5x7 bitmap font: each glyph is 7 rows of 5 bits.
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
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
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
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u2013': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '\u00b7': ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    '\u2022': ("00000", "01100", "11110", "11110", "11110", "01100", "00000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '\\': ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    '~': ("00000", "00000", "00101", "01010", "00000", "00000", "00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.buf[off:off + len(row)] = row

    def border(self, x, y, w, h, color, t):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(sqrt(r * r - dy * dy))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def poly(self, pts, color):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa = int(xs[i])
                xb = int(xs[i + 1])
                self.rect(xa, y, xb - xa + 1, 1, color)

    def text_w(self, s, scale, spacing=1):
        adv = (5 + spacing) * scale
        return len(s) * adv - spacing * scale

    def text(self, x, y, s, scale, color, bold=False, spacing=1):
        adv = (5 + spacing) * scale
        boff = max(1, scale // 3) if bold else 0
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g:
                for r in range(7):
                    row = g[r]
                    for c in range(5):
                        if row[c] == '1':
                            self.rect(cx + c * scale, y + r * scale,
                                      scale, scale, color)
                            if boff:
                                self.rect(cx + c * scale + boff,
                                          y + r * scale, scale, scale, color)
            cx += adv
        return cx - x

    def text_center(self, cx, y, s, scale, color, bold=False, spacing=1):
        x = cx - self.text_w(s, scale, spacing) // 2
        self.text(x, y, s, scale, color, bold, spacing)
        return x


def wrap_text(s, max_chars):
    words = s.split(' ')
    lines = []
    cur = ''
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += ' ' + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- data
# All 38 stories, verified 24 November 2026. (headline, one-line fact)
COLUMNS = [
    [("EUROPE", [
        ("BENGHAZI FALLOUT", "Zelensky confirms 7 drones sank the Merkury."),
        ("NATO SPACE", "Rutte vows space defence; nuclear satellite feared."),
        ("EU SANCTIONS", "EU proposes 22nd Russia sanctions package."),
        ("GERMANY-UKRAINE", "Germany gains access to Ukraine's Delta system."),
        ("BELGIUM STRIKE", "Strike halts flights; tear gas in Brussels."),
        ("SPAIN AMNESTY", "Court grants amnesty to Catalan leader Puigdemont."),
        ("DENMARK EVICTIONS", "Top court backs 'ghetto law' evictions."),
        ("ZELENSKY TALKS", "Zelensky urges four-way peace talks soon."),
        ("POLAND AWACS", "NATO sends AWACS plane to Poland after missile falls."),
    ])],
    [("MIDDLE EAST", [
        ("HORMUZ TANKERS", "Iran claims 3 tankers hit mines; claim unconfirmed."),
        ("GAZA STRIKES", "Israeli strikes kill at least six in Gaza Tuesday."),
        ("GAZA MENINGITIS", "Gaza declares meningitis alert; cases 8x the norm."),
        ("QATAR MEDIATION", "Qatar PM seeks to revive US-Iran talks via Rubio."),
        ("IRAQ OIL TAKEOVER", "Baghdad orders takeover of Kurdish oilfields."),
        ("YEMEN STRIKES", "Strikes hit buses in Lahj; about 25 dead or missing."),
    ]),
     ("AFRICA", [
        ("DR CONGO", "Military plane missing in east; rebels claim downing."),
        ("SUDAN STRIKES", "Drone strikes hit homes and a UN building in Khartoum."),
        ("ETHIOPIA PROBE CALL", "Amnesty urges war-crimes probe of Tigray shelling."),
    ])],
    [("ASIA", [
        ("NEPAL QUAKE", "Magnitude 5.6 quake near Nepal-Tibet border."),
        ("KOREA JETS", "Seoul scrambles jets as Russian planes enter zone."),
        ("CHINA MINERALS", "China extends pause on mineral export curbs to US."),
        ("SHENZHOU-24", "Pakistan pilot first foreigner aboard Tiangong."),
        ("BANTEN TOLL RISES", "Banten fire toll rises to 26; about 34 missing."),
        ("INDONESIA TREASON", "Ex-police chief named suspect in treason case."),
        ("INDONESIA VP RACE", "Prabowo nominates two to replace VP Gibran."),
        ("CHINA SPY DEATH", "Chinese official sentenced to death for spying."),
    ]),
     ("OCEANIA", [
        ("AUSTRALIA TECH LAW", "People may sue big tech; fines up to 5% of revenue."),
        ("ENGLAND WIN T20", "England chase 185, win by 8 wickets; series 1-1."),
    ])],
    [("NORTH AMERICA", [
        ("MARKETS RALLY", "Tech rebounds: S&P 500 +4.73%, Nikkei +3.91%."),
        ("GROK LAWSUIT", "Two states sue SpaceX and X over Grok deepfakes."),
        ("FED RATES", "NY Fed chief hints at more rate rises; yields fall."),
        ("IOWA BLAST", "Court lets Army detonate 5 tons of explosives in Iowa."),
    ]),
     ("LATIN AMERICA", [
        ("COLOMBIA BOMB", "Car bomb injures 21 in Villavicencio; power cut."),
        ("MEXICO CARTEL TRIAL", "Mexico will try cartel figure 'Chapo Isidro'."),
        ("HAITI MISSION", "Salvadoran troops push gangs; 3 soldiers named."),
    ]),
     ("GLOBAL", [
        ("ICJ ACTION", "UK sanctions Myanmar generals; backs ICJ ruling."),
        ("HASINA RETURN", "Hasina says she will return from exile on 16 Dec."),
        ("WOMEN'S WORLD CUP", "2031 hosts: US, Mexico, Costa Rica, Jamaica."),
    ])],
]

REGIONS = [
    ("EUROPE", 9, BLUE),
    ("MIDDLE EAST", 6, AMBER),
    ("ASIA", 8, RED),
    ("AFRICA", 3, GREEN),
    ("NORTH AMERICA", 4, PURPLE),
    ("LATIN AMERICA", 3, TEAL),
    ("OCEANIA", 2, PINK),
    ("GLOBAL", 3, GRAY),
]

NUMBERS = [
    ("+4.73%", "S&P 500 TUESDAY", GREEN),
    ("31%", "NVIDIA MONDAY", INK),
    ("5.6", "NEPAL QUAKE", INK),
    ("25", "YEMEN DEAD/MISSING", INK),
    ("21", "COLOMBIA INJURED", INK),
    ("7", "DRONES SANK MERKURY", INK),
]

ALSO_ON = ("Democrats flip 47 House seats \u00b7 California braces for floods "
            "\u00b7 Webb hints at supernova clue \u00b7 Pope diary reveals crisis "
            "\u00b7 Landmines hurt ~7,000 in 2025 \u00b7 India Women win "
            "\u00b7 Senegal rout Cuba 9-0 \u00b7 Commanders edge Bengals 22-20 "
            "\u00b7 Hong Kong fire grants \u00b7 Zambia treason charge "
            "\u00b7 Seychelles tortoises return")

TRAPS = ("Nvidia CEO return (23 Nov) \u00b7 COP31 ends (22 Nov) \u00b7 Merkury sinking "
         "(22 Nov) \u00b7 Poland drone (22 Nov) \u00b7 Penge RSM win (23 Nov) "
         "\u00b7 Brentford 4-0 Everton (23 Nov) \u00b7 ICJ ruling itself (19 Nov) "
         "\u00b7 Banten fire itself (21 Nov)")

SECONDARY = [
    ("SHENZHOU-24",
     "Pakistan pilot Zeeshan Ali, first foreign astronaut on Tiangong.",
     "rocket"),
    ("ENGLAND WIN T20",
     "England chase 185, win by 8 wickets; Donald 85 off 32.",
     "cricket"),
    ("NEPAL QUAKE",
     "Magnitude 5.6 near Nepal-Tibet border; felt in 4 countries.",
     "quake"),
    ("NATO SPACE",
     "Rutte vows space defence; Russia may launch nuclear satellite.",
     "satellite"),
    ("COLOMBIA BOMB",
     "Car bomb injures 21 in Villavicencio; power cut.",
     "blast"),
]


# ---------------------------------------------------------------- scenes
def scene_rocket(cv, x, y, w, h):
    cv.rect(x, y, w, h, NAVY)
    for sx, sy in [(14, 12), (52, 30), (96, 10), (150, 26), (200, 12),
                   (250, 34), (300, 14), (330, 30), (120, 44), (230, 48)]:
        cv.rect(x + sx, y + sy, 4, 4, WHITE)
    cx = x + w // 2
    cv.disc(cx, y + h + 34, 46, (46, 111, 64))
    cv.rect(cx - 13, y + 8, 26, 52, WHITE)
    cv.poly([(cx - 13, y + 8), (cx + 13, y + 8), (cx, y - 6)], RED)
    cv.rect(cx - 24, y + 44, 11, 18, RED)
    cv.rect(cx + 13, y + 44, 11, 18, RED)
    cv.poly([(cx - 10, y + 60), (cx + 10, y + 60), (cx, y + 84)], ORANGE)
    cv.poly([(cx - 5, y + 60), (cx + 5, y + 60), (cx, y + 76)], GOLD)
    cv.disc(cx, y + 30, 5, SKY)


def scene_cricket(cv, x, y, w, h):
    cv.rect(x, y, w, h, (34, 139, 34))
    cv.rect(x + w // 2 - 34, y, 68, h, (222, 184, 135))
    for sx in (x + w // 2 - 8, x + w // 2 + 2, x + w // 2 + 12):
        cv.rect(sx, y + 8, 5, 26, GOLD)
    cv.poly([(x + 60, y + 62), (x + 96, y + 20), (x + 108, y + 30),
             (x + 74, y + 72)], (139, 90, 43))
    cv.rect(x + 52, y + 58, 14, 10, (139, 90, 43))
    cv.disc(x + w - 70, y + 58, 9, RED)
    cv.line(x + w - 70, y + 58, x + w - 110, y + 40, WHITE, 2)
    cv.line(x + w - 110, y + 40, x + w - 150, y + 46, WHITE, 2)


def scene_quake(cv, x, y, w, h):
    cv.rect(x, y, w, h, (219, 234, 254))
    cv.poly([(x, y + h), (x + 90, y + 18), (x + 180, y + h)], (100, 116, 139))
    cv.poly([(x + 150, y + h), (x + 250, y + 8), (x + 340, y + h)],
            (71, 85, 105))
    cv.poly([(x + 232, y + 26), (x + 250, y + 8), (x + 268, y + 26)],
            WHITE)
    cv.poly([(x + 74, y + 34), (x + 90, y + 18), (x + 106, y + 34)], WHITE)
    pts = [(x + 10, y + 66), (x + 60, y + 52), (x + 110, y + 70),
           (x + 170, y + 50), (x + 230, y + 68), (x + 290, y + 52),
           (x + 350, y + 66)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 4)
    cv.rect(x + 40, y + h - 16, 26, 16, (120, 53, 15))
    cv.rect(x + 300, y + h - 14, 22, 14, (120, 53, 15))


def scene_satellite(cv, x, y, w, h):
    cv.rect(x, y, w, h, NAVY)
    for sx, sy in [(16, 14), (60, 34), (110, 12), (170, 30), (230, 14),
                   (290, 36), (330, 16), (90, 52), (260, 54), (200, 58)]:
        cv.rect(x + sx, y + sy, 4, 4, WHITE)
    cx = x + w // 2
    cy = y + h // 2
    cv.rect(cx - 60, cy - 8, 120, 16, BLUE)
    cv.rect(cx - 16, cy - 14, 32, 28, (148, 163, 184))
    cv.rect(cx - 12, cy - 10, 8, 8, GOLD)
    cv.line(cx + 16, cy - 14, cx + 44, cy - 34, WHITE, 2)
    cv.disc(cx + 46, cy - 36, 4, RED)
    cv.line(cx - 30, cy + 22, cx - 60, cy + 40, WHITE, 2)
    cv.line(cx - 34, cy + 26, cx - 66, cy + 40, WHITE, 2)


def scene_blast(cv, x, y, w, h):
    cv.rect(x, y, w, h, (254, 226, 190))
    cv.rect(x + 20, y + 34, 70, h - 34, GRAY)
    cv.rect(x + 110, y + 22, 80, h - 22, (31, 41, 55))
    cv.rect(x + 250, y + 40, 64, h - 40, GRAY)
    for wx in (34, 58, 126, 150, 262, 286):
        for wy in (44, 62):
            cv.rect(x + wx, y + wy, 10, 8, GOLD)
    cx = x + 150
    cy = y + 26
    burst = []
    for i in range(12):
        ang = i * 30
        import math as _m
        r1 = 34 if i % 2 == 0 else 16
        burst.append((int(cx + r1 * _m.cos(_m.radians(ang))),
                      int(cy + r1 * _m.sin(_m.radians(ang)) * 0.7)))
    cv.poly(burst, GOLD)
    cv.poly([(cx - 16, cy - 8), (cx + 16, cy - 8), (cx, cy + 10)], ORANGE)
    cv.disc(cx - 40, cy - 6, 10, (107, 114, 128))
    cv.disc(cx + 44, cy - 10, 12, (107, 114, 128))


SCENES = {
    "rocket": scene_rocket,
    "cricket": scene_cricket,
    "quake": scene_quake,
    "satellite": scene_satellite,
    "blast": scene_blast,
}


# ---------------------------------------------------------------- layout
def draw_masthead(cv):
    cv.text_center(W // 2, 34, "THE WORLD IN ONE PAGE", 3, SOFT, bold=True)
    cv.text_center(W // 2, 60, "TUESDAY 24 NOVEMBER 2026", 13, INK, bold=True)
    cv.rect(M, 158, CW, 5, RED)
    cv.text_center(W // 2, 170, "38 STORIES \u00b7 8 REGIONS \u00b7 ONE DAY, THE WHOLE WORLD",
                   2, SOFT)


def draw_numbers(cv):
    y = 192
    bw = (CW - 5 * 10) // 6
    for i, (num, label, color) in enumerate(NUMBERS):
        x = M + i * (bw + 10)
        cv.rect(x, y, bw, 62, WHITE)
        cv.border(x, y, bw, 62, INK, 2)
        cv.text_center(x + bw // 2, y + 6, num, 5, color, bold=True)
        cv.text_center(x + bw // 2, y + 44, label, 2, SOFT)


def draw_region_bar(cv):
    y = 264
    total = sum(n for _, n, _ in REGIONS)
    x = M
    for i, (name, n, color) in enumerate(REGIONS):
        w = CW * n // total
        if i == len(REGIONS) - 1:
            w = M + CW - x
        cv.rect(x, y, w, 40, color)
        cv.text_center(x + w // 2, y + 13, "%s %d" % (name, n), 2, WHITE,
                       bold=True, spacing=0)
        x += w


def draw_lead_markets(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK, 3)
    cx, cy, chh = x + 28, y + 24, 186
    base = cy + chh
    bars = [50, 85, 110, 140, 175]
    tops = []
    for i, bh in enumerate(bars):
        bx = cx + i * 108
        cv.rect(bx, base - bh, 64, bh, GREEN if i < 4 else DARKGREEN)
        tops.append((bx + 32, base - bh))
    for a, b in zip(tops, tops[1:]):
        cv.line(a[0], a[1], b[0], b[1], DARKGREEN, 4)
    cv.line(tops[-1][0], tops[-1][1], tops[-1][0] + 26, tops[-1][1] - 18,
            DARKGREEN, 4)
    cv.poly([(tops[-1][0] + 26, tops[-1][1] - 18),
             (tops[-1][0] + 8, tops[-1][1] - 16),
             (tops[-1][0] + 24, tops[-1][1] - 2)], DARKGREEN)
    cv.line(cx, base, cx + 600, base, INK, 3)
    rx = x + 660
    cv.text(rx, y + 30, "+4.73%", 8, GREEN, bold=True)
    cv.text(rx, y + 100, "S&P 500", 3, INK, bold=True)
    cv.text(rx, y + 126, "NIKKEI +3.91%", 3, INK)
    cv.text(rx, y + 152, "SEOUL +6%", 3, INK)
    cv.rect(rx, y + 182, 240, 24, LIGHTGRAY)
    cv.border(rx, y + 182, 240, 24, INK, 2)
    cv.text(rx + 10, y + 187, "NVIDIA +31% MONDAY", 2, INK, bold=True)
    cv.text(x + 28, y + 222, "MARKETS RALLY", 6, INK, bold=True)
    fact = ("Tech shares rebound: S&P 500 +4.73%, Nikkei +3.91%, Seoul +6%. "
            "Nvidia +31% Monday drove the rally; Nasdaq fell 10% last week.")
    lines = wrap_text(fact, (w - 56) // 18)
    fy = y + 272
    for ln in lines:
        cv.text(x + 28, fy, ln, 3, SOFT)
        fy += 24


def draw_lead_hormuz(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK, 3)
    sx, sy = x + 12, y + 16
    cv.rect(sx, sy, w - 24, 85, SKY)
    cv.rect(sx, sy + 85, w - 24, 75, SEA)
    for dx in range(0, w - 24, 24):
        cv.rect(sx + dx, sy + 92, 12, 3, WHITE)
    for hx, hw, hh in [(sx + 20, 130, 20), (sx + 170, 110, 18),
                        (sx + 300, 90, 16)]:
        cv.rect(hx, sy + 100 - hh, hw, hh, (17, 24, 39))
        cv.rect(hx + hw - 34, sy + 100 - hh - 16, 24, 16, WHITE)
        cv.rect(hx + 12, sy + 100 - hh - 12, 10, 12, RED)
    for mx, my in [(sx + 90, sy + 138), (sx + 320, sy + 144)]:
        cv.disc(mx, my, 9, INK)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            cv.line(mx, my, mx + dx * 15, my + dy * 15, INK, 2)
    cv.text(x + 20, y + 190, "HORMUZ TANKERS", 4, INK, bold=True)
    fact = ("Iran claims 3 tankers hit mines under US escort; maritime "
            "centre says unconfirmed. Brent $86.71.")
    lines = wrap_text(fact, (w - 40) // 18)
    fy = y + 228
    for ln in lines:
        cv.text(x + 20, fy, ln, 3, SOFT)
        fy += 24


def draw_lead_benghazi(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK, 3)
    sx, sy = x + 16, y + 16
    cv.rect(sx, sy, w - 32, 70, (148, 163, 184))
    cv.rect(sx, sy + 70, w - 32, 90, (30, 58, 95))
    for bx, bw, bh in [(sx + 10, 60, 34), (sx + 90, 44, 46), (sx + 150, 70, 28)]:
        cv.rect(bx, sy + 70 - bh, bw, bh, GRAY)
    cv.poly([(sx + 60, sy + 118), (sx + 330, sy + 102), (sx + 360, sy + 122),
             (sx + 350, sy + 138), (sx + 80, sy + 150)], (17, 24, 39))
    cv.line(sx + 190, sy + 108, sx + 190, sy + 66, INK, 4)
    cv.poly([(sx + 150, sy + 112), (sx + 180, sy + 112), (sx + 165, sy + 78)],
            ORANGE)
    cv.poly([(sx + 200, sy + 110), (sx + 225, sy + 110), (sx + 212, sy + 84)],
            GOLD)
    cv.poly([(sx + 235, sy + 112), (sx + 255, sy + 112), (sx + 245, sy + 92)],
            ORANGE)
    for dx, dy, r in [(170, 62, 12), (205, 52, 15), (240, 60, 11)]:
        cv.disc(sx + dx, sy + dy, r, (107, 114, 128))
    for i in range(7):
        dx = sx + 40 + i * 48
        cv.disc(dx, sy + 22, 4, INK)
        cv.line(dx - 10, sy + 30, dx + 10, sy + 30, INK, 2)
    cv.text(x + 20, y + 190, "BENGHAZI FALLOUT", 4, INK, bold=True)
    fact = ("Zelensky confirms 7 naval drones sank the Merkury; a cargo "
            "ship was also hit; UN demands a probe.")
    lines = wrap_text(fact, (w - 40) // 18)
    fy = y + 228
    for ln in lines:
        cv.text(x + 20, fy, ln, 3, SOFT)
        fy += 24


def draw_secondary(cv, x, y, w, h):
    pw = (CW - 4 * 10) // 5
    for i, (title, fact, kind) in enumerate(SECONDARY):
        px = x + i * (pw + 10)
        cv.rect(px, y, pw, h, WHITE)
        cv.border(px, y, pw, h, INK, 2)
        SCENES[kind](cv, px + 12, y + 12, pw - 24, 88)
        cv.text(px + 12, y + 108, title, 3, INK, bold=True)
        lines = wrap_text(fact, (pw - 24) // 12)
        fy = y + 132
        for ln in lines[:3]:
            cv.text(px + 12, fy, ln, 2, SOFT)
            fy += 16


def draw_stories(cv):
    y0 = 948
    cv.text_center(W // 2, 904, "ALL 38 STORIES \u2014 TUESDAY 24 NOVEMBER 2026",
                   4, INK, bold=True)
    cv.rect(M, 938, CW, 3, RED)
    col_w = (CW - 3 * 16) // 4
    for ci, groups in enumerate(COLUMNS):
        cx = M + ci * (col_w + 16)
        cy = y0
        for region, stories in groups:
            cv.text(cx, cy, "%s \u2014 %d" % (region, len(stories)), 3, RED,
                    bold=True)
            cv.rect(cx, cy + 22, col_w, 3, RED)
            cy += 28
            for headline, fact in stories:
                cv.text(cx, cy, headline, 4, INK, bold=True)
                lines = wrap_text(fact, col_w // 18)
                fy = cy + 31
                for ln in lines:
                    cv.text(cx, fy, ln, 3, SOFT)
                    fy += 22
                cy = fy + 6


def draw_also(cv):
    cv.text(M, 1858, "ALSO ON \u2014 MORE FROM TUESDAY 24 NOVEMBER 2026", 3,
            INK, bold=True)
    lines = wrap_text(ALSO_ON, CW // 12)
    fy = 1884
    for ln in lines:
        cv.text(M, fy, ln, 2, SOFT)
        fy += 16


def draw_redbox(cv):
    y = 1922
    cv.rect(M, y, CW, 88, LIGHTRED)
    cv.border(M, y, CW, 88, RED, 4)
    cv.text(M + 16, y + 10, "NOT 24 NOVEMBER \u2014 THESE ARE NOT TODAY'S NEWS",
            3, RED, bold=True)
    lines = wrap_text(TRAPS, (CW - 32) // 12)
    fy = y + 38
    for ln in lines:
        cv.text(M + 16, fy, ln, 2, INK)
        fy += 16


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_numbers(cv)
    draw_region_bar(cv)
    draw_lead_markets(cv, M, 314, 1010, 380)
    draw_lead_hormuz(cv, M + 1020, 314, 440, 380)
    draw_lead_benghazi(cv, M + 1470, 314, 490, 380)
    draw_secondary(cv, M, 704, 0, 190)
    draw_stories(cv)
    draw_also(cv)
    draw_redbox(cv)
    return cv.buf


def downscale(src, w, h):
    ow, oh = w // 2, h // 2
    out = bytearray(ow * oh * 3)
    sw3 = w * 3
    for oy in range(oh):
        row0 = oy * 2 * sw3
        row1 = row0 + sw3
        orow = oy * ow * 3
        for ox in range(ow):
            sx = ox * 6
            o = orow + ox * 3
            out[o] = (src[row0 + sx] + src[row0 + sx + 3] +
                      src[row1 + sx] + src[row1 + sx + 3] + 2) // 4
            out[o + 1] = (src[row0 + sx + 1] + src[row0 + sx + 4] +
                          src[row1 + sx + 1] + src[row1 + sx + 4] + 2) // 4
            out[o + 2] = (src[row0 + sx + 2] + src[row0 + sx + 5] +
                          src[row1 + sx + 2] + src[row1 + sx + 5] + 2) // 4
    return out


def png_bytes(w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += rgb[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    big = build()
    small = downscale(big, W, H)
    data = png_bytes(1024, 1024, small)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
