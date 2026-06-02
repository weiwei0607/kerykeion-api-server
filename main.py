"""
Kerykeion FastAPI Astrology Server
Free alternative to RapidAPI Astrologer.
Powered by NASA JPL ephemerides via Kerykeion + Swiss Ephemeris.
"""

import json
import os
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, Field

app = FastAPI(
    title="Kerykeion Astrology API",
    description="Free birth charts, synastry, transits, composite charts, returns & moon phases.",
    version="1.0.0",
)

# Allow CORS for local dev / frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ──────────────────────────────────────────

class Subject(BaseModel):
    name: str = "Subject"
    year: int = Field(..., ge=1800, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(12, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    timezone: str = "UTC"


class ChartRequest(BaseModel):
    subject: Subject
    theme: Literal["light", "dark", "cosmic", "sakura", "gold"] = "cosmic"
    split_chart: bool = False


class SynastryRequest(BaseModel):
    subject_1: Subject
    subject_2: Subject
    theme: Literal["light", "dark", "cosmic", "sakura", "gold"] = "cosmic"
    split_chart: bool = False


class TransitRequest(BaseModel):
    subject: Subject
    transit_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        description="YYYY-MM-DD",
    )
    theme: Literal["light", "dark", "cosmic", "sakura", "gold"] = "cosmic"


class CompositeRequest(BaseModel):
    subject_1: Subject
    subject_2: Subject
    theme: Literal["light", "dark", "cosmic", "sakura", "gold"] = "cosmic"


class ReturnRequest(BaseModel):
    subject: Subject
    return_year: int = Field(..., ge=1800, le=2100)
    theme: Literal["light", "dark", "cosmic", "sakura", "gold"] = "cosmic"


# ── Helpers ──────────────────────────────────────────────────

def _to_kerykeion_subject(s: Subject):
    """Convert Pydantic Subject to Kerykeion AstrologicalSubject."""
    from kerykeion import AstrologicalSubject
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


def _serialize_subject(subj):
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


_THEME_PRESETS = {
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
        "zodiac_bg": ["#0d1235", "#131c45", "#0d1235", "#131c45", "#0d1235", "#131c45",
                      "#0d1235", "#131c45", "#0d1235", "#131c45", "#0d1235", "#131c45"],
        "glow": True,
        "bg_gradient": "radial-gradient(circle at 50% 50%, #0f1a4a 0%, #080c24 70%)",
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
        "zodiac_bg": ["#fdf2f4", "#fce7f0", "#fdf2f4", "#fce7f0", "#fdf2f4", "#fce7f0",
                      "#fdf2f4", "#fce7f0", "#fdf2f4", "#fce7f0", "#fdf2f4", "#fce7f0"],
        "glow": False,
        "bg_gradient": "linear-gradient(135deg, #fdf2f4 0%, #fce7f0 100%)",
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
        "zodiac_bg": ["#0f0c06", "#1a1408", "#0f0c06", "#1a1408", "#0f0c06", "#1a1408",
                      "#0f0c06", "#1a1408", "#0f0c06", "#1a1408", "#0f0c06", "#1a1408"],
        "glow": True,
        "bg_gradient": "radial-gradient(circle at 50% 50%, #1c1508 0%, #0a0a0a 70%)",
    },
}


