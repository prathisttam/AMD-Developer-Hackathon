FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if your parser needs them (e.g., poppler-utils for pdfs)
# RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
