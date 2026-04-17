## Tech Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| Queue Broker | RabbitMQ |
| Background Tasks | Celery |
| Auth | JWT (Access + Refresh Tokens) |
| Email | aiosmtplib / fastapi-mail |
| Runtime | Python 3.13 + uv |
| Container | Docker + Docker Compose |

---

## Project Structure

```
app/
├── api/             # Route handlers (admin, user, event, booking)
├── core/            # Config and JWT security helpers
├── db/              # MongoDB connection and Redis cache
├── dependencies/    # Auth guards (get_current_user, RBAC)
├── middleware/      # Request logging middleware
├── models/          # Data models
├── queue/           # Celery app and background tasks
├── repositories/    # Database query layer
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic
└── utils/           # Email utilities
tests/               # Unit tests
```

---

## Setup & Run

### With Docker

```bash
git clone https://github.com/yash-gorasia-python-ak/task-automation-system.git
cd task-automation-system

# Start everything (API + PostgreSQl + Redis + RabbitMQ + Celery worker)
docker compose up --build
```

API will be available at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

---

## Environment Variables

Create a `.env` file in the root directory:

```env
# ---------------- DATABASE ----------------
DB_URL=postgresql+asyncpg://postgres:postgres@db:5432/task_automation_system
TEST_DB_URL=postgresql+asyncpg://postgres:postgres@test_db:5432/test_task_automation_system

CELERY_DB_URL=postgresql://postgres:postgres@db:5432/task_automation_system
TEST_CELERY_DB_URL=postgresql://postgres:postgres@test_db:5432/test_task_automation_system

# ---------------- AUTH ----------------
ACCESS_SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
REFRESH_SECRET_KEY=b7a9563b93f7099f6f0f4caa6cf63b88e8d3e709d25e094faa6ca2556c818166

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=2

# ---------------- MAIL ----------------
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=MyApp

MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
VALIDATE_CERTS=True

# ---------------- REDIS ----------------
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# ----------------RABBITMQ-------------
RABBITMQ_URL=pyamqp://guest:guest@rabbitmq:5672//

# ---------------- APP ----------------
DOMAIN=0.0.0.0:8080

```

---

## API Endpoints

### Auth / User

All routes are prefixed with `/auth`.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | No | Register a new user |
| POST | `/login` | No | Login and get tokens |
| POST | `/refresh` | No | Refresh access token |
| POST | `/logout` | Yes | Logout and delete refresh token from cookie |

### Task

All routes are prefixed with `/tasks`.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/` | Yes | create new task |
| GET | `/` | Yes | Get all tasks |
| GET | `/{task_id}` | Yes | Get task by ID |
| DELETE | `/{task_id}` | Yes | Delete task by ID |

---
.

## Key Features

### **1. Dynamic Task Scheduling**
*   **Flexible Schedule Types**: Supports multiple scheduling strategies via `sqlalchemy-celery-beat`:
    *   **Reminders**: One-off tasks using `ClockedSchedule`.
    *   **System Checks**: Recurring tasks using `IntervalSchedule`.
    *   **Daily Automations**: Calendar-based tasks using `CrontabSchedule`.
*   **Dynamic Lifecycle**: Tasks can be created, retrieved, triggered, and deleted via API. Deleting a task automatically cleans up its associated Celery Beat schedule.

### **2. Automated Service Workers**
*   **Comic Service**: Integration with the XKCD API to fetch and email random comics.
*   **System Health**: Monitors disk usage using `shutil` and logs health data directly into task metadata.
*   **Reminder Engine**: Asynchronous mail notifications for user-defined reminders.

---

## Running Tests

```bash
uv run pytest
```

With coverage report:

```bash
uv run pytest --cov
```

Tests are organized to mirror the app structure:
- `test_auth_*` — user registration, login, token refresh
- `test_task_*` — task read and delete operation
