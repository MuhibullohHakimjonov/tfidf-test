# TFIDF Project

## 📦 Описание

Этот проект представляет собой Django-приложение, развёрнутое с использованием
Docker и PostgreSQL. Он включает в себя настройку `gunicorn` для продакшн-сервера,
сборку статических файлов и автоматическое применение миграций при старте контейнера.


## 📁 Структура проекта


├── config/ # Конфигурация проекта Django (settings, urls, wsgi)

├── tfidf/ # Основное Django-приложение

├── static/ # Статические файлы (генерируются collectstatic)

├── media/ # Медиа-файлы (загрузка пользователями)

├── requirements.txt # Список зависимостей Python

├── Dockerfile # Описание Docker-образа

├── docker-compose.yml # Docker Compose конфигурация для web и db

├── .env # Файл переменных окружения

├── entrypoint.sh # Скрипт запуска приложения (миграции, collectstatic, gunicorn)

└── README.md # Документация проекта


## 🚀 Запуск приложения

### 📋 Зависимости

Для запуска проекта необходимы:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### 🛠 Шаги для запуска

1. **Клонировать репозиторий:**

```bash
   git clone git@github.com:MuhibullohHakimjonov/tfidf-test.git
```

2. Создать .env файл в корневом каталоге и указать параметры

Пример .env файла:
```
DEBUG=False
SECRET_KEY=supersecretkey
POSTGRES_DB=tfidf
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
DB_HOST=db
DB_PORT=5432
```

3. Построить и запустить контейнеры:
```commandline
docker-compose up --build
```
📦 Версия приложения
v1.1

## 📜 История изменений (Changelog)
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

