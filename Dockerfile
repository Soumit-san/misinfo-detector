# ---------- Stage 1: Builder ----------
FROM python:3.11-slim as builder

WORKDIR /app

# Install system deps required to build wheels (temporary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a local folder
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy project files
COPY . .

# Ensure local binaries are in PATH
ENV PATH=/root/.local/bin:$PATH

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
