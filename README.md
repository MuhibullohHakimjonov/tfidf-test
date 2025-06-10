# TFIDF Project

## 📦 Описание


Этот проект представляет собой Django-приложение, развёрнутое с использованием Docker, MongoDB и PostgreSQL.
Он включает:

- API для анализа TF-IDF текста
- Хранение статистики в MongoDB, метаданных — в PostgreSQL
- Frontend на Vue.js
- Продакшн-сервер с Gunicorn и Nginx
- Поддержку Celery и Redis для фоновых задач (например, отправки email-кодов)


## 📁 Структура проекта

<pre>
├── config/             # Конфигурация проекта Django
├── tfidf/              # Основное Django-приложение
├── user/               # Пользовательское приложение
├── frontend/           # Vue.js клиентская часть
├── static/             # Статика Django (collectstatic)
├── media/              # Медиа-файлы пользователей
├── entrypoint.sh       # Скрипт запуска миграций и collectstatic
├── Dockerfile          # Docker-образ для backend
├── docker-compose.yml  # Docker Compose конфигурация
├── nginx/              # Конфигурация Nginx (nginx.conf)
├── .env                # Переменные окружения
└── README.md           # Документация проекта
</pre>

## 🚀 Запуск приложения

### 📋 Зависимости

Для запуска проекта необходимы:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### 🛠 Шаги для запуска

1. **Клонировать репозиторий:**

```bash
   git clone https://github.com/MuhibullohHakimjonov/tfidf-test.git
   cd tfidf-test
```

2. Создать .env файл в корневом каталоге и указать параметры

Пример .env файла:
```text
DJANGO_READ_DOT_ENV_FILE=True
DJANGO_SECRET_KEY=django-secret-key
DJANGO_DEBUG=False

DATABASE_NAME=example_db
POSTGRES_USER=example_user
POSTGRES_PASSWORD=example_password
POSTGRES_HOST=postgres
POSTGRES_PORT=example_port

# MongoDB
MONGO_USERNAME=example_user
MONGO_PASSWORD=example_password
MONGO_HOST=mongo
MONGO_PORT=example_port
MONGO_DB_NAME=example_db

# Email
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password

REDIS_HOST=redis
REDIS_PORT=redis_port
```

3. Построить и запустить контейнеры:
```bash
  docker-compose up --build -d
```




📦 Версия приложения
v2.0

## 📜 История изменений (Changelog)

### v2.0
- Добавлен фронтенд на Vue.js и интеграция через Nginx
- Поддержка PostgreSQL + MongoDB
- Reverse proxy через Nginx
- Добавлена поддержка Celery и Redis для отправки email-кодов и хранения временных данных
- Добавлен Rate Limit(throttle) и Пагинация для улучшения производительности
- Обновлён Docker (docker-compose): добавлены сервисы Celery, Redis, Frontend (Vue.js) и Nginx
- Добавлены новые API endpoints для реализации логики работы с:
  - документами (documents)
  - коллекциями (collections)
  - пользователями (users)



### v1.3
- удаление Ngnix из проекта
- Обновлена конфигурация .env, Dockerfile и docker-compose.yml
- Улучшена структура README
### v1.2
- Переход с PostgreSQL на MongoDB
- Облегчённый Mongo-образ (mongo:7-jammy)
- Обновлена конфигурация .env, Dockerfile и docker-compose.yml
- Улучшена структура README

### v1.1
- Контейнеризация проекта с Docker и Docker Compose
- Использование gunicorn как сервера в продакшн-режиме
- Автоматическое выполнение migrate и collectstatic при старте
- Поддержка .env для конфигурации параметров
- Минимизированный образ на базе python:3.12-slim

### v1.0
- Базовый Django-проект без контейнеризации
- Локальный запуск через runserver
- Настройки прописаны в settings.py

