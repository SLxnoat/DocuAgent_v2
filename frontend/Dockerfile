# ─────────────────────────────────────────────────────────────────────────────
# DocuAgent AI — Frontend Dockerfile
# Multi-stage: Node 20 build → Nginx 1.27 static serve
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Cache node_modules layer separately from source code
COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline

# Copy source and build production bundle
COPY . .
RUN npm run build


# ── Stage 2: serve with nginx ─────────────────────────────────────────────────
FROM nginx:1.27-alpine

# Remove default nginx site
RUN rm -rf /usr/share/nginx/html/*

# Copy built SPA
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config: SPA routing + reverse proxy to backend API/WS
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
