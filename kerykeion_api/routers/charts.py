"""API routers for chart endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from kerykeion_api.core.auth import verify_api_key
from kerykeion_api.models.schemas import (
    ChartRequest,
    CompositeRequest,
    ReturnRequest,
    Subject,
    SynastryRequest,
    TransitRequest,
)
from kerykeion_api.services.astrology import make_svg, serialize_subject, to_kerykeion_subject

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/v1/chart", tags=["charts"])


@router.post("/birth-chart")
@limiter.limit("30/minute")
def birth_chart(request: Request, body: ChartRequest, api_key: str = Depends(verify_api_key)):
    try:
        subj = to_kerykeion_subject(body.subject)
        data = serialize_subject(subj)
        svg = make_svg(subj, chart_type="Natal", theme=body.theme, renderer=body.renderer)
        if body.split_chart:
            return {"status": "OK", "chart_wheel": svg, "chart_data": data}
        return {"status": "OK", "chart": svg, "chart_data": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/synastry")
@limiter.limit("20/minute")
def synastry(request: Request, body: SynastryRequest, api_key: str = Depends(verify_api_key)):
    try:
        s1 = to_kerykeion_subject(body.subject_1)
        s2 = to_kerykeion_subject(body.subject_2)
        svg = make_svg(s1, chart_type="Synastry", second_obj=s2, theme=body.theme, renderer=body.renderer)
        if body.split_chart:
            return {
                "status": "OK",
                "chart_wheel": svg,
                "chart_data": {
                    "subject_1": serialize_subject(s1),
                    "subject_2": serialize_subject(s2),
                },
            }
        return {
            "status": "OK",
            "chart": svg,
            "chart_data": {
                "subject_1": serialize_subject(s1),
                "subject_2": serialize_subject(s2),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/transit")
@limiter.limit("20/minute")
def transit(request: Request, body: TransitRequest, api_key: str = Depends(verify_api_key)):
    try:
        subj = to_kerykeion_subject(body.subject)
        td = datetime.strptime(body.transit_date, "%Y-%m-%d")
        transit_subj = to_kerykeion_subject(
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
        svg = make_svg(subj, chart_type="Transit", second_obj=transit_subj, theme=body.theme, renderer=body.renderer)
        return {
            "status": "OK",
            "chart": svg,
            "transit_date": body.transit_date,
            "chart_data": {"natal": serialize_subject(subj), "transit": serialize_subject(transit_subj)},
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/composite")
@limiter.limit("20/minute")
def composite(request: Request, body: CompositeRequest, api_key: str = Depends(verify_api_key)):
    try:
        s1 = to_kerykeion_subject(body.subject_1)
        s2 = to_kerykeion_subject(body.subject_2)
        svg = make_svg(s1, chart_type="Composite", second_obj=s2, theme=body.theme, renderer=body.renderer)
        return {
            "status": "OK",
            "chart": svg,
            "chart_data": {"subject_1": serialize_subject(s1), "subject_2": serialize_subject(s2)},
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/solar-return")
@limiter.limit("20/minute")
def solar_return(request: Request, body: ReturnRequest, api_key: str = Depends(verify_api_key)):
    try:
        subj = to_kerykeion_subject(body.subject)
        sr = to_kerykeion_subject(
            Subject(
                name=f"{subj.name} Solar Return {body.return_year}",
                year=body.return_year,
                month=subj.month,
                day=subj.day,
                hour=subj.hour,
                minute=subj.minute,
                longitude=subj.lng,
                latitude=subj.lat,
                timezone=subj.tz_str,
            )
        )
        svg = make_svg(sr, chart_type="Natal", theme=body.theme, renderer=body.renderer)
        return {"status": "OK", "chart": svg, "return_year": body.return_year, "chart_data": serialize_subject(sr)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/lunar-return")
@limiter.limit("20/minute")
def lunar_return(request: Request, body: ReturnRequest, api_key: str = Depends(verify_api_key)):
    try:
        subj = to_kerykeion_subject(body.subject)
        lr = to_kerykeion_subject(
            Subject(
                name=f"{subj.name} Lunar Return {body.return_year}",
                year=body.return_year,
                month=subj.month,
                day=subj.day,
                hour=subj.hour,
                minute=subj.minute,
                longitude=subj.lng,
                latitude=subj.lat,
                timezone=subj.tz_str,
            )
        )
        svg = make_svg(lr, chart_type="Natal", theme=body.theme, renderer=body.renderer)
        return {"status": "OK", "chart": svg, "return_year": body.return_year, "chart_data": serialize_subject(lr)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
