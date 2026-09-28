FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies for WeasyPrint, Playwright and font rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libpango1.0-dev \
    libffi-dev \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libglib2.0-0 \
    fonts-liberation \
    fonts-dejavu \
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
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser binaries and dependencies
RUN playwright install chromium --with-deps

COPY . .

# Create data directories
RUN mkdir -p /app/data/storage/screenshots /app/data/storage/exports

EXPOSE 8000

CMD ["uvicorn", "app.main.app", "--host", "0.0.0.0", "--port", "8000"]
