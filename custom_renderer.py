"""
Custom SVG Chart Renderer for Kerykeion.
Generates beautiful, themeable astrology wheel charts from scratch.
"""

import math
import random
from dataclasses import dataclass
from typing import Optional

from zodiac_paths import ZODIAC_PATHS

# ── Constants ──────────────────────────────────────────────────

ZODIAC_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
ZODIAC_SHORT = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍",
                  "♎", "♏", "♐", "♑", "♒", "♓"]

PLANET_SYMBOLS = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀",
    "mars": "♂", "jupiter": "♃", "saturn": "♄", "uranus": "♅",
    "neptune": "♆", "pluto": "♇", "mean_node": "☊",
    "true_node": "☊", "chiron": "⚷", "lilith": "⚸",
    "ascendant": "Asc", "medium_coeli": "MC",
    "first_house": "I", "tenth_house": "X",
}

PLANET_ORDER = [
    "sun", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "uranus", "neptune", "pluto",
    "mean_node", "chiron", "lilith",
]

SIGN_TO_ELEMENT = {
    "Ari": "Fire", "Leo": "Fire", "Sag": "Fire",
    "Tau": "Earth", "Vir": "Earth", "Cap": "Earth",
    "Gem": "Air", "Lib": "Air", "Aqu": "Air",
    "Can": "Water", "Sco": "Water", "Pis": "Water",
}

# Pastel zodiac colors for cosmic theme (subtle, elegant)
ZODIAC_COLORS_COSMIC = [
    "#2a1520", "#2a1a15", "#1a202a", "#15202a",
    "#1a2a1a", "#202a15", "#1a1520", "#201520",
    "#15202a", "#201a15", "#151a20", "#201520",
]
ZODIAC_COLORS_SAKURA = [
    "#fff0f5", "#ffe4ec", "#fff0f8", "#fce7f0",
    "#fff5f8", "#fdf2f6", "#fff0f5", "#ffe8f0",
    "#fdf0f5", "#fcecf2", "#fff2f7", "#fceaf2",
]
ZODIAC_COLORS_GOLD = [
    "#140f08", "#1a1208", "#0f1408", "#081408",
    "#08140f", "#0a1014", "#100a14", "#140a10",
    "#0f0814", "#140f08", "#081014", "#140810",
]

@dataclass
class Theme:
    name: str
    bg: str
    bg_gradient: Optional[str]
    text: str
    text_dim: str
    line: str
    line_dim: str
    accent: str
    accent_secondary: str
    zodiac_colors: list[str]
    zodiac_stroke: str
    house_line: str
    house_line_width: float
    planet_color: str
    planet_size: int
    retro_color: str
    table_bg: Optional[str]
    star_field: bool
    vignette: bool
    glow: bool
    font_family: str


