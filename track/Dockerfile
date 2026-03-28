FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./lib ./lib

CMD ["fastapi", "run", "./lib/track.py", "--port", "80"]
