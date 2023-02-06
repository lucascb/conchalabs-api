FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements/base.txt

CMD exec gunicorn -k uvicorn.workers.UvicornWorker --bind :$PORT --workers 1 --threads 8 --timeout 0 conchalabs.app:app
