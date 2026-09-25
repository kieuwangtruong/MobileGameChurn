# ==============================================================================
# Production-Grade Dockerfile for Mobile Game Churn Analytics & LiveOps Studio
# Optimized for: Security (Non-root), Layer Caching, Minimal Size & Observability
# ==============================================================================

# 1. Base Image: Python 3.10 Slim (Official Debian-based minimal image)
FROM python:3.10-slim

# 2. Environment Variables for Python & Streamlit in Production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 3. Working Directory
WORKDIR /app

# 4. Install essential OS runtime dependencies:
#    - curl: for container HEALTHCHECK
#    - libgomp1: OpenMP runtime required by XGBoost, LightGBM & Scikit-learn
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# 5. Security: Create non-root system user and group (UID/GID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m -d /home/appuser appuser

# 6. Layer Caching: Copy dependency definition first
COPY requirements.txt /app/requirements.txt

# 7. Install Python packages without cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 8. Copy Application Source Code
COPY . /app

# 9. Set permissions for non-root user
RUN chown -R appuser:appgroup /app /home/appuser

# 10. Switch to Non-Root User for security compliance
USER appuser

# 11. Expose Default Port (Can be overridden by Render via $PORT)
ENV PORT=8501
EXPOSE 8501

# 12. Healthcheck: Query Streamlit's native health endpoint (supports dynamic $PORT)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:${PORT:-8501}/_stcore/health || exit 1

# 13. Application Entrypoint: Support Render dynamic $PORT and local 8501 default
CMD ["sh", "-c", "streamlit run dashboard/app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false --browser.gatherUsageStats=false"]

