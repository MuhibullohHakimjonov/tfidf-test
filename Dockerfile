FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev cargo

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt gunicorn


FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache libffi openssl

COPY --from=builder /install /usr/local

COPY . .


EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=4", "--threads=2", "--timeout=120"]
