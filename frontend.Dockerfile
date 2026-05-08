FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8501

WORKDIR /app/frontend

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
