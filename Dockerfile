# Stage 1: Builder stage with all build dependencies
FROM python:3.11-slim-bookworm AS builder

# Set up apt for faster installations
RUN echo 'APT::Install-Recommends "false";' > /etc/apt/apt.conf.d/00recommends && \
    echo 'APT::Install-Suggests "false";' >> /etc/apt/apt.conf.d/00recommends && \
    echo 'APT::Get::Assume-Yes "true";' >> /etc/apt/apt.conf.d/00global && \
    echo 'APT::Get::force-yes "true";' >> /etc/apt/apt.conf.d/00global

# Install system dependencies with optimized apt settings
RUN apt-get update -o Acquire::http::No-Cache=True && \
    apt-get install -o Dpkg::Options::="--force-confold" -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy the rest of the application (including entrypoint)
COPY . .

# Stage 2: Final production image
FROM python:3.11-slim-bookworm

# Configure apt for production image
RUN echo 'APT::Install-Recommends "false";' > /etc/apt/apt.conf.d/00recommends && \
    echo 'APT::Get::Assume-Yes "true";' >> /etc/apt/apt.conf.d/00global

# Install runtime dependencies
RUN apt-get update -o Acquire::http::No-Cache=True && \
    apt-get install -o Dpkg::Options::="--force-confold" -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -r appuser && \
    mkdir -p /app && \
    chown appuser:appuser /app

WORKDIR /app

# Copy installed Python packages
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code (including entrypoint)
COPY --from=builder --chown=appuser:appuser /app /app

# Verify entrypoint exists before making it executable
RUN test -f /app/entrypoint.prod.sh && \
    chmod +x /app/entrypoint.prod.sh || \
    (echo "Entrypoint file missing!" && exit 1)

# Environment variables
ENV PATH="/home/appuser/.local/bin:${PATH}"
ENV PYTHONPATH="/home/appuser/.local/lib/python3.11/site-packages"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8000

CMD ["/app/entrypoint.prod.sh"]