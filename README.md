# Syrano Backend (syrano-be)

Backend API for **Syrano**, a Korean RizzGPT-style assistant that generates attractive and context-aware chat messages.
Built with **FastAPI**, **SQLAlchemy (async)**, **LangChain**, **Naver Clova OCR**, and **PostgreSQL**.

---

## 📦 Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Package Manager:** PDM
- **ORM:** SQLAlchemy 2.0 (Async)
- **Database:** PostgreSQL (Docker)
- **LLM Provider:** OpenAI (via `langchain-openai`)
- **OCR Provider:** Naver Clova OCR (General OCR, Premium)
- **Config:** python-dotenv
- **Infra:** DigitalOcean App Platform

---

## 📁 Project Structure

```bash
syrano/
  app/
    main.py                  # FastAPI entrypoint (lifespan, CORS, router wiring)
    config.py                # Environment config loader (.env / os.environ)
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
      rizz.py                # /rizz endpoints (text & image-based message generation)
    services/
      llm.py                 # LangChain + OpenAI LLM handler
      users.py               # User-related helpers
      subscriptions.py       # Subscription-related helpers
      ocr/                   # OCR service (Protocol pattern)
        __init__.py          # Empty
        base.py              # OCRService Protocol
        naver.py             # NaverOCRService implementation
    schemas/
      rizz.py                # Request/Response DTOs
  docs/
    ocr-integration.md       # OCR 통합 과정 문서
  .env                       # Environment variables (ignored by Git)
  pyproject.toml             # PDM configuration
  Dockerfile                 # Docker build configuration
  .gitignore
  README.md
```

---

## 🔧 Environment Variables

Create a `.env` file in the project root **for local development**:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_STANDARD_MODEL=gpt-4o-mini
OPENAI_PREMIUM_MODEL=gpt-4o

# Database
DATABASE_URL=postgresql+asyncpg://syrano:syrano@localhost:5432/syrano

# Naver Clova OCR
NAVER_OCR_SECRET_KEY=xxxxx
NAVER_OCR_INVOKE_URL=https://xxxxx.apigw.ntruss.com/custom/v1/.../general

# SQLAlchemy debug logging (development only)
SQLALCHEMY_ECHO=true
```

> `.env` is already included in `.gitignore`.

In production (DigitalOcean), these should be configured as **App-Level Environment Variables**.

---

## 🐳 Running PostgreSQL via Docker

Create and start a persistent PostgreSQL container (first time only):

```bash
docker run --name syrano-postgres \
  -e POSTGRES_USER=syrano \
  -e POSTGRES_PASSWORD=syrano \
  -e POSTGRES_DB=syrano \
  -p 5432:5432 \
  -v syrano_pgdata:/var/lib/postgresql/data \
  -d postgres:16
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
> The UI should label these as e.g. "7-day pass", "30-day pass" to match behavior.

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
curl -X POST "http://127.0.0.1:8000/auth/anonymous" \
  -H "Content-Type: application/json" \
  -d '{}'
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
curl -X POST "http://127.0.0.1:8000/billing/subscribe" \
  -H "Content-Type: application/json" \
  -d '{
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

### 4) `POST /rizz/generate` – Text-Based Message Generation

Generate attractive, context-aware reply suggestions based on conversation text.

**Important:**  
- `user_id` is **required**.
- Premium vs Free is determined **on the server**, using `Subscription.is_premium`.

**Request**

```bash
curl -X POST "http://127.0.0.1:8000/rizz/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": "어제 소개팅 하고 오늘 첫 연락 보내려는데 뭐라고 해야 할지 모르겠어",
    "platform": "kakao",
    "relationship": "first_meet",
    "style": "banmal",
    "tone": "friendly",
    "num_suggestions": 3,
    "user_id": "cdcbad1a-d960-48f3-961a-5b08ae87ad60"
  }'
```

**Response**

```json
{
  "suggestions": [
    "어제 이야기 재밌었어! 오늘 하루는 어땠어?",
    "나 어제 너랑 얘기하면서 시간 가는 줄 몰랐어. 또 연락할게!",
    "잘 자고 일어나서 기분 좋은 하루 보내길 바랄게!"
  ]
}
```

---

### 5) `POST /rizz/analyze-image` – Image-Based Message Generation (NEW)

Generate reply suggestions by extracting text from a chat screenshot using **Naver Clova OCR**.

**Request (multipart/form-data)**

