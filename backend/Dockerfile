FROM python:3.12-slim

WORKDIR /app

# Install curl (needed to fetch uv)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files (assuming pyproject.toml + uv.lock exist)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy project files
COPY backend ./backend
COPY services ./services

# Expose FastAPI port
EXPOSE 8000

# Default command: run FastAPI server via uv
CMD ["uv", "run", "-m", "app.main"]