THEMES = {
    "cosmic": Theme(
        name="Cosmic Night",
        bg="#080c24",
        bg_gradient="radial-gradient(circle at 50% 40%, #0d1538 0%, #080c24 70%)",
        text="#e8ecf8",
        text_dim="#a0aec8",
        line="#c8d4e8",
        line_dim="#5a6e96",
        accent="#f0c840",
        accent_secondary="#60a5fa",
        zodiac_colors=ZODIAC_COLORS_COSMIC,
        zodiac_stroke="#3a4e7a",
        house_line="#b8cce8",
        house_line_width=1.4,
        planet_color="#e8ecf8",
        planet_size=18,
        retro_color="#fb7185",
        table_bg="#0a1030",
        star_field=True,
        vignette=True,
        glow=True,
        font_family="'Noto Sans', 'PingFang TC', 'Microsoft JhengHei', sans-serif",
    ),
    "dark": Theme(
        name="Dark Moon",
        bg="#111827",
        bg_gradient=None,
        text="#f3f4f6",
        text_dim="#9ca3af",
        line="#d1d5db",
        line_dim="#6b7280",
        accent="#60a5fa",
        accent_secondary="#a78bfa",
        zodiac_colors=["#1a2230"] * 12,
        zodiac_stroke="#4b5563",
        house_line="#9ca3af",
        house_line_width=1.0,
        planet_color="#f3f4f6",
        planet_size=16,
        retro_color="#f87171",
        table_bg="#1f2937",
        star_field=False,
        vignette=False,
        glow=False,
        font_family="'Noto Sans', 'PingFang TC', sans-serif",
    ),
    "light": Theme(
        name="Day Light",
        bg="#ffffff",
        bg_gradient=None,
        text="#1f2937",
        text_dim="#4b5563",
        line="#1f2937",
        line_dim="#9ca3af",
        accent="#2563eb",
        accent_secondary="#7c3aed",
        zodiac_colors=["#f9fafb", "#f3f4f6"] * 6,
        zodiac_stroke="#d1d5db",
        house_line="#4b5563",
        house_line_width=1.0,
        planet_color="#1f2937",
        planet_size=16,
        retro_color="#dc2626",
        table_bg="#f9fafb",
        star_field=False,
        vignette=False,
        glow=False,
        font_family="'Noto Sans', 'PingFang TC', sans-serif",
    ),
    "sakura": Theme(
        name="Sakura Dream",
        bg="#fdf2f4",
        bg_gradient=None,
        text="#5a3542",
        text_dim="#8a5868",
        line="#8a4a60",
        line_dim="#d8a8b8",
        accent="#e879a8",
        accent_secondary="#c084fc",
        zodiac_colors=ZODIAC_COLORS_SAKURA,
        zodiac_stroke="#e0b8c8",
        house_line="#a06078",
        house_line_width=1.0,
        planet_color="#5a3542",
        planet_size=16,
        retro_color="#e879a8",
        table_bg="#fce7f0",
        star_field=False,
        vignette=False,
        glow=False,
        font_family="'Noto Sans', 'PingFang TC', sans-serif",
    ),
    "gold": Theme(
        name="Imperial Gold",
        bg="#0a0a0a",
        bg_gradient="radial-gradient(circle at 50% 40%, #141208 0%, #0a0a0a 70%)",
        text="#f0e4c8",
        text_dim="#b0a070",
        line="#e0c860",
        line_dim="#6a5a30",
        accent="#f0d040",
        accent_secondary="#d8b850",
        zodiac_colors=ZODIAC_COLORS_GOLD,
        zodiac_stroke="#3a3020",
        house_line="#c8b878",
        house_line_width=1.4,
        planet_color="#f0e4c8",
        planet_size=18,
        retro_color="#e07060",
        table_bg="#141208",
        star_field=True,
        vignette=True,
        glow=True,
        font_family="'Noto Serif', 'Georgia', serif",
    ),
}


