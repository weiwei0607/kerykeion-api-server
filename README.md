# Kerykeion Astrology API Server

Free alternative to RapidAPI Astrologer. Powered by NASA JPL ephemerides via Kerykeion + Swiss Ephemeris.

## Features

- Birth charts (Natal)
- Synastry (relationship compatibility)
- Transit charts
- Composite charts
- Solar & Lunar returns
- Current moment chart
- Moon phase data
- 5 themes: light, dark, cosmic, sakura, gold
- Two renderers: Kerykeion (full) / Custom (lightweight)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m kerykeion_api.main
```

## API Authentication

Set `API_KEY` in your environment or `.env` file. Include it in requests:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/now/moon-phase
```

If `API_KEY` is not set, the API runs in dev mode (no auth required).

## Deployment

### Render.com

Click the button or push to GitHub with `render.yaml` in the root.

### Docker

```bash
docker build -t kerykeion-api .
docker run -p 8000:8000 -e API_KEY=your-key kerykeion-api
```

## Endpoints

See `/docs` (Swagger UI) or `/redoc` (ReDoc) when running locally.

## Rate Limits

- Birth chart: 30/minute
- Synastry / Transit / Composite / Returns: 20/minute
- Moon phase: 60/minute

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | "" | API authentication key |
| `CORS_ORIGINS` | "*" | Comma-separated allowed origins |
| `PORT` | 8000 | Server port |

## License

MIT
