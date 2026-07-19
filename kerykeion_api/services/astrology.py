"""Astrology calculation services using Kerykeion."""

import math
import os
import re
import tempfile
from typing import Any

from kerykeion import AstrologicalSubject, KerykeionChartSVG

from kerykeion_api.models.schemas import Subject


_THEME_PRESETS: dict[str, dict[str, Any]] = {
    "cosmic": {
        "name": "Cosmic Night",
        "paper": "#080c24",
        "paper_0": "#c8d0e0",
        "base_100": "#080c24",
        "base_200": "#0a1030",
        "base_300": "#131842",
        "neutral_content": "#a8b5d0",
        "primary": "#60a5fa",
        "secondary": "#a78bfa",
        "accent": "#f472b6",
        "info": "#38bdf8",
        "success": "#34d399",
        "warning": "#fbbf24",
        "error": "#fb7185",
        "modern_planet_ring": "#131842",
        "modern_planet_ring_outer": "#0d1230",
        "modern_house_ring": "#1e2a5a",
        "modern_stroke": "#3a4e7a",
        "modern_retrograde": "#fb7185",
        "modern_indicator": "#4e6090",
        "line_color": "#4a6fa5",
        "house_number_color": "#7a9cc6",
        "zodiac_bg": ["#0a0e2a", "#121a42"] * 6,
        "glow": True,
    },
    "sakura": {
        "name": "Sakura Dream",
        "paper": "#fdf2f4",
        "paper_0": "#5a3542",
        "base_100": "#fdf2f4",
        "base_200": "#fce7f0",
        "base_300": "#f8d7e8",
        "neutral_content": "#5a3542",
        "primary": "#e879a8",
        "secondary": "#c084fc",
        "accent": "#f472b6",
        "info": "#67e8f9",
        "success": "#6ee7b7",
        "warning": "#fcd34d",
        "error": "#fb7185",
        "modern_planet_ring": "#fce7f0",
        "modern_planet_ring_outer": "#f8d7e8",
        "modern_house_ring": "#f5d0e0",
        "modern_stroke": "#e8b4c0",
        "modern_retrograde": "#e879a8",
        "modern_indicator": "#d4a5b5",
        "line_color": "#c48a9e",
        "house_number_color": "#a06078",
        "zodiac_bg": ["#fdf2f4", "#fce7f0"] * 6,
        "glow": False,
    },
    "gold": {
        "name": "Imperial Gold",
        "paper": "#0a0a0a",
        "paper_0": "#d4af37",
        "base_100": "#0a0a0a",
        "base_200": "#141208",
        "base_300": "#1c1508",
        "neutral_content": "#c9b896",
        "primary": "#d4af37",
        "secondary": "#c9a84c",
        "accent": "#e8c866",
        "info": "#87ceeb",
        "success": "#98d8a0",
        "warning": "#f0c040",
        "error": "#e07060",
        "modern_planet_ring": "#1c1508",
        "modern_planet_ring_outer": "#141208",
        "modern_house_ring": "#2a200c",
        "modern_stroke": "#5a4a28",
        "modern_retrograde": "#e07060",
        "modern_indicator": "#7a6838",
        "line_color": "#8a7a4a",
        "house_number_color": "#b8a878",
        "zodiac_bg": ["#0f0c06", "#1a1408"] * 6,
        "glow": True,
    },
}


def to_kerykeion_subject(s: Subject) -> AstrologicalSubject:
    """Convert Pydantic Subject to Kerykeion AstrologicalSubject."""
    return AstrologicalSubject(
        name=s.name,
        year=s.year,
        month=s.month,
        day=s.day,
        hour=s.hour,
        minute=s.minute,
        lng=s.longitude,
        lat=s.latitude,
        tz_str=s.timezone,
    )


