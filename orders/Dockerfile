FROM python:3.12-slim

WORKDIR /app

# 1. Copy requirements first (this layer is cached if requirements.txt doesn't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy code last (changes here don't invalidate pip install)
COPY orders.py .

EXPOSE 5001

CMD ["uvicorn", "orders:app", "--host", "0.0.0.0", "--port", "5001"]