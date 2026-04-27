🚀 Messenger App Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-000000?style=for-the-badge&logo=socket.io&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pytest](https://img.shields.io/badge/Pytest-38%20tests-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)

Полностью асинхронный backend для мессенджера реального времени.  
Мгновенная доставка сообщений через WebSocket, шифрование Fernet, JWT-аутентификация, Docker.

---

## 🔥 Особенности

- ⚡ **WebSocket-чат** — обмен сообщениями в реальном времени без задержек
- 🔐 **Шифрование Fernet** — сообщения шифруются на клиенте, сервер хранит только хэш
- 🔑 **JWT-авторизация** — защита HTTP и WebSocket-эндпоинтов
- 🗄️ **Асинхронная БД** — PostgreSQL + asyncpg + SQLAlchemy 2.0
- 📡 **Broadcast** — мгновенная рассылка новых сообщений всем участникам чата
- 🐳 **Docker** — всё окружение одной командой
- ✅ **38 тестов** — pytest + httpx + WebSocket

---

## 🛠 Технологический стек

| Слой | Инструменты |
|------|-------------|
| **Фреймворк** | FastAPI, WebSocket, Pydantic |
| **База данных** | PostgreSQL + asyncpg + SQLAlchemy 2.0 (async) |
| **Миграции** | Alembic |
| **Безопасность** | JWT (access + refresh), Fernet (cryptography) |
| **Тестирование** | pytest, httpx, WebSocket-тесты |
| **Деплой** | Docker, Docker Compose |

---

## 📁 Структура проекта

```
backend/
├── app/
│   ├── api/              # Роутеры (HTTP + WebSocket)
│   ├── core/             # Конфиги, безопасность, БД, WebSocket-менеджер
│   ├── models/           # SQLAlchemy-модели
│   ├── repositories/     # Паттерн Repository
│   ├── services/         # Бизнес-логика
│   ├── schemas/          # Pydantic-схемы
│   └── tests/            # 38 unit-тестов
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Быстрый старт
### 1. Клонирование
```
git clone <repo-url>
cd messenger-backend
```

### 2. Настройка окружения
Создайте `.env` файл:
```
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/messenger
SECRET_KEY=your-secret-key
```

### 3. Запуск через Docker
```
docker-compose up -d
```

Сервер доступен на `http://localhost:8000`.

### 4. Тесты
```
docker-compose exec backend pytest -v
```
```
tests/test_messages.py::test_send_message PASSED
tests/test_messages.py::test_websocket_chat PASSED
...
✅ 38 passed
```

---

## 🔌 WebSocket

Подключение после получения JWT-токена:
```
const ws = new WebSocket("ws://localhost:8000/api/messages/ws/1?token=<JWT>");
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

**Формат отправки:**
```
{
  "type": "message",
  "chat_id": 1,
  "text": "encrypted_message"
}
```

**Broadcast-уведомление:**
```
{
  "type": "new_message",
  "message": {
    "id": 1,
    "chat_id": 1,
    "sender_id": 1,
    "text": "encrypted_hash",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

---

## 📡 REST API

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/api/messages/` | Отправить сообщение |
| `GET` | `/api/messages/{chat_id}` | История чата (пагинация) |
| `DELETE` | `/api/messages/{message_id}` | Удалить сообщение |

Swagger UI: [`http://localhost:8000/docs`](http://localhost:8000/docs)

---

## 🔐 Безопасность

- **JWT** — защита HTTP и WebSocket
- **Проверка токена в WebSocket** — невалидный токен → разрыв соединения
- **Fernet** — симметричное шифрование, ключ генерируется на клиенте
- **Изоляция чатов** — нельзя читать/писать в чужие диалоги

---

## 👤 Автор
GitHub: https://github.com/FirstAgain27