def serialize_subject(subj: AstrologicalSubject) -> dict[str, Any]:
    """Serialize a Kerykeion AstrologicalSubject to dict."""
    return {
        "name": subj.name,
        "birth_data": {
            "date": f"{subj.year}-{subj.month:02d}-{subj.day:02d}",
            "time": f"{subj.hour:02d}:{subj.minute:02d}",
            "longitude": subj.lng,
            "latitude": subj.lat,
            "timezone": subj.tz_str,
        },
        "sun": subj.sun,
        "moon": subj.moon,
        "mercury": subj.mercury,
        "venus": subj.venus,
        "mars": subj.mars,
        "jupiter": subj.jupiter,
        "saturn": subj.saturn,
        "uranus": subj.uranus,
        "neptune": subj.neptune,
        "pluto": subj.pluto,
        "mean_node": getattr(subj, "mean_node", None),
        "true_node": getattr(subj, "true_node", None),
        "chiron": getattr(subj, "chiron", None),
        "lilith": getattr(subj, "lilith", None),
        "ascendant": subj.first_house,
        "midheaven": subj.tenth_house,
        "houses": {
            f"house_{i}": getattr(subj, f"{i}_house", None)
            for i in range(1, 13)
        },
    }


def _beautify_svg(svg: str, theme: str) -> str:
    """Post-process Kerykeion SVG with custom color themes & effects."""
    preset = _THEME_PRESETS.get(theme)
    if preset is None:
        return svg

    overrides = f""":root {{
    --kerykeion-color-neutral-content: {preset['neutral_content']};
    --kerykeion-color-base-content: {preset['neutral_content']};
    --kerykeion-color-primary: {preset['primary']};
    --kerykeion-color-secondary: {preset['secondary']};
    --kerykeion-color-accent: {preset['accent']};
    --kerykeion-color-neutral: {preset['base_300']};
    --kerykeion-color-base-100: {preset['base_100']};
    --kerykeion-color-base-200: {preset['base_200']};
    --kerykeion-color-base-300: {preset['base_300']};
    --kerykeion-modern-planet-ring: {preset['modern_planet_ring']};
    --kerykeion-modern-planet-ring-outer: {preset['modern_planet_ring_outer']};
    --kerykeion-modern-house-ring: {preset['modern_house_ring']};
    --kerykeion-modern-stroke: {preset['modern_stroke']};
    --kerykeion-modern-retrograde: {preset['modern_retrograde']};
    --kerykeion-modern-indicator: {preset['modern_indicator']};
    --kerykeion-color-info: {preset['info']};
    --kerykeion-color-success: {preset['success']};
    --kerykeion-color-warning: {preset['warning']};
    --kerykeion-color-error: {preset['error']};
    --kerykeion-chart-color-paper-0: {preset['paper_0']};
    --kerykeion-chart-color-paper-1: {preset['paper']};
    --kerykeion-chart-color-houses-radix-line: {preset['line_color']};
    --kerykeion-chart-color-houses-transit-line: {preset['line_color']};
    --kerykeion-chart-color-house-number: {preset['house_number_color']};
"""
    for i, color in enumerate(preset["zodiac_bg"]):
        overrides += f"    --kerykeion-chart-color-zodiac-bg-{i}: {color};\n"
        overrides += f"    --kerykeion-modern-zodiac-bg-{i}: {color};\n"
    overrides += "}\n"

    style_match = re.search(r"(<style\s+kr:node='Theme_Colors_Tag'>.*?</style>)", svg, re.DOTALL)
    if style_match:
        original_style = style_match.group(1)
        new_style = original_style.replace("</style>", f"\n{overrides}</style>")
        svg = svg.replace(original_style, new_style, 1)
    else:
        svg = svg.replace("</title>", f"</title>\n<style>{overrides}</style>", 1)

    effects_css = f"""
    line[style*="houses-radix-line"] {{ stroke-opacity: 0.75 !important; stroke-dasharray: none !important; stroke-width: 1.2px !important; }}
    line[style*="houses-transit-line"] {{ stroke-opacity: 0.6 !important; stroke-dasharray: none !important; stroke-width: 1px !important; }}
    g[kr:node="Aspects"] line {{ stroke-opacity: 0.45 !important; }}
    g[kr:node="Aspects"] path {{ stroke-opacity: 0.45 !important; }}
    text {{ font-family: 'Noto Sans', 'PingFang TC', sans-serif; }}
    g[kr:node*="Planet"] text, g[kr:node*="Cusp"] text {{ filter: drop-shadow(0 0 2px {preset['paper']}); }}
    g[kr:node="HouseNumber"] text {{ fill-opacity: 0.9 !important; font-weight: 500; }}
    circle[kr:node="Zodiac_Wheel"] {{ stroke-opacity: 0.6; }}
    """

    if preset.get("glow"):
        effects_css += f"""
    g[kr:node*="Planet"] text, g[kr:node*="Cusp"] text {{ filter: drop-shadow(0 0 3px rgba(255,255,255,0.25)); }}
    """

    bg_rect = f'<rect width="100%" height="100%" fill="{preset["paper"]}" />\n'

    star_field = ""
    if preset.get("glow"):
        import random
        random.seed(42)
        stars = []
        for _ in range(80):
            x, y = random.randint(0, 890), random.randint(0, 580)
            r = random.choice([0.5, 0.8, 1.2])
            op = random.choice([0.3, 0.5, 0.7])
            stars.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" opacity="{op}"/>')
        star_field = "\n".join(stars) + "\n"

    svg = re.sub(
        r"(<svg[^>]*>)",
        rf"\1\n<defs><style>{effects_css}</style></defs>\n{bg_rect}{star_field}",
        svg,
        count=1,
    )

    return svg