class CustomChartSVG:
    """Renders a beautiful astrology wheel chart from Kerykeion subject data."""

    def __init__(
        self,
        subject,
        theme: str = "cosmic",
        width: int = 900,
        height: int = 700,
        title: Optional[str] = None,
    ):
        self.subject = subject
        self.theme = THEMES.get(theme, THEMES["cosmic"])
        self.W = width
        self.H = height
        # Chart wheel center & radii
        self.CX = 340
        self.CY = height // 2
        self.R_OUTER = 310
        self.R_ZODIAC_INNER = 250
        self.R_HOUSE_OUTER = 240
        self.R_HOUSE_INNER = 140
        self.R_PLANET = 165
        self.R_PLANET_LABEL = 120

        self.title = title or getattr(subject, "name", "Chart")

        # Extract data
        self.houses = self._extract_houses()
        self.planets = self._extract_planets()
        self.asc = self.houses[0]["abs_pos"] if self.houses else 0

    # ── Data extraction ──────────────────────────────────────────

    def _extract_houses(self) -> list[dict]:
        houses = []
        house_names = [
            "first", "second", "third", "fourth", "fifth", "sixth",
            "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
        ]
        for i, name in enumerate(house_names, 1):
            h = getattr(self.subject, f"{name}_house", None)
            if h is None:
                continue
            houses.append({
                "num": i,
                "name": h.name,
                "abs_pos": float(h.abs_pos),
                "sign": h.sign,
                "sign_num": h.sign_num,
            })
        return houses

    def _extract_planets(self) -> list[dict]:
        planets = []
        for name in PLANET_ORDER:
            p = getattr(self.subject, name, None)
            if p is None or getattr(p, "abs_pos", None) is None:
                continue
            planets.append({
                "key": name,
                "name": p.name,
                "abs_pos": float(p.abs_pos),
                "sign": p.sign,
                "sign_num": p.sign_num,
                "position": float(p.position),
                "retrograde": bool(p.retrograde) if p.retrograde is not None else False,
                "house": getattr(p, "house", None),
                "emoji": getattr(p, "emoji", ""),
            })
        return planets

    # ── Geometry helpers ─────────────────────────────────────────

    def _polar(self, angle_deg: float, radius: float) -> tuple[float, float]:
        """Convert astrology angle (0=Aries at right, CCW) to SVG coords."""
        rad = math.radians(-angle_deg)
        x = self.CX + radius * math.cos(rad)
        y = self.CY + radius * math.sin(rad)
        return x, y

    def _arc_path(self, r: float, start_deg: float, end_deg: float, large_arc: bool = False) -> str:
        """SVG arc path from start to end angle."""
        x1, y1 = self._polar(start_deg, r)
        x2, y2 = self._polar(end_deg, r)
        sweep = 1 if large_arc else 0
        large = 1 if (end_deg - start_deg) % 360 > 180 else 0
        return f"A {r:.1f} {r:.1f} 0 {large} {sweep} {x2:.2f} {y2:.2f}"

    def _sector_path(self, r_out: float, r_in: float, start_deg: float, end_deg: float) -> str:
        """Closed path for a circular sector (annulus slice)."""
        x1o, y1o = self._polar(start_deg, r_out)
        x2o, y2o = self._polar(end_deg, r_out)
        x2i, y2i = self._polar(end_deg, r_in)
        x1i, y1i = self._polar(start_deg, r_in)
        sweep = 1
        large = 1 if (end_deg - start_deg) % 360 > 180 else 0
        return (
            f"M {x1o:.2f} {y1o:.2f} "
            f"A {r_out:.1f} {r_out:.1f} 0 {large} {sweep} {x2o:.2f} {y2o:.2f} "
            f"L {x2i:.2f} {y2i:.2f} "
            f"A {r_in:.1f} {r_in:.1f} 0 {large} {1 - sweep} {x1i:.2f} {y1i:.2f} Z"
        )

    def _place_planets(self) -> list[dict]:
        """Compute planet display positions, handling overlap by fanning out."""
        placed = []
        for p in self.planets:
            placed.append({
                **p,
                "display_angle": p["abs_pos"],
                "display_radius": self.R_PLANET,
            })

        # Sort by angle for overlap detection
        placed.sort(key=lambda x: x["display_angle"])

        # Simple overlap resolution: if two planets are within 6°, offset them
        MIN_SEP = 7.0  # degrees
        for _ in range(3):  # iterate a few times
            for i in range(len(placed)):
                for j in range(i + 1, len(placed)):
                    a1 = placed[i]["display_angle"]
                    a2 = placed[j]["display_angle"]
                    diff = min((a1 - a2) % 360, (a2 - a1) % 360)
                    if diff < MIN_SEP:
                        # Push them apart
                        shift = (MIN_SEP - diff) / 2 + 0.5
                        placed[i]["display_angle"] = (a1 + shift) % 360
                        placed[j]["display_angle"] = (a2 - shift) % 360
                        # Also vary radius slightly
                        placed[i]["display_radius"] += 8
                        placed[j]["display_radius"] -= 5

        return placed

    # ── SVG builders ─────────────────────────────────────────────

    def _svg_header(self) -> str:
        th = self.theme
        defs = []
        defs.append('<defs>')
        # Glow filter for planets
        if th.glow:
            defs.append('''
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            ''')
        # Vignette
        if th.vignette:
            defs.append('''
            <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
                <stop offset="60%" stop-color="black" stop-opacity="0"/>
                <stop offset="100%" stop-color="black" stop-opacity="0.5"/>
            </radialGradient>
            ''')
        defs.append('</defs>')
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" '
            f'viewBox="0 0 {self.W} {self.H}" style="font-family: {th.font_family}; background: {th.bg}; font-variant-emoji: text;">\n'
            + "\n".join(defs)
        )

    def _background(self) -> str:
        th = self.theme
        parts = []
        # Base rect
        parts.append(f'<rect width="{self.W}" height="{self.H}" fill="{th.bg}"/>')
        # Star field
        if th.star_field:
            random.seed(42)
            stars = []
            for _ in range(100):
                x = random.randint(0, self.W)
                y = random.randint(0, self.H)
                r = random.choice([0.4, 0.7, 1.0, 1.3])
                op = random.choice([0.2, 0.35, 0.5, 0.7])
                stars.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" opacity="{op}"/>')
            parts.extend(stars)
        # Vignette overlay
        if th.vignette:
            parts.append(f'<rect width="{self.W}" height="{self.H}" fill="url(#vignette)" style="mix-blend-mode: multiply;" pointer-events="none"/>')
        return "\n".join(parts)

    def _zodiac_wheel(self) -> str:
        """Draw the outer zodiac ring: 12 colored sectors + symbols + degree numbers."""
        th = self.theme
        parts = []

        # 12 zodiac sectors (each 30°)
        for i, (sign, color) in enumerate(zip(ZODIAC_SHORT, th.zodiac_colors)):
            start = i * 30
            end = (i + 1) * 30
            path_d = self._sector_path(self.R_OUTER, self.R_ZODIAC_INNER, start, end)
            parts.append(
                f'<path d="{path_d}" fill="{color}" stroke="{th.zodiac_stroke}" stroke-width="0.5"/>'
            )

        # Zodiac symbols placed at middle of each sector
        icon_size = 22
        scale = icon_size / 24
        for i, sign in enumerate(ZODIAC_NAMES):
            mid = i * 30 + 15
            x, y = self._polar(mid, (self.R_OUTER + self.R_ZODIAC_INNER) / 2)
            tx = x - icon_size / 2
            ty = y - icon_size / 2
            paths = ZODIAC_PATHS.get(sign, [])
            if paths:
                path_strs = "".join(f'<path d="{d}"/>' for d in paths)
                parts.append(
                    f'<g transform="translate({tx:.1f},{ty:.1f}) scale({scale:.3f})" '
                    f'fill="{th.text_dim}" opacity="0.85">{path_strs}</g>'
                )
            else:
                sym = ZODIAC_SYMBOLS[i]
                parts.append(
                    f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" '
                    f'fill="{th.text_dim}" font-size="16" opacity="0.7">{sym}</text>'
                )

        # Degree numbers every 10° on outer rim
        for deg in range(0, 360, 10):
            x, y = self._polar(deg, self.R_OUTER + 14)
            parts.append(
                f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" '
                f'fill="{th.text_dim}" font-size="7" opacity="0.6">{deg}°</text>'
            )

        # Outer and inner ring strokes
        parts.append(
            f'<circle cx="{self.CX}" cy="{self.CY}" r="{self.R_OUTER}" '
            f'fill="none" stroke="{th.line}" stroke-width="1.2" opacity="0.7"/>'
        )
        parts.append(
            f'<circle cx="{self.CX}" cy="{self.CY}" r="{self.R_ZODIAC_INNER}" '
            f'fill="none" stroke="{th.line_dim}" stroke-width="0.8" opacity="0.5"/>'
        )

        # Degree ticks every 1°
        for deg in range(0, 360):
            if deg % 30 == 0:
                tick_len = 12
                sw = 1.5
                op = 0.9
                stroke = th.line
            elif deg % 10 == 0:
                tick_len = 7
                sw = 0.9
                op = 0.6
                stroke = th.line_dim
            elif deg % 5 == 0:
                tick_len = 4
                sw = 0.5
                op = 0.4
                stroke = th.line_dim
            else:
                tick_len = 2
                sw = 0.3
                op = 0.22
                stroke = th.line_dim
            x1, y1 = self._polar(deg, self.R_OUTER)
            x2, y2 = self._polar(deg, self.R_OUTER - tick_len)
            parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>'
            )

        return "\n".join(parts)

    def _house_lines(self) -> str:
        """Draw house cusp lines from center all the way to outer rim."""
        th = self.theme
        parts = []
        for h in self.houses:
            angle = h["abs_pos"]
            x1, y1 = self._polar(angle, 4)
            x2, y2 = self._polar(angle, self.R_OUTER)
            is_major = h["num"] in (1, 4, 7, 10)
            stroke = "#ffffff" if is_major else th.house_line
            sw = th.house_line_width * (3.0 if is_major else 2.0)
            parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{stroke}" stroke-width="{sw}" opacity="1"/>'
            )

        # Zodiac ring radial dividers (every 30°)
        for deg in range(0, 360, 30):
            x1, y1 = self._polar(deg, self.R_ZODIAC_INNER)
            x2, y2 = self._polar(deg, self.R_OUTER)
            parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{th.line_dim}" stroke-width="0.8" opacity="0.6"/>'
            )

        # Concentric rings
        for r, sw in [(self.R_OUTER, 1.5), (self.R_ZODIAC_INNER, 1.0),
                      (self.R_HOUSE_OUTER, 1.0), (self.R_HOUSE_INNER, 1.0)]:
            parts.append(
                f'<circle cx="{self.CX}" cy="{self.CY}" r="{r}" '
                f'fill="none" stroke="{th.line_dim}" stroke-width="{sw}" opacity="0.7"/>'
            )

        # House numbers inside house ring
        for i in range(len(self.houses)):
            h = self.houses[i]
            next_h = self.houses[(i + 1) % 12]
            mid = (h["abs_pos"] + (next_h["abs_pos"] - h["abs_pos"]) % 360 / 2) % 360
            x, y = self._polar(mid, (self.R_HOUSE_OUTER + self.R_HOUSE_INNER) / 2)
            parts.append(
                f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" '
                f'fill="{th.text_dim}" font-size="9" opacity="0.6">{h["num"]}</text>'
            )

        return "\n".join(parts)

    def _planets(self) -> str:
        """Draw planet glyphs with degree markers."""
        th = self.theme
        parts = []
        placed = self._place_planets()
        filter_attr = ' filter="url(#glow)"' if th.glow else ""

        for p in placed:
            angle = p["display_angle"]
            r = p["display_radius"]
            x, y = self._polar(angle, r)

            # Degree tick line from planet toward center (more visible)
            x_in, y_in = self._polar(angle, self.R_HOUSE_INNER + 8)
            parts.append(
                f'<line x1="{x_in:.1f}" y1="{y_in:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
                f'stroke="{th.line_dim}" stroke-width="0.6" opacity="0.5"/>'
            )

            # Planet glyph
            sym = PLANET_SYMBOLS.get(p["key"], p["name"][:2])
            parts.append(
                f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" '
                f'fill="{th.planet_color}" font-size="{th.planet_size}"{filter_attr}>{sym}</text>'
            )

            # Retrograde mark
            if p["retrograde"]:
                rx, ry = self._polar(angle, r + 14)
                parts.append(
                    f'<text x="{rx:.1f}" y="{ry:.1f}" text-anchor="middle" dominant-baseline="central" '
                    f'fill="{th.retro_color}" font-size="8">℞</text>'
                )

            # Degree text
            dx, dy = self._polar(angle, r - 22)
            deg = int(p["position"])
            parts.append(
                f'<text x="{dx:.1f}" y="{dy:.1f}" text-anchor="middle" dominant-baseline="central" '
                f'fill="{th.text_dim}" font-size="8" opacity="0.6">{deg}°</text>'
            )

        return "\n".join(parts)

    def _center_info(self) -> str:
        """Birth data in the center circle."""
        th = self.theme
        parts = []
        # Center small circle background
        parts.append(
            f'<circle cx="{self.CX}" cy="{self.CY}" r="{self.R_HOUSE_INNER - 5}" '
            f'fill="{th.bg}" opacity="0.85"/>'
        )

        # Name
        parts.append(
            f'<text x="{self.CX}" y="{self.CY - 20}" text-anchor="middle" '
            f'fill="{th.text}" font-size="14" font-weight="600">{self.title}</text>'
        )

        # Birth date
        yr = getattr(self.subject, "year", None)
        mo = getattr(self.subject, "month", None)
        da = getattr(self.subject, "day", None)
        hr = getattr(self.subject, "hour", None)
        mn = getattr(self.subject, "minute", None)
        if yr and mo and da:
            date_str = f"{yr}-{mo:02d}-{da:02d} {hr:02d}:{mn:02d}"
        else:
            date_str = ""
        parts.append(
            f'<text x="{self.CX}" y="{self.CY}" text-anchor="middle" '
            f'fill="{th.text_dim}" font-size="11">{date_str}</text>'
        )

        # Location
        loc = f"{getattr(self.subject, 'lat', '?'):.2f}°N, {getattr(self.subject, 'lng', '?'):.2f}°E"
        parts.append(
            f'<text x="{self.CX}" y="{self.CY + 16}" text-anchor="middle" '
            f'fill="{th.text_dim}" font-size="10">{loc}</text>'
        )

        # ASC / MC info
        asc_sign = self.houses[0]["sign"] if self.houses else "?"
        mc_sign = next((h["sign"] for h in self.houses if h["num"] == 10), "?")
        parts.append(
            f'<text x="{self.CX}" y="{self.CY + 34}" text-anchor="middle" '
            f'fill="{th.accent}" font-size="10">ASC {asc_sign}  MC {mc_sign}</text>'
        )

        return "\n".join(parts)

    def _planet_table(self) -> str:
        """Right-hand side planet data table."""
        th = self.theme
        parts = []
        tx = 640
        ty = 60
        row_h = 24
        col_w = [30, 80, 50, 50, 40]  # symbol, name, sign, deg, house

        # Title
        parts.append(
            f'<text x="{tx}" y="{ty - 10}" fill="{th.text}" font-size="14" font-weight="600">Planets</text>'
        )

        # Headers
        headers = ["", "Planet", "Sign", "Deg", "H"]
        for i, (h, w) in enumerate(zip(headers, col_w)):
            x = tx + sum(col_w[:i]) + w / 2
            parts.append(
                f'<text x="{x:.0f}" y="{ty + 10}" text-anchor="middle" '
                f'fill="{th.text_dim}" font-size="9" font-weight="600">{h}</text>'
            )

        # Separator line
        parts.append(
            f'<line x1="{tx}" y1="{ty + 16}" x2="{tx + sum(col_w)}" y2="{ty + 16}" '
            f'stroke="{th.line_dim}" stroke-width="0.5"/>'
        )

        for idx, p in enumerate(self.planets):
            y = ty + 30 + idx * row_h
            sym = PLANET_SYMBOLS.get(p["key"], "?")
            name = p["name"]
            sign = p["sign"]
            deg = f"{int(p['position'])}°{int((p['position'] % 1) * 60):02d}'"
            house = p["house"].replace("_House", "").replace("First", "1").replace("Second", "2") \
                .replace("Third", "3").replace("Fourth", "4").replace("Fifth", "5") \
                .replace("Sixth", "6").replace("Seventh", "7").replace("Eighth", "8") \
                .replace("Ninth", "9").replace("Tenth", "10").replace("Eleventh", "11") \
                .replace("Twelfth", "12") if p["house"] else ""
            retro = " ℞" if p["retrograde"] else ""

            # Alternating row bg
            if idx % 2 == 0 and th.table_bg:
                parts.append(
                    f'<rect x="{tx}" y="{y - 10}" width="{sum(col_w)}" height="{row_h}" '
                    f'fill="{th.table_bg}" opacity="0.3" rx="2"/>'
                )

            # Symbol
            parts.append(
                f'<text x="{tx + col_w[0] / 2}" y="{y}" text-anchor="middle" dominant-baseline="central" '
                f'fill="{th.accent}" font-size="14">{sym}</text>'
            )
            # Name
            name_color = th.retro_color if p["retrograde"] else th.text
            parts.append(
                f'<text x="{tx + col_w[0] + 4}" y="{y}" dominant-baseline="central" '
                f'fill="{name_color}" font-size="11">{name}{retro}</text>'
            )
            # Sign
            parts.append(
                f'<text x="{tx + col_w[0] + col_w[1] + col_w[2] / 2}" y="{y}" text-anchor="middle" dominant-baseline="central" '
                f'fill="{th.text_dim}" font-size="10">{sign}</text>'
            )
            # Deg
            parts.append(
                f'<text x="{tx + col_w[0] + col_w[1] + col_w[2] + col_w[3] / 2}" y="{y}" text-anchor="middle" dominant-baseline="central" '
                f'fill="{th.text_dim}" font-size="10">{deg}</text>'
            )
            # House
            parts.append(
                f'<text x="{tx + sum(col_w[:4]) + col_w[4] / 2}" y="{y}" text-anchor="middle" dominant-baseline="central" '
                f'fill="{th.text_dim}" font-size="10">{house}</text>'
            )

        return "\n".join(parts)

    def _aspects(self) -> str:
        """Draw aspect lines inside the chart wheel (prominent like astro.com)."""
        th = self.theme
        if not self.planets or len(self.planets) < 2:
            return ""

        ASPECT_ANGLES = {
            "conjunct": (0, 6.0),
            "semi-sextile": (30, 2.0),
            "semi-square": (45, 2.0),
            "sextile": (60, 5.0),
            "quintile": (72, 2.0),
            "square": (90, 5.0),
            "trine": (120, 5.0),
            "sesqui-quadrate": (135, 2.0),
            "quincunx": (150, 2.5),
            "opposite": (180, 5.0),
        }
        # Colors: blue = harmonious, red = tense, green = minor, gold = major
        ASPECT_STYLES = {
            "conjunct": ("#ffd700", 1.5, 0.9, None),
            "semi-sextile": ("#c0c8d8", 0.7, 0.6, "2,2"),
            "semi-square": ("#ff9999", 0.8, 0.7, "2,2"),
            "sextile": ("#80e0ff", 1.2, 0.9, "3,3"),
            "quintile": ("#c0c8d8", 0.7, 0.6, "2,2"),
            "square": ("#ff5555", 1.4, 0.9, None),
            "trine": ("#80e0ff", 1.2, 0.9, "4,2"),
            "sesqui-quadrate": ("#ff9999", 0.8, 0.7, "4,2"),
            "quincunx": ("#c0c8d8", 0.8, 0.7, "3,3"),
            "opposite": ("#ff5555", 1.4, 0.9, "6,3"),
        }

        parts = []
        drawn = set()
        for i, p1 in enumerate(self.planets):
            for j, p2 in enumerate(self.planets):
                if i >= j:
                    continue
                diff = abs(p1["abs_pos"] - p2["abs_pos"])
                diff = min(diff, 360 - diff)

                for aspect_name, (target, orb) in ASPECT_ANGLES.items():
                    if abs(diff - target) <= orb:
                        key = tuple(sorted([p1["key"], p2["key"]]))
                        if key in drawn:
                            continue
                        drawn.add(key)

                        # Draw line inside the house ring
                        x1, y1 = self._polar(p1["abs_pos"], self.R_HOUSE_INNER + 12)
                        x2, y2 = self._polar(p2["abs_pos"], self.R_HOUSE_INNER + 12)
                        color, sw, op, dash = ASPECT_STYLES[aspect_name]
                        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
                        parts.append(
                            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                            f'stroke="{color}" stroke-width="{sw}" opacity="{op}"{dash_attr}/>'
                        )
                        break
        return "\n".join(parts)

    # ── Public render ────────────────────────────────────────────

    def render(self) -> str:
        parts = [
            self._svg_header(),
            self._background(),
            self._zodiac_wheel(),
            self._house_lines(),
            self._aspects(),
            self._planets(),
            self._center_info(),
            self._planet_table(),
            "</svg>",
        ]
        return "\n".join(parts)


def render_chart(subject, theme: str = "cosmic", title: Optional[str] = None) -> str:
    """Convenience function: render a chart from a Kerykeion subject."""
    renderer = CustomChartSVG(subject, theme=theme, title=title)
    return renderer.render()
