FROM python:3.11-slim

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download Swiss Ephemeris data
RUN python -c "from kerykeion.settings.kerykeion_settings import get_settings; get_settings()"

COPY kerykeion_api/ ./kerykeion_api/
COPY custom_renderer.py .
COPY zodiac_paths.py .

EXPOSE 8000

CMD ["uvicorn", "kerykeion_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