def make_svg(
    subject: AstrologicalSubject,
    chart_type: str = "Natal",
    second_obj: AstrologicalSubject | None = None,
    theme: str = "dark",
    renderer: str = "kerykeion",
) -> str:
    """Render SVG chart using Kerykeion or custom renderer."""
    if renderer == "custom":
        from custom_renderer import render_chart as custom_render_chart
        return custom_render_chart(subject, theme=theme, title=getattr(subject, "name", None))

    kerykeion_theme = theme if theme in ("dark", "light", "classic") else "dark"
    chart = KerykeionChartSVG(
        subject,
        chart_type=chart_type,
        second_obj=second_obj,
        theme=kerykeion_theme,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        chart.output_directory = tmpdir
        chart.makeSVG()
        svg_files = [f for f in os.listdir(tmpdir) if f.endswith(".svg")]
        if not svg_files:
            raise RuntimeError("SVG generation failed: no .svg file found")
        with open(os.path.join(tmpdir, svg_files[0]), "r", encoding="utf-8") as f:
            svg = f.read()

    if theme in _THEME_PRESETS:
        svg = _beautify_svg(svg, theme)

    return svg


def get_moon_phase() -> dict[str, Any]:
    """Calculate current moon phase and illumination."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    subj = to_kerykeion_subject(
        Subject(
            name="Moon",
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            longitude=0.0,
            latitude=0.0,
            timezone="UTC",
        )
    )
    sun_pos = subj.sun["position"]
    moon_pos = subj.moon["position"]
    angle = (moon_pos - sun_pos) % 360

    if angle < 22.5:
        phase = "New Moon"
    elif angle < 67.5:
        phase = "Waxing Crescent"
    elif angle < 112.5:
        phase = "First Quarter"
    elif angle < 157.5:
        phase = "Waxing Gibbous"
    elif angle < 202.5:
        phase = "Full Moon"
    elif angle < 247.5:
        phase = "Waning Gibbous"
    elif angle < 292.5:
        phase = "Last Quarter"
    elif angle < 337.5:
        phase = "Waning Crescent"
    else:
        phase = "New Moon"

    illumination = round((1 - math.cos(math.radians(angle))) / 2 * 100, 1)

    return {
        "phase": phase,
        "illumination_percent": illumination,
        "sun_longitude": round(sun_pos, 4),
        "moon_longitude": round(moon_pos, 4),
        "angle": round(angle, 2),
    }
