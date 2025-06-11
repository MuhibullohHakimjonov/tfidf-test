FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    libffi-dev \
    libssl-dev \
    cargo \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas0 \
    liblapack3 \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local/
COPY . .

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
