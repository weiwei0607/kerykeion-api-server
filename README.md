# Kerykeion Astrology API Server

Free alternative to RapidAPI Astrologer. Self-hosted birth charts, synastry, transits, composite charts, returns & moon phases.

## Powered by
- [Kerykeion](https://github.com/g-battaglia/kerykeion) — NASA JPL ephemerides
- [Swiss Ephemeris](https://www.astro.com/swisseph/) — sub-arcsecond precision
- FastAPI + Uvicorn

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/chart/birth-chart` | POST | Natal chart SVG + data |
| `/api/v1/chart/synastry` | POST | Synastry chart (2 people) |
| `/api/v1/chart/transit` | POST | Transit chart vs natal |
| `/api/v1/chart/composite` | POST | Composite chart (midpoint) |
| `/api/v1/chart/solar-return` | POST | Solar return chart |
| `/api/v1/chart/lunar-return` | POST | Lunar return chart |
| `/api/v1/now/chart` | GET | Current moment chart |
| `/api/v1/now/moon-phase` | GET | Current moon phase |

## Quick Start

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Test:
```bash
curl -X POST http://localhost:8000/api/v1/chart/birth-chart \
  -H "Content-Type: application/json" \
  -d '{
    "subject": {
      "name": "John Lennon",
      "year": 1940, "month": 10, "day": 9,
      "hour": 18, "minute": 30,
      "longitude": -2.98, "latitude": 53.41,
      "timezone": "Europe/London"
    },
    "theme": "dark"
  }'
```

## Deploy to Render

1. Push this repo to GitHub
2. Connect repo on [Render](https://render.com)
3. Use `render.yaml` blueprint (auto-detected)
4. Free tier works fine

## No API Key Required

Unlike RapidAPI, this server has **no API key**. If you deploy publicly, consider adding:
- A simple Bearer token middleware
- Rate limiting (`slowapi`)
- CORS origin whitelist
