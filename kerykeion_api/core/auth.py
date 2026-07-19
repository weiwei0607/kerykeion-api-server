"""Authentication and rate limiting dependencies."""

import os
from typing import Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Security(api_key_header),
) -> str:
    """Verify API key from header or query param."""
    expected = os.environ.get("API_KEY", "")
    # If no API_KEY is set, allow all (dev mode)
    if not expected:
        return "dev"
    key = api_key or request.query_params.get("api_key")
    if not key:
        raise HTTPException(status_code=401, detail="API key required")
    if key != expected:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key
