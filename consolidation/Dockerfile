FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY consolidate.py .

EXPOSE 5002

CMD ["uvicorn", "consolidate:app", "--host", "0.0.0.0", "--port", "5002"]
