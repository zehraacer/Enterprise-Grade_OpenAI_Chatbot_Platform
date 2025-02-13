# Dockerfile
# Multi-stage build kullanarak imaj boyutunu küçültme
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/wheels /wheels
COPY . .

RUN pip install --no-cache /wheels/*

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]