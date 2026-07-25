# ==============================================================
# Dockerfile
# AI Hotel Booking Competitor Intelligence Platform — Backend
# ==============================================================
# Multi-stage build:
#   Stage 1 (builder) — installs Python deps in a venv
#   Stage 2 (runtime) — copies only the venv + app source
#
# Deployed to Render via render.yaml.
# Playwright browsers are installed at build time.
# ==============================================================

# ── Stage 1: Builder ──────────────────────────────────────────
FROM python:3.12-slim AS builder

# Prevent .pyc files and enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install OS-level build dependencies (needed by asyncpg, psycopg, lxml)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries (Chromium only for scraping)
RUN playwright install chromium --with-deps


# ── Stage 2: Runtime ──────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    # Render sets PORT; Uvicorn will bind to it.
    PORT=8000 \
    # Tell Playwright where to find the installed browsers
    PLAYWRIGHT_BROWSERS_PATH=/opt/venv/lib/python3.12/site-packages/playwright/driver/package/.local-browsers

WORKDIR /app

# Runtime OS libraries required by asyncpg / psycopg / lxml + Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libxml2 \
        libxslt1.1 \
        # Playwright runtime deps (Chromium headless)
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder (includes Playwright browsers)
COPY --from=builder /opt/venv /opt/venv

# Copy application source
COPY . .

# Non-root user for security
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser

# Expose port (Render overrides via $PORT env var)
EXPOSE ${PORT}

# Health check — Render uses this to know the app is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:${PORT}/api/v1/health').raise_for_status()"

# Start command (matches render.yaml startCommand)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
