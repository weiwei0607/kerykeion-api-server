"""Pydantic models for request/response validation."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


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
    theme: Literal["light", "dark", "cosmic", "sakura", "gold", "classic"] = "cosmic"
    renderer: Literal["kerykeion", "custom"] = "kerykeion"
    split_chart: bool = False


class SynastryRequest(BaseModel):
    subject_1: Subject
    subject_2: Subject
    theme: Literal["light", "dark", "cosmic", "sakura", "gold", "classic"] = "cosmic"
    renderer: Literal["kerykeion", "custom"] = "kerykeion"
    split_chart: bool = False


class TransitRequest(BaseModel):
    subject: Subject
    transit_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        description="YYYY-MM-DD",
    )
    theme: Literal["light", "dark", "cosmic", "sakura", "gold", "classic"] = "cosmic"
    renderer: Literal["kerykeion", "custom"] = "kerykeion"


class CompositeRequest(BaseModel):
    subject_1: Subject
    subject_2: Subject
    theme: Literal["light", "dark", "cosmic", "sakura", "gold", "classic"] = "cosmic"
    renderer: Literal["kerykeion", "custom"] = "kerykeion"


class ReturnRequest(BaseModel):
    subject: Subject
    return_year: int = Field(..., ge=1800, le=2100)
    theme: Literal["light", "dark", "cosmic", "sakura", "gold", "classic"] = "cosmic"
    renderer: Literal["kerykeion", "custom"] = "kerykeion"


class NowChartRequest(BaseModel):
    longitude: float = Field(121.53, ge=-180, le=180)
    latitude: float = Field(25.04, ge=-90, le=90)
    timezone: str = "Asia/Taipei"
    theme: Literal["light", "dark", "cosmic", "sakura", "gold", "classic"] = "cosmic"