def _beautify_svg(svg: str, theme: str) -> str:
    """Post-process Kerykeion SVG with custom color themes & effects.
    
    Strategy: keep the original :root block intact (it has 100+ vars),
    then inject a SECOND :root block that overrides only the colors we care about.
    CSS cascade means the later :root wins for same-name vars.
    """
    import re
    preset = _THEME_PRESETS.get(theme)
    if preset is None:
        return svg

    # Build override :root block (only vars we want to change)
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
"""
    for i, color in enumerate(preset['zodiac_bg']):
        overrides += f"    --kerykeion-chart-color-zodiac-bg-{i}: {color};\n"
        overrides += f"    --kerykeion-modern-zodiac-bg-{i}: {color};\n"
    overrides += "}\n"

    # Find the FIRST <style kr:node='Theme_Colors_Tag'> block and append override :root inside it
    # We inject after the existing :root { ... } closing brace within that style tag
    style_match = re.search(r"(<style\s+kr:node='Theme_Colors_Tag'>.*?</style>)", svg, re.DOTALL)
    if style_match:
        original_style = style_match.group(1)
        # Insert overrides just before </style>
        new_style = original_style.replace("</style>", f"\n{overrides}</style>")
        svg = svg.replace(original_style, new_style, 1)
    else:
        # Fallback: inject after </title>
        svg = svg.replace("</title>", f"</title>\n<style>{overrides}</style>", 1)

    # Inject glow effects + background rect
    extra_css = ""
    if preset.get("glow"):
        extra_css += "text {{ filter: drop-shadow(0 0 1px rgba(255,255,255,0.3)); }}\n"
        extra_css += "circle[stroke*='#'] {{ filter: drop-shadow(0 0 2px rgba(255,255,255,0.15)); }}\n"

    bg_rect = f'<rect width="100%" height="100%" fill="{preset["paper"]}" />\n'

    # Insert right after <svg ...> opening tag
    svg = re.sub(r"(<svg[^>]*>)", rf"\1\n<defs><style>{extra_css}</style></defs>\n{bg_rect}", svg, count=1)

    return svg


def _make_svg(subject, chart_type="Natal", second_obj=None, theme="dark"):
    """Render SVG chart using Kerykeion, then apply custom theme beautification."""
    from kerykeion import KerykeionChartSVG
    # Kerykeion only knows built-in themes; use 'dark' as base for custom presets
    kerykeion_theme = theme if theme in ("dark", "light", "classic") else "dark"
    chart = KerykeionChartSVG(
        subject,
        chart_type=chart_type,
        second_obj=second_obj,
        theme=kerykeion_theme,
    )
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        chart.output_directory = tmpdir
        chart.makeSVG()
        svg_files = [f for f in os.listdir(tmpdir) if f.endswith(".svg")]
        if not svg_files:
            raise RuntimeError("SVG generation failed: no .svg file found")
        with open(os.path.join(tmpdir, svg_files[0]), "r", encoding="utf-8") as f:
            svg = f.read()

    # Apply custom beautification if theme is one of our presets
    if theme in _THEME_PRESETS:
        svg = _beautify_svg(svg, theme)

    return svg



# ── Endpoints ────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "engine": "kerykeion", "ephemeris": "NASA JPL"}


@app.post("/api/v1/chart/birth-chart")
def birth_chart(req: ChartRequest):
    try:
        subj = _to_kerykeion_subject(req.subject)
        data = _serialize_subject(subj)
        svg = _make_svg(subj, chart_type="Natal", theme=req.theme)
        if req.split_chart:
            return {
                "status": "OK",
                "chart_wheel": svg,
                "chart_data": data,
            }
        return {
            "status": "OK",
            "chart": svg,
            "chart_data": data,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/chart/synastry")
def synastry(req: SynastryRequest):
    try:
        s1 = _to_kerykeion_subject(req.subject_1)
        s2 = _to_kerykeion_subject(req.subject_2)
        svg = _make_svg(s1, chart_type="Synastry", second_obj=s2, theme=req.theme)
        if req.split_chart:
            return {
                "status": "OK",
                "chart_wheel": svg,
                "chart_data": {
                    "subject_1": _serialize_subject(s1),
                    "subject_2": _serialize_subject(s2),
                },
            }
        return {
            "status": "OK",
            "chart": svg,
            "chart_data": {
                "subject_1": _serialize_subject(s1),
                "subject_2": _serialize_subject(s2),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/chart/transit")
def transit(req: TransitRequest):
    try:
        subj = _to_kerykeion_subject(req.subject)
        td = datetime.strptime(req.transit_date, "%Y-%m-%d")
        transit_subj = _to_kerykeion_subject(
            Subject(
                name="Transit",
                year=td.year,
                month=td.month,
                day=td.day,
                hour=12,
                minute=0,
                longitude=subj.lng,
                latitude=subj.lat,
                timezone=subj.tz_str,
            )
        )
        svg = _make_svg(subj, chart_type="Transit", second_obj=transit_subj, theme=req.theme)
        return {
            "status": "OK",
            "chart": svg,
            "transit_date": req.transit_date,
            "chart_data": {
                "natal": _serialize_subject(subj),
                "transit": _serialize_subject(transit_subj),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/chart/composite")
def composite(req: CompositeRequest):
    try:
        s1 = _to_kerykeion_subject(req.subject_1)
        s2 = _to_kerykeion_subject(req.subject_2)
        svg = _make_svg(s1, chart_type="Composite", second_obj=s2, theme=req.theme)
        return {
            "status": "OK",
            "chart": svg,
            "chart_data": {
                "subject_1": _serialize_subject(s1),
                "subject_2": _serialize_subject(s2),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/chart/solar-return")
def solar_return(req: ReturnRequest):
    try:
        subj = _to_kerykeion_subject(req.subject)
        # Solar return: same date/month but target year
        sr = _to_kerykeion_subject(
            Subject(
                name=f"{subj.name} Solar Return {req.return_year}",
                year=req.return_year,
                month=subj.month,
                day=subj.day,
                hour=subj.hour,
                minute=subj.minute,
                longitude=subj.lng,
                latitude=subj.lat,
                timezone=subj.tz_str,
            )
        )
        svg = _make_svg(sr, chart_type="Natal", theme=req.theme)
        return {
            "status": "OK",
            "chart": svg,
            "return_year": req.return_year,
            "chart_data": _serialize_subject(sr),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/chart/lunar-return")
def lunar_return(req: ReturnRequest):
    try:
        subj = _to_kerykeion_subject(req.subject)
        lr = _to_kerykeion_subject(
            Subject(
                name=f"{subj.name} Lunar Return {req.return_year}",
                year=req.return_year,
                month=subj.month,
                day=subj.day,
                hour=subj.hour,
                minute=subj.minute,
                longitude=subj.lng,
                latitude=subj.lat,
                timezone=subj.tz_str,
            )
        )
        svg = _make_svg(lr, chart_type="Natal", theme=req.theme)
        return {
            "status": "OK",
            "chart": svg,
            "return_year": req.return_year,
            "chart_data": _serialize_subject(lr),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/now/chart")
def now_chart(
    longitude: float = 121.53,
    latitude: float = 25.04,
    timezone: str = "Asia/Taipei",
    theme: Literal["light", "dark", "cosmic", "sakura", "gold"] = "cosmic",
):
    """Current moment chart (UTC now)."""
    try:
        now = datetime.now(timezone.utc)
        subj = _to_kerykeion_subject(
            Subject(
                name="Now",
                year=now.year,
                month=now.month,
                day=now.day,
                hour=now.hour,
                minute=now.minute,
                longitude=longitude,
                latitude=latitude,
                timezone=timezone,
            )
        )
        svg = _make_svg(subj, chart_type="Natal", theme=theme)
        return {
            "status": "OK",
            "chart": svg,
            "chart_data": _serialize_subject(subj),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/now/moon-phase")
def moon_phase():
    """Current moon phase name and illumination percentage."""
    try:
        from kerykeion.kr_types.kr_models import AstrologicalSubjectModel
        # Kerykeion doesn't expose moon phase directly, but we can compute it
        # from the sun-moon angle.
        now = datetime.now(timezone.utc)
        subj = _to_kerykeion_subject(
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

        # Map angle to phase
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

        # Illumination ~ (1 - cos(angle°)) / 2 * 100
        import math
        illumination = round((1 - math.cos(math.radians(angle))) / 2 * 100, 1)

        return {
            "status": "OK",
            "phase": phase,
            "illumination_percent": illumination,
            "sun_longitude": round(sun_pos, 4),
            "moon_longitude": round(moon_pos, 4),
            "angle": round(angle, 2),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Raw SVG convenience endpoint ─────────────────────────────

@app.post("/api/v1/chart/birth-chart/svg", response_class=PlainTextResponse)
def birth_chart_svg(req: ChartRequest):
    subj = _to_kerykeion_subject(req.subject)
    svg = _make_svg(subj, chart_type="Natal", theme=req.theme)
    return svg


# ── Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
