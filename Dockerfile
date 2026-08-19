# ==============================================================================
# ORBIT-X Unified Multi-Stage Production Dockerfile (Single Package)
# ==============================================================================

# Stage 1: Build React 18 + Three.js WebGL Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Unified Backend, AI Engine & WebGL HUD Runtime
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install Python backend dependencies
COPY backend/pyproject.toml backend/README.md ./
COPY backend/app ./app
RUN uv pip install --system --no-cache .

# Copy remaining backend source & models
COPY backend/ ./

# Copy compiled frontend distribution into app for single-port unified serving
COPY --from=frontend-builder /frontend/dist ./frontend_dist

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
