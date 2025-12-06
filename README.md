# Syrano Backend (syrano-be)

Backend API for **Syrano**, a Korean RizzGPT-style assistant that generates attractive and context-aware chat messages.
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
- **Infra (planned):** DigitalOcean (App Platform or Droplet)

---

## 📁 Project Structure

```bash
syrano/
  app/
    main.py                  # FastAPI entrypoint (lifespan, CORS, router wiring)
    db.py                    # Database engine/session/init
    models/                  # SQLAlchemy models
      __init__.py
      base.py                # Base + common helpers
      user.py                # User entity
      subscription.py        # Subscription entity (User 1:1)
      message_history.py     # MessageHistory entity (table ready, not used in MVP)
    routers/
      auth.py                # /auth endpoints (anonymous, subscription status)
      billing.py             # /billing endpoints (premium activation)
      rizz.py                # /rizz endpoints (message generation)
    services/
      config.py              # Environment config loader (.env / os.environ)
      llm.py                 # LangChain + OpenAI LLM handler
      users.py               # User-related helpers
      subscriptions.py       # Subscription-related helpers
  .env                       # Environment variables (ignored by Git)
  pyproject.toml             # PDM configuration
  .gitignore
  README.md
```

---

## 🔧 Environment Variables

Create a `.env` file in the project root **for local development**:

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

> `.env` is already included in `.gitignore`.

In production (DigitalOcean etc.), these should be configured as **environment variables** in the platform, not via `.env` committed to the repo.

---

## 🐳 Running PostgreSQL via Docker

Create and start a persistent PostgreSQL container (first time only):

```bash
docker run --name syrano-postgres   -e POSTGRES_USER=syrano   -e POSTGRES_PASSWORD=syrano   -e POSTGRES_DB=syrano   -p 5432:5432   -v syrano_pgdata:/var/lib/postgresql/data   -d postgres:16
```

Useful commands:

```bash
# Start/stop container
docker start syrano-postgres
docker stop syrano-postgres

# Check container status
docker ps

# Connect to the DB
docker exec -it syrano-postgres psql -U syrano -d syrano
```

Check tables:

```sql
\dt
```

Expected:

```text
 Schema |      Name       | Type  | Owner
--------+-----------------+-------+--------
 public | users           | table | syrano
 public | subscriptions   | table | syrano
 public | message_history | table | syrano
```

---

## 🗄️ Database Schema

### `users`

| Column     | Type        | Description        |
|-----------|-------------|--------------------|
| id        | VARCHAR(36) | Primary key (UUID) |
| created_at| TIMESTAMPTZ | Creation time      |

---

### `subscriptions` (User 1:1 Subscription)

| Column     | Type        | Description                                  |
|-----------|-------------|----------------------------------------------|
| id        | VARCHAR(36) | Primary key                                  |
| user_id   | VARCHAR(36) | FK → users.id, UNIQUE (enforces 1:1)         |
| is_premium| BOOLEAN     | Premium status                               |
| plan_type | VARCHAR(32) | e.g., "weekly", "monthly"                    |
| expires_at| TIMESTAMPTZ | Subscription expiration time                 |
| created_at| TIMESTAMPTZ | Row creation time                            |

> For MVP, `weekly` and `monthly` are interpreted as **7 days** and **30 days** from activation.
> The UI should label these as e.g. “7-day pass”, “30-day pass” to match behavior.

---

### `message_history` (Prepared for future use)

| Column       | Type        | Description                                   |
|--------------|-------------|-----------------------------------------------|
| id           | VARCHAR(36) | Primary key                                   |
| user_id      | VARCHAR(36) | FK → users.id                                 |
| conversation | TEXT        | Input conversation text                       |
| suggestions  | JSONB       | Generated suggestions (e.g. {"items":[...]}) |
| created_at   | TIMESTAMPTZ | Creation time                                 |

> MVP: table exists but is not yet populated.  
> Future: history, analytics, usage limits.

---

## ▶️ Running the API (Local)

### 1. Install dependencies

```bash
pdm install
```

### 2. Start the database

```bash
docker start syrano-postgres
```

### 3. Run the dev server

Using PDM script:

```bash
pdm run dev
```

(Equivalent to `uvicorn app.main:app --reload`.)

On startup you should see:

```text
INFO:syrano:Initializing database...
INFO:syrano:Database initialized.
INFO:     Application startup complete.
```

Health check:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

---

## 🌐 CORS Configuration

