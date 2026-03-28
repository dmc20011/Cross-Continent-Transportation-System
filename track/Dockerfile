FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./lib ./lib

#ENV DB_HOST trackdb
#ENV DB_USER root
#ENV DB_PASS mypass
#ENV DB_NAME trackingdb
#ENV RABBITMQ_HOST localhost  

CMD ["fastapi", "run", "./lib/track.py", "--port", "80"]
