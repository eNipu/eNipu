#!/usr/bin/env python3
"""Generate terminal.svg, the terminal-style card at the top of the profile README.

Edit the CONTENT section below, then run:

    pip install fonttools
    python3 scripts/make_terminal_svg.py

GitHub shows the SVG as an image, and an image cannot load web fonts. Each device
would then pick its own font, and phones often end up with a thin Courier. So the
text is drawn as outlines of JetBrains Mono from scripts/fonts (SIL Open Font
License, see scripts/fonts/OFL.txt) and looks the same everywhere.
Colors are Catppuccin Mocha.
"""
import sys
from pathlib import Path

try:
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.ttLib import TTFont
except ImportError:
    sys.exit("fontTools is missing: pip install fonttools")

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "terminal.svg"
FONTS = HERE / "fonts"
# Keep HEIGHT / WIDTH small so the whole card fits in one browser window.
WIDTH = 900
BAR = 34
LEFT = 34

# Font weights: normal text, emphasis, name.
N, B, XB = 500, 700, 800

BASE, MANTLE, CHIP, CHIP_BORDER = "#181825", "#11111b", "#232336", "#45475a"
# MUTED and FAINT stay above 6:1 contrast on BASE, so they still read on a phone.
TEXT, MUTED, FAINT = "#cdd6f4", "#a6adc8", "#9399b2"
GREEN, YELLOW, RED = "#a6e3a1", "#f9e2af", "#f38ba8"
CYAN, BLUE, PURPLE, PEACH = "#89dceb", "#89b4fa", "#cba6f7", "#fab387"

# ---------------------------------------------------------------- CONTENT
# A span is (color, weight, text).
NAME = "Md Al-Amin Khandaker"
TITLE = [(CYAN, B, "Applied Cryptographer"), (FAINT, N, "  ·  "), (TEXT, N, "Security Engineer")]
PLACE = [(MUTED, N, "Berlin, DE"), (FAINT, N, "  ·  "), (MUTED, N, "industry since 2019")]
OPEN_TO = [
    (GREEN, B, "open to"),
    (TEXT, N, "   Applied cryptography"),
    (FAINT, N, "  ·  "),
    (TEXT, N, "ZK / protocol security"),
    (FAINT, N, "  ·  "),
    (TEXT, N, "Security engineering"),
]
HIGHLIGHTS = [
    (GREEN, [
        (GREEN, B, "Threat modeling + security code review"),
        (TEXT, N, " for embedded systems"),
        (MUTED, N, "  @ Bosch Group"),
    ]),
    (PURPLE, [
        (PURPLE, B, "Homomorphic encryption + MPC"),
        (TEXT, N, " for SQL on encrypted data"),
        (MUTED, N, "  @ EAGLYS, Tokyo"),
    ]),
    (BLUE, [
        (TEXT, N, "Ph.D. in "),
        (BLUE, B, "pairing-based cryptography"),
        (TEXT, N, ", 27 papers"),
        (FAINT, N, "  ·  "),
        (MUTED, N, "INDOCRYPT, ICISC"),
    ]),
    (YELLOW, [
        (TEXT, N, "Author of "),
        (YELLOW, B, "ELiPS"),
        (TEXT, N, ", a C library for pairings on BN and BLS12 curves"),
    ]),
]
SKILLS = [
    ("crypto", CYAN, ["Pairings / ECC", "Homomorphic Enc", "MPC", "ABE", "Lattice / LWE", "PQC"]),
    ("security", PEACH, ["Threat modeling", "Code review", "ISO/SAE 21434", "EU CRA", "SEI CERT", "Mbed TLS"]),
    ("code", GREEN, ["C", "C++", "Rust", "Python"]),
]
# ------------------------------------------------------------------------


class Font:
    """JetBrains Mono glyphs, each stored once as a <path> and placed with <use>."""

    def __init__(self):
        self.faces = {w: TTFont(FONTS / f"jetbrains-mono-latin-{w}-normal.woff") for w in (N, B, XB)}
        self.glyph_sets = {w: face.getGlyphSet() for w, face in self.faces.items()}
        face = self.faces[N]
        self.upm = face["head"].unitsPerEm
        self.advance = face["hmtx"][face.getBestCmap()[ord("0")]][0]
        self.x_height = face["OS/2"].sxHeight
        self.ids = {}
        self.defs = []

    def width(self, chars, size):
        return chars * self.advance * size / self.upm

    def glyph(self, weight, ch):
        key = (weight, ch)
        if key not in self.ids:
            name = self.faces[weight].getBestCmap().get(ord(ch))
            if name is None:
                sys.exit(f"JetBrains Mono has no glyph for {ch!r}")
            pen = SVGPathPen(self.glyph_sets[weight], ntos=lambda v: str(round(v)))
            self.glyph_sets[weight][name].draw(pen)
            self.ids[key] = f"g{len(self.ids)}"
            self.defs.append(f'<path id="{self.ids[key]}" d="{pen.getCommands()}"/>')
        return self.ids[key]