CORS is enabled in `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Syrano API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development: allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- **Native Flutter apps (Android/iOS)** do **not** require CORS.
- CORS mainly affects **browser-based clients (Flutter Web, SPA, etc.)**.
- For production, `allow_origins` should be replaced with the actual frontend origins,  
  e.g. `["https://syrano.app"]`.

---

## 💬 Core APIs

### 1) `POST /auth/anonymous` – Anonymous User Provisioning

Create (or reuse) an anonymous user and ensure a default subscription exists.

**Request**

```bash
curl -X POST "http://127.0.0.1:8000/auth/anonymous"   -H "Content-Type: application/json"   -d '{}'
```

Optionally, an existing `user_id` can be passed:

```json
{
  "user_id": "existing-user-id"
}
```

**Response**

```json
{
  "user_id": "cdcbad1a-d960-48f3-961a-5b08ae87ad60",
  "is_premium": false
}
```

- Creates a new `User` row if `user_id` is not provided or not found.
- Ensures a corresponding `Subscription` row exists with `is_premium=false`.

---

### 2) `GET /auth/me/subscription` – Subscription Status

Retrieve the current subscription status for a given user.

**Request**

```bash
curl "http://127.0.0.1:8000/auth/me/subscription?user_id=USER_ID"
```

**Response**

```json
{
  "user_id": "0653a764-b671-4334-8daa-685b060f2b6e",
  "is_premium": false,
  "plan_type": null,
  "expires_at": null
}
```

After activation, for example:

```json
{
  "user_id": "0653a764-b671-4334-8daa-685b060f2b6e",
  "is_premium": true,
  "plan_type": "monthly",
  "expires_at": "2026-01-05T01:53:28.326837Z"
}
```

---

### 3) `POST /billing/subscribe` – Premium Activation (MVP)

Activate a premium subscription for a user.  
**This is MVP logic**: no real app store receipt validation yet, just a simple switch in the DB.

**Request**

```bash
curl -X POST "http://127.0.0.1:8000/billing/subscribe"   -H "Content-Type: application/json"   -d '{
    "user_id": "0653a764-b671-4334-8daa-685b060f2b6e",
    "plan_type": "monthly"
  }'
```

`plan_type`:

- `"weekly"` → 7 days from now
- `"monthly"` → 30 days from now

**Response**

```json
{
  "user_id": "0653a764-b671-4334-8daa-685b060f2b6e",
  "is_premium": true,
  "plan_type": "monthly",
  "expires_at": "2026-01-05T01:53:28.326837Z"
}
```

After this, `GET /auth/me/subscription` will reflect the updated premium status.

---

### 4) `POST /rizz/generate` – Rizz Message Generation

Generate attractive, context-aware reply suggestions based on the conversation.

**Important:**  
- `user_id` is **required**.
- Premium vs Free is determined **on the server**, using `Subscription.is_premium`.

**Request**

```bash
curl -X POST "http://127.0.0.1:8000/rizz/generate"   -H "Content-Type: application/json"   -d '{
    "mode": "conversation",
    "conversation": "어제 소개팅 하고 오늘 첫 연락 보내려는데 뭐라고 해야 할지 모르겠어",
    "platform": "kakao",
    "relationship": "first_meet",
    "style": "banmal",
    "tone": "friendly",
    "num_suggestions": 3,
    "user_id": "cdcbad1a-d960-48f3-961a-5b08ae87ad60"
  }'
```

**Response (example)**

```json
{
  "suggestions": [
    "어제 이야기 재밌었어! 오늘 하루는 어땠어?",
    "나 어제 너랑 얘기하면서 시간 가는 줄 몰랐어. 또 연락할게!",
    "잘 자고 일어나서 기분 좋은 하루 보내길 바랄게!"
  ]
}
```

**Internal flow:**

1. Look up `Subscription` by `user_id`.
2. If not found → `404` (client should call `/auth/anonymous` first).
3. Decide `is_premium` from DB.
4. Select appropriate LLM model:
   - Standard model for free users
   - Premium model for paying users
5. Build a Korean “Rizz assistant” prompt and call OpenAI via LangChain.
6. Parse response into a list of suggestions.

---

## 🧠 LLM Handling

Implemented in `app/services/llm.py`:

- Uses `ChatOpenAI` with models from env:
  - `OPENAI_STANDARD_MODEL`
  - `OPENAI_PREMIUM_MODEL`
- System prompt describes a Korean dating assistant (시라노 스타일).
- User/context prompt includes:
  - Conversation text
  - Platform, relationship, style, tone, num_suggestions
- Output is split into multiple suggestion lines.

---

## ✅ Current MVP Status

As of now, the backend supports:

- Anonymous user provisioning
  - `POST /auth/anonymous`
- Subscription lookup
  - `GET /auth/me/subscription`
- Premium upgrade (MVP implementation: simple DB switch)
  - `POST /billing/subscribe`
- Rizz message generation
  - `POST /rizz/generate` (uses `user_id` + subscription status)
- Database schema ready for future message history
  - `message_history` table exists
- CORS enabled for development
- Dockerized Postgres with persistent volume

This is sufficient for:

- **Free tier**
  - Ads controlled by frontend via `is_premium=false`
  - Standard LLM model
- **Premium tier**
  - Ads removed (frontend responsibility)
  - Optionally better LLM model, more suggestions, relaxed limits

Future work:

- Persist message history into `message_history` in `/rizz/generate`
- Free-tier daily limits based on history/usage
- Real payment integration and receipt validation
- Production-grade CORS origin restrictions
- Deployment to DigitalOcean with HTTPS (App Platform recommended for simplicity)

---

## 📄 License

MIT
