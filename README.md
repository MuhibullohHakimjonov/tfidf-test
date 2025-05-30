# TFIDF Project

## 📦 Описание

Этот проект представляет собой Django-приложение, развёрнутое с использованием Docker и MongoDB.
Он включает в себя настройку gunicorn для продакшн-сервера, сборку статических файлов и автоматическое 
применение миграций (если используются) при старте контейнера.


## 📁 Структура проекта


├── config/              # Конфигурация проекта Django (settings, urls, wsgi)\
├── tfidf/               # Основное Django-приложение\
├── static/              # Статические файлы (генерируются collectstatic)\
├── media/               # Медиа-файлы (загрузка пользователями)\
├── requirements.txt     # Список зависимостей Python\
├── Dockerfile           # Описание Docker-образа\
├── docker-compose.yml   # Docker Compose конфигурация для web, MongoDB\
├── .env                 # Файл переменных окружения\
└── README.md            # Документация проекта


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
DJANGO_SECRET_KEY=very-secret-key
DJANGO_DEBUG=False
MONGO_INITDB_ROOT_USERNAME=username
MONGO_INITDB_ROOT_PASSWORD=password
MONGO_URI=mongodb://username:password@mongo:27017/?authSource=admin
MONGO_DB_NAME=exmaple_db
```

3. Построить и запустить контейнеры:
```bash
  docker-compose up -d
```
📦 Версия приложения
v1.3

## 📜 История изменений (Changelog)

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