```bash
curl -X POST "http://127.0.0.1:8000/rizz/analyze-image" \
  -F "image=@screenshot.png" \
  -F "user_id=cdcbad1a-d960-48f3-961a-5b08ae87ad60" \
  -F "platform=kakao" \
  -F "relationship=first_meet" \
  -F "style=banmal" \
  -F "tone=friendly" \
  -F "num_suggestions=3"
```

**Response**

```json
{
  "suggestions": [
    "나도 이제 좀 쉬려고 해, 오늘 하루 어땠어?",
    "저녁 맛있게 먹었어? 난 간단히 먹었어ㅎㅎ",
    "프리한 시간 진짜 좋지, 뭐하고 놀아?"
  ]
}
```

**Flow:**

1. Save uploaded image temporarily
2. Extract text using Naver Clova OCR (95%+ accuracy)
3. Generate suggestions via LLM
4. Delete temporary file
5. Return suggestions

**OCR Service Architecture (Protocol Pattern):**

```python
# app/services/ocr/base.py
class OCRService(Protocol):
    async def extract_text(self, image_path: str | Path) -> str:
        ...

# app/services/ocr/naver.py
class NaverOCRService:
    async def extract_text(self, image_path: str | Path) -> str:
        # Naver Clova OCR implementation
        ...
```

> See `docs/ocr-integration.md` for detailed OCR integration history and comparison.

---

## 🧠 LLM Handling

Implemented in `app/services/llm.py`:

- Uses `ChatOpenAI` with models from env:
  - `OPENAI_STANDARD_MODEL` (Free tier)
  - `OPENAI_PREMIUM_MODEL` (Premium tier)
- System prompt describes a Korean dating assistant (시라노 스타일).
- User/context prompt includes:
  - Conversation text
  - Platform, relationship, style, tone, num_suggestions
- Output is split into multiple suggestion lines.

---

## 🖼️ OCR Integration

### Naver Clova OCR (Selected)

**Why Naver Clova?**
- **Accuracy:** 95%+ on chat screenshots (vs 60-70% with PyTesseract)
- **Cost:** 100 requests/month free, ₩1/request after
- **Memory:** External API (0MB server memory)
- **Speed:** ~3 seconds per request

**Alternatives Tried:**
- **EasyOCR:** 90% accuracy, but requires 2GB RAM ($48/month server)
- **PyTesseract:** 60-70% accuracy, failed on complex chat UI

**Setup:**
1. Create Naver Cloud account
2. Enable CLOVA OCR (General OCR, Premium)
3. Create Domain
4. Auto-link API Gateway
5. Copy Secret Key + Invoke URL to `.env`

**Cost Estimate:**
- DAU 50 (500 requests/month): **Free**
- DAU 500 (5,000 requests/month): **~$3/month**
- Breakeven: ~30,000 requests/month (then self-hosted OCR becomes cheaper)

See `docs/ocr-integration.md` for full details.

---

## ✅ Current MVP Status

As of now, the backend supports:

- Anonymous user provisioning (`POST /auth/anonymous`)
- Subscription lookup (`GET /auth/me/subscription`)
- Premium upgrade - MVP implementation (`POST /billing/subscribe`)
- **Text-based message generation** (`POST /rizz/generate`)
- **Image-based message generation** (`POST /rizz/analyze-image`) ⭐ **NEW**
- Database schema ready for future message history
- CORS enabled for development
- Dockerized Postgres with persistent volume
- **OCR service with Protocol pattern** (easy to swap providers) ⭐ **NEW**

This is sufficient for:

- **Free tier**
  - Ads controlled by frontend via `is_premium=false`
  - Standard LLM model
  - OCR-powered screenshot analysis
- **Premium tier**
  - Ads removed (frontend responsibility)
  - Premium LLM model
  - More suggestions, relaxed limits

Future work:

- Persist message history into `message_history` in `/rizz/generate`
- Free-tier daily limits based on history/usage
- Real payment integration and receipt validation
- Production-grade CORS origin restrictions
- Profile-based personalization (name, age, MBTI, gender, memo)
- OCR prompt optimization

---

## 🚀 Deployment

**Platform:** DigitalOcean App Platform

**Current Plan:** 512MB RAM, 1 vCPU ($12/month)

**Configuration:**
- Environment variables set in App-Level settings
- Auto-deploy from `main` branch
- HTTPS enabled by default

**Database:** Managed PostgreSQL (DigitalOcean)

---

## 📄 License

MIT