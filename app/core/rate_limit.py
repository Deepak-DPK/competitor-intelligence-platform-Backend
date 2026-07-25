"""
app/core/rate_limit.py
----------------------
Rate limiting configuration using slowapi.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

# In-memory limiter based on the client IP address.
# Suitable for a single Render instance.
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app: FastAPI) -> None:
    """Register the slowapi limiter to the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
