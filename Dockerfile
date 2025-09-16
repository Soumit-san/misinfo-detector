FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for spacy, psycopg2, etc.
RUN apt-get update && apt-get install -y \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
