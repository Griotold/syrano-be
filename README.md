# Syrano Backend (syrano-be)

Backend API for **Syrano**, a Korean RizzGPT-style service that generates attractive and context-aware chat messages.  
Built with **FastAPI**, **SQLAlchemy (async)**, **LangChain**, and **PostgreSQL**.

---

## 📦 Tech Stack

- **Language:** Python 3.12  
- **Framework:** FastAPI  
- **Package Manager:** PDM  
- **ORM:** SQLAlchemy 2.0 (Async)  
- **Database:** PostgreSQL (Docker)  
- **LLM Provider:** OpenAI (via `langchain-openai`)  
- **Config:** python-dotenv  

---

## 📁 Project Structure

```
syrano/
  app/
    main.py                  # FastAPI entrypoint
    db.py                    # Database engine/session/init
    models/                  # SQLAlchemy models (User, Subscription, MessageHistory)
      __init__.py
      base.py
      user.py
      subscription.py
      message_history.py
    routers/
      rizz.py                # /rizz/generate endpoint
    services/
      config.py              # Environment config loader
      llm.py                 # LangChain + OpenAI LLM handler
  .env                       # Environment variables (ignored by Git)
  pyproject.toml             # PDM configuration
  .gitignore
```

---

## 🔧 Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_STANDARD_MODEL=gpt-4.1-mini
OPENAI_PREMIUM_MODEL=gpt-4.1

# Database
DATABASE_URL=postgresql+asyncpg://syrano:syrano@localhost:5432/syrano

# SQLAlchemy debug logging (development only)
SQLALCHEMY_ECHO=true
```

Note: `.env` is already included in `.gitignore`.

---

## 🐳 Running PostgreSQL via Docker

Create and start a persistent PostgreSQL container:

```bash
docker run --name syrano-postgres   -e POSTGRES_USER=syrano   -e POSTGRES_PASSWORD=syrano   -e POSTGRES_DB=syrano   -p 5432:5432   -v syrano_pgdata:/var/lib/postgresql/data   -d postgres:16
```

Check container status:

```bash
docker ps
```

Connect to PostgreSQL:

```bash
docker exec -it syrano-postgres psql -U syrano -d syrano
```

View tables:

```sql
\dt
```

Expected result:

```
 Schema |      Name       | Type  | Owner
--------+-----------------+-------+--------
 public | users           | table | syrano
 public | subscriptions   | table | syrano
 public | message_history | table | syrano
```

---

## 🗄️ Database Schema Overview

### **users**
| Column     | Type        | Description        |
|------------|-------------|--------------------|
| id         | VARCHAR(36) | Primary key (UUID) |
| created_at | TIMESTAMPTZ | Creation time      |

### **subscriptions** (1:1 relationship with User)
| Column     | Type        | Description                                  |
|------------|-------------|----------------------------------------------|
| id         | VARCHAR(36) | Primary key                                  |
| user_id    | VARCHAR(36) | FK → users.id, UNIQUE (enforces 1:1)         |
| is_premium | BOOLEAN     | Premium status                               |
| plan_type  | VARCHAR(32) | e.g., "weekly", "monthly"                    |
| expires_at | TIMESTAMPTZ | Subscription expiration                      |
| created_at | TIMESTAMPTZ | Row creation time                            |

### **message_history** (not used in MVP, table only)
| Column       | Type        | Description               |
|--------------|-------------|---------------------------|
| id           | VARCHAR(36) | Primary key               |
| user_id      | VARCHAR(36) | FK → users.id             |
| conversation | TEXT        | Input conversation        |
| suggestions  | JSONB       | Generated LLM suggestions |
| created_at   | TIMESTAMPTZ | Creation time             |

---

## ▶️ Running the API

Start the API server:

```bash
pdm run uvicorn app.main:app --reload
```

Expected startup log:

```
INFO:syrano:Initializing database...
INFO:syrano:Database initialized.
INFO:     Application startup complete.
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

---

## 💬 Rizz Generation API

### Endpoint  
`POST /rizz/generate`

### Example Request

```json
{
  "mode": "conversation",
  "conversation": "어제 소개팅 하고 오늘 첫 연락 보내려는데 뭐라고 해야 할지 모르겠어",
  "platform": "kakao",
  "relationship": "first_meet",
  "style": "banmal",
  "tone": "friendly",
  "num_suggestions": 3,
  "is_premium": false,
  "user_id": null
}
```

### Example Response

```json
{
  "suggestions": [
    "어제 즐거웠어! 오늘 하루 어땠어?",
    "안녕! 어제 만나서 반가웠어, 오늘도 좋은 하루 보내~",
    "어제 얘기한 거 생각나서 연락했어, 잘 지내?"
  ]
}
```

---

## 🧠 LLM Processing

Located in: `app/services/llm.py`

- Uses OpenAI via `ChatOpenAI`
- Constructs a structured system prompt
- Generates multiple suggestions
- Splits LLM output into list form (line-based)

---

## ✔️ Completed Work (current)

- Python + PDM project initialization  
- FastAPI setup (`/health`)  
- `/rizz/generate` implemented and connected to LLM  
- Logging & exception handling added  
- PostgreSQL (Docker) integrated  
- SQLAlchemy async setup completed  
- Database schema created:
  - `users`
  - `subscriptions`
  - `message_history`  
- Automatic DB initialization via `init_db()` on startup  
- LLM working with both standard/premium model selection  

---

## 🔜 Next Steps

### 1. User Identity
- Implement `/auth/anonymous`
  - Create a new `User` row
  - Return `user_id`
  - Store `user_id` on the client (Flutter app)

### 2. Subscription Integration
- `GET /me/subscription` (current subscription status by user_id)
- `POST /billing/subscribe` (apply in-app purchase result to backend)
- Use `subscriptions` table to manage:
  - `is_premium`
  - `expires_at`
  - `plan_type`

### 3. Apply user_id to /rizz/generate
- Require `user_id` in requests
- Look up subscription by `user_id`
- Select model / limit usage based on subscription

### 4. Message History (later)
- Save each `/rizz/generate` call to `message_history`
- Provide a history API (e.g. recent messages)
- Potential analytics/statistics in the future

---

## 📄 License

MIT
