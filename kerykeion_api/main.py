"""Main FastAPI application with middleware and router registration."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from kerykeion_api.core.config import get_settings
from kerykeion_api.core.logging import configure_logging
from kerykeion_api.routers import charts, now

configure_logging()

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    description="Free birth charts, synastry, transits, composite charts, returns & moon phases.",
    version=settings.app_version,
)
app.state.limiter = limiter

# CORS - restrict in production
cors_origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"status": "error", "detail": "Rate limit exceeded. Try again later."},
    )


@app.get("/health")
def health():
    return {"status": "ok", "engine": "kerykeion", "ephemeris": "NASA JPL", "version": settings.app_version}


app.include_router(charts.router)
app.include_router(now.router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run("kerykeion_api.main:app", host="0.0.0.0", port=port)
