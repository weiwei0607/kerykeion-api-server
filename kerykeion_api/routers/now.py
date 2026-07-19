"""API routers for current moment endpoints."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from kerykeion_api.core.auth import verify_api_key
from kerykeion_api.models.schemas import NowChartRequest, Subject
from kerykeion_api.services.astrology import make_svg, serialize_subject, to_kerykeion_subject
from kerykeion_api.services.astrology import get_moon_phase as _get_moon_phase

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/v1/now", tags=["now"])


@router.get("/chart")
@limiter.limit("30/minute")
def now_chart(
    longitude: float = 121.53,
    latitude: float = 25.04,
    timezone: str = "Asia/Taipei",
    theme: Literal["light", "dark", "cosmic", "sakura", "gold", "classic"] = "cosmic",
    api_key: str = Depends(verify_api_key),
):
    """Current moment chart (UTC now)."""
    try:
        from datetime import datetime, timezone as tz
        now = datetime.now(tz.utc)
        subj = to_kerykeion_subject(
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
        svg = make_svg(subj, chart_type="Natal", theme=theme, renderer="kerykeion")
        return {"status": "OK", "chart": svg, "chart_data": serialize_subject(subj)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/moon-phase")
@limiter.limit("60/minute")
def moon_phase(api_key: str = Depends(verify_api_key)):
    """Current moon phase name and illumination percentage."""
    try:
        data = _get_moon_phase()
        return {"status": "OK", **data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
