# ─────────────────────────────────────────────────────────────────────────────
# DocuAgent AI — Backend Dockerfile
# Python 3.12-slim (Debian 12 Bookworm) for WeasyPrint 70 + Playwright compat.
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build tools only in builder stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.12/site-packages"

WORKDIR /app

# ── System deps:
#    WeasyPrint 70  → Pango, Cairo, GDK-PixBuf, Fontconfig
#    Playwright     → Chromium shared libs
# ─────────────────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # WeasyPrint / Cairo / Pango
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libharfbuzz0b \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libglib2.0-0 \
    libffi8 \
    fontconfig \
    fonts-liberation \
    fonts-dejavu-core \
    # Playwright / Chromium
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libx11-6 \
    libxext6 \
    libxss1 \
    # curl for healthcheck
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built Python packages from builder
COPY --from=builder /install /install

# Install Playwright browser binaries (Chromium only)
RUN PYTHONPATH="/install/lib/python3.12/site-packages" \
    playwright install chromium --with-deps 2>/dev/null || \
    python3 -m playwright install chromium --with-deps

# Copy application source
COPY . .

# Create data directories and set permissions
RUN mkdir -p /app/data/storage/screenshots /app/data/storage/exports \
    && addgroup --system --gid 1001 docuagent \
    && adduser --system --uid 1001 --gid 1001 --no-create-home docuagent \
    && chown -R docuagent:docuagent /app/data

USER docuagent

EXPOSE 8030

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fs http://localhost:8030/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8030", "--workers", "1"]
