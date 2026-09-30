#!/usr/bin/env python3
"""Generate terminal.svg, the terminal-style card at the top of the profile README.

Edit the CONTENT section below, then run:

    python3 scripts/make_terminal_svg.py

Only the Python standard library is needed. Colors are Catppuccin Mocha.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "terminal.svg"
FONT = "'JetBrains Mono','Fira Code','DejaVu Sans Mono','Courier New',monospace"
WIDTH = 860
LEFT = 34
# Width of one monospace character at 13px, with some slack for fallback fonts.
CHAR_13 = 8.4

BASE, MANTLE, CRUST = "#181825", "#11111b", "#232336"
SURFACE = "#313244"
TEXT, DIM = "#cdd6f4", "#6c7086"
GREEN, YELLOW, RED = "#a6e3a1", "#f9e2af", "#f38ba8"
CYAN, BLUE, PURPLE, PEACH = "#89dceb", "#89b4fa", "#cba6f7", "#fab387"

# ---------------------------------------------------------------- CONTENT
NAME = "Md Al-Amin Khandaker"
TITLE = [(CYAN, True, "Applied Cryptographer"), (TEXT, False, "   ·   Security Engineer")]
ORG = [
    (PEACH, False, "ITK Engineering (Bosch Group)"),
    (DIM, False, "   ·   Berlin, DE   ·   industry since 2019"),
]
HIGHLIGHTS = [
    (GREEN, [
        (GREEN, True, "Threat modeling + security code review"),
        (TEXT, False, " for embedded systems"),
        (DIM, False, "  @ Bosch Group"),
    ]),
    (PURPLE, [
        (PURPLE, True, "Homomorphic encryption + MPC"),
        (TEXT, False, " for SQL on encrypted data"),
        (DIM, False, "  @ EAGLYS, Tokyo"),
    ]),
    (BLUE, [
        (TEXT, False, "Ph.D. in "),
        (BLUE, True, "pairing-based cryptography"),
        (TEXT, False, ", 27 papers"),
        (DIM, False, "  ·  INDOCRYPT, ICISC"),
    ]),
    (YELLOW, [
        (TEXT, False, "Author of "),
        (YELLOW, True, "ELiPS"),
        (TEXT, False, ", a C library for pairings on BN and BLS12 curves"),
    ]),
]
SKILLS = [
    ("crypto", CYAN, ["Pairings / ECC", "Homomorphic Enc", "MPC", "ABE", "Lattice / LWE", "PQC"]),
    ("security", PEACH, ["Threat modeling", "Code review", "ISO/SAE 21434", "EU CRA", "SEI CERT", "Mbed TLS"]),
    ("code", GREEN, ["C", "C++", "Rust", "Python"]),
]
OPEN_TO = [
    (TEXT, False, "Applied cryptography"),
    (DIM, False, "  ·  "),
    (TEXT, False, "ZK / protocol security"),
    (DIM, False, "  ·  "),
    (TEXT, False, "Security engineering"),
]
# ------------------------------------------------------------------------


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def text(x, y, size, spans, anchor=None):
    parts = []
    for color, bold, s in spans:
        if not s:
            continue
        weight = "bold" if bold else "normal"
        parts.append(f'<tspan fill="{color}" font-weight="{weight}">{escape(s)}</tspan>')
    extra = f' text-anchor="{anchor}"' if anchor else ""
    width = sum(len(s) for _, _, s in spans) * size * 0.61
    if not anchor and x + width > WIDTH - LEFT:
        raise SystemExit(f"line at y={num(y)} is too wide ({num(x + width)}px)")
    return f'<text x="{num(x)}" y="{num(y)}" font-size="{size}" xml:space="preserve"{extra}>{"".join(parts)}</text>'


def prompt(y, cmd):
    return [text(LEFT, y, 14, [(GREEN, True, "$")]), text(LEFT + 18, y, 14, [(TEXT, False, cmd)])]


def main():
    out = []
    y = 92
    out += prompt(y, "whoami")
    y += 40
    out.append(text(LEFT, y, 26, [(YELLOW, True, NAME)]))
    y += 28
    out.append(text(LEFT, y, 15, TITLE))
    y += 24
    out.append(text(LEFT, y, 14, ORG))

    y += 52
    out += prompt(y, "cat highlights.txt")
    y += 5
    for marker, spans in HIGHLIGHTS:
        y += 27
        out.append(text(LEFT, y, 14, [(marker, True, "▸")]))
        out.append(text(LEFT + 20, y, 14, spans))

    y += 55
    out += prompt(y, "ls skills/")
    y += 6
    label_w = max(len(label) for label, _, _ in SKILLS) * CHAR_13 + 16
    for label, color, items in SKILLS:
        y += 34
        out.append(text(LEFT, y, 13, [(DIM, False, label)]))
        x = LEFT + label_w
        for item in items:
            w = len(item) * CHAR_13 + 20
            out.append(
                f'<rect x="{num(x)}" y="{num(y - 16)}" width="{num(w)}" height="24" rx="6" '
                f'fill="{CRUST}" stroke="{SURFACE}"/>'
            )
            out.append(text(x + 10, y, 13, [(color, False, item)]))
            x += w + 8
        if x > WIDTH - LEFT:
            raise SystemExit(f"skills row '{label}' is too wide ({num(x)}px)")

    y += 56
    out += prompt(y, "cat open_to.txt")
    y += 30
    out.append(text(LEFT, y, 14, OPEN_TO))

    y += 46
    out.append(text(LEFT, y, 14, [(GREEN, True, "$")]))
    out.append(
        f'<rect x="{LEFT + 18}" y="{num(y - 13)}" width="9" height="17" rx="1" fill="{TEXT}">'
        '<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect>'
    )
    height = y + 28

    head = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {WIDTH} {height}" '
        f'font-family="{FONT}" role="img" aria-labelledby="title">',
        f'<title id="title">{escape(NAME)}: applied cryptographer and security engineer</title>',
        f'<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="12" fill="{BASE}"/>',
        f'<rect x="0" y="0" width="{WIDTH}" height="40" rx="12" fill="{MANTLE}"/>',
        f'<rect x="0" y="20" width="{WIDTH}" height="20" fill="{MANTLE}"/>',
        f'<circle cx="22" cy="20" r="6.5" fill="{RED}"/>',
        f'<circle cx="44" cy="20" r="6.5" fill="{YELLOW}"/>',
        f'<circle cx="66" cy="20" r="6.5" fill="{GREEN}"/>',
        text(WIDTH / 2, 25, 13, [(DIM, False, "eNipu@github: ~/profile")], anchor="middle"),
    ]
    OUT.write_text("\n".join(head + out + ["</svg>"]) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({WIDTH}x{height})")


if __name__ == "__main__":
    main()
