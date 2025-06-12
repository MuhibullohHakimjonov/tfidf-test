# TFIDF Project

Ссылка на работающий сайт http://37.9.53.228/ \
Документация сайта http://37.9.53.228/api/docs/

## 📦 Описание

Данный проект представляет собой полнофункциональное Django-приложение для
работы с текстовыми документами и их статистическим анализом. Система
предоставляет API для загрузки файлов и вычисления TF-IDF, а также интерфейс
пользователя на Vue.js.\
Функциональные возможности:

- Загрузка текстовых файлов пользователями.
- Расчёт TF-IDF для слов в документах.
- Хранение статистики TF-IDF в MongoDB.
- Хранение метаданных документов, коллекций и пользователей в PostgreSQL.
- Регистрация пользователей с подтверждением email (код подтверждения отправляется через Celery и Redis).
- Разграничение доступа к API на основе аутентификации.
- Frontend на Vue.js для взаимодействия с API.
- Продакшн-развёртывание через Docker с использованием Nginx и Gunicorn.
- Асинхронная обработка задач с помощью Celery и Redis.

## ⚙️ Используемые технологии

- Python 3.12+
- Django 5.x
- Django REST Framework (DRF)
- Celery
- Redis
- MongoDB (pymongo)
- PostgreSQL
- Vue.js 3 (Composition API)
- Vite
- Docker & Docker Compose
- Nginx (reverse proxy)

## 📁 Структура проекта

<pre>
├── config/             # Конфигурация проекта Django
├── tfidf/              # Основное Django-приложение
├── user/               # Пользовательское приложение
├── frontend/           # Vue.js клиентская часть
├── static/             # Статика Django (collectstatic)
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
------
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
EMAIL_HOST_PASSWORD=your-password # Инструкция как получить пароль: https://www.getmailbird.com/ru/parol-prilozheniya-gmail/

REDIS_HOST=redis
REDIS_PORT=redis_port
```
--------
3. В nginx/default.conf: Замените 37.9.53.228 на ip вашего vm

---------
4. Создать .env файл внутри 'frontend/' и указать параметр
   Пример .env файла:
------
```text
VITE_API_URL=http://ip вашего vm/api/
```
----
5. Построить и запустить контейнеры:
----
```bash
  docker compose up --build -d
```
---

6. Чтобы открыть: http:// ip-вашего-vm /

-----
📦 Версия приложения
v2.0

## 📜 История изменений (Changelog)

### v3.0

- Новый API эндпойнт:
  GET /api/documents/<document_id>/huffman/
  Возвращает закодированное содержимое документа с использованием алгоритма Хаффмана,
- Мелкие улучшения фронтенда: исправлены стили таблицы и порядок элементов на странице Хаффмана
- Ограничение (Rate Limiting / Throttle):

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

