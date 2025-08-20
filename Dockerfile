# Multi-stage build for SERRA ORGIN Core
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for full-stack capabilities
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY pyproject.toml requirements.txt* ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -e .

# Copy package.json and install Node dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    docker.io \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create non-root user
RUN groupadd -r serra && useradd -r -g serra serra

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy Node dependencies from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy application source
COPY src/ ./src/
COPY web_ui/ ./web_ui/
COPY scraper/ ./scraper/
COPY deployment/ ./deployment/
COPY swarm/ ./swarm/
COPY core/ ./core/

# Copy configuration files
COPY pyproject.toml package.json ./
COPY .env.example .env

# Create necessary directories
RUN mkdir -p data logs temp uploads
RUN chown -R serra:serra /app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV NODE_PATH=/app/node_modules
ENV PATH=/app/node_modules/.bin:$PATH
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER serra

# Expose ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "-m", "serra_orgin.main"]