FONT = Font()


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def text(x, y, size, spans, center=False):
    width = FONT.width(sum(len(s) for _, _, s in spans), size)
    if center:
        x -= width / 2
    elif x + width > WIDTH - LEFT:
        sys.exit(f"line at y={num(y)} is too wide ({num(x + width)}px)")
    k = size / FONT.upm
    out, col = [], 0
    for color, weight, s in spans:
        uses = "".join(
            f'<use href="#{FONT.glyph(weight, ch)}" x="{(col + i) * FONT.advance}"/>'
            for i, ch in enumerate(s)
            if ch != " "
        )
        if uses:
            out.append(f'<g fill="{color}" transform="translate({num(x)} {num(y)}) scale({k:g} {-k:g})">{uses}</g>')
        col += len(s)
    return "".join(out)


def prompt(y, cmd):
    return text(LEFT, y, 14, [(GREEN, B, "$"), (TEXT, N, " " + cmd)])


def marker(x, y, size, color):
    """A small right-pointing triangle, centered on the x-height."""
    cy = y - FONT.x_height * size / FONT.upm / 2
    h, w = 0.42 * size, 0.36 * size
    return f'<path d="M{num(x)} {num(cy - h / 2)}L{num(x + w)} {num(cy)}L{num(x)} {num(cy + h / 2)}Z" fill="{color}"/>'


def main():
    out = []
    y = BAR + 28
    out.append(prompt(y, "whoami"))
    y += 32
    out.append(text(LEFT, y, 24, [(YELLOW, XB, NAME)]))
    y += 26
    out.append(text(LEFT, y, 16, TITLE))
    y += 24
    out.append(text(LEFT, y, 14, PLACE))
    y += 26
    out.append(text(LEFT, y, 15, OPEN_TO))

    y += 38
    out.append(prompt(y, "cat highlights.txt"))
    for color, spans in HIGHLIGHTS:
        y += 26
        out.append(marker(LEFT + 1, y, 15, color))
        out.append(text(LEFT + 22, y, 15, spans))

    y += 38
    out.append(prompt(y, "ls skills/"))
    label_w = FONT.width(max(len(label) for label, _, _ in SKILLS), 14) + 18
    for label, color, items in SKILLS:
        y += 32
        out.append(text(LEFT, y, 14, [(MUTED, N, label)]))
        x = LEFT + label_w
        for item in items:
            w = FONT.width(len(item), 14) + 20
            out.append(
                f'<rect x="{num(x)}" y="{num(y - 18)}" width="{num(w)}" height="26" rx="6" '
                f'fill="{CHIP}" stroke="{CHIP_BORDER}"/>'
            )
            out.append(text(x + 10, y, 14, [(color, N, item)]))
            x += w + 8
        if x > WIDTH - LEFT:
            sys.exit(f"skills row '{label}' is too wide ({num(x)}px)")

    y += 38
    out.append(text(LEFT, y, 14, [(GREEN, B, "$")]))
    out.append(
        f'<rect x="{num(LEFT + FONT.width(2, 14))}" y="{num(y - 13)}" width="9" height="17" rx="1" fill="{TEXT}">'
        '<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect>'
    )
    height = y + 20

    head = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {WIDTH} {height}" '
        'role="img" aria-labelledby="title">',
        f'<title id="title">{NAME}: applied cryptographer and security engineer</title>',
        f'<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="12" fill="{BASE}"/>',
        f'<rect x="0" y="0" width="{WIDTH}" height="{BAR}" rx="12" fill="{MANTLE}"/>',
        f'<rect x="0" y="{BAR // 2}" width="{WIDTH}" height="{BAR - BAR // 2}" fill="{MANTLE}"/>',
        f'<circle cx="22" cy="{BAR / 2}" r="6.5" fill="{RED}"/>',
        f'<circle cx="44" cy="{BAR / 2}" r="6.5" fill="{YELLOW}"/>',
        f'<circle cx="66" cy="{BAR / 2}" r="6.5" fill="{GREEN}"/>',
        text(WIDTH / 2, BAR / 2 + 4.5, 13, [(FAINT, N, "eNipu@github: ~/profile")], center=True),
    ]
    defs = "<defs>" + "".join(FONT.defs) + "</defs>"
    OUT.write_text("\n".join([head[0], defs] + head[1:] + out + ["</svg>"]) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({WIDTH}x{height}, {OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
