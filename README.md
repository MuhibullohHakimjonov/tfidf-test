# TFIDF Project

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




---

## ▶️ Запуск приложения

### Зависимости

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Шаги запуска

1. **Склонируйте репозиторий**
   ```bash
   git clone <URL-репозитория>
   cd <название-папки-проекта>




