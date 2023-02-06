FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements/base.txt

CMD ["alembic", "upgrade", "head"]
