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
      profile.py             # Profile entity (User 1:N) ✅ NEW
      message_history.py     # MessageHistory entity (table ready, not used in MVP)
    routers/
      auth.py                # /auth endpoints (anonymous, subscription status)
      billing.py             # /billing endpoints (premium activation)
      profiles.py            # /profiles endpoints (CRUD) ✅ NEW
      rizz.py                # /rizz endpoints (text & image-based message generation)
    services/
      llm.py                 # LangChain + OpenAI LLM handler
      users.py               # User-related helpers
      subscriptions.py       # Subscription-related helpers
      profiles.py            # Profile-related helpers ✅ NEW
      ocr/                   # OCR service (Protocol pattern)
        __init__.py          # Empty
        base.py              # OCRService Protocol
        naver.py             # NaverOCRService implementation
    prompts/                 # Prompt templates ✅ NEW
      __init__.py
      rizz.py                # Rizz prompt builders (system & user prompts)
    schemas/
      rizz.py                # Rizz Request/Response DTOs
      profile.py             # Profile Request/Response DTOs ✅ NEW
  docs/
    ocr-integration.md       # OCR 통합 과정 문서
  temp_images/               # Temporary image storage (gitignored) ✅ NEW
  .env                       # Environment variables (ignored by Git)
  pyproject.toml             # PDM configuration
  Dockerfile                 # Docker build configuration
  .gitignore
  README.md
  TODO.md
  DATABASE.md                # Database schema documentation ✅ NEW
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

### `profiles` (User 1:N Profile) ✅ NEW
| Column     | Type        | Description                                  |
|-----------|-------------|----------------------------------------------|
| id        | VARCHAR(36) | Primary key                                  |
| user_id   | VARCHAR(36) | FK → users.id (CASCADE DELETE)               |
| name      | VARCHAR(100)| Profile name (required)                      |
| age       | INTEGER     | Age (optional)                               |
| gender    | VARCHAR(10) | Gender (optional)                            |
| memo      | TEXT        | Memo/notes (optional)                        |
| created_at| TIMESTAMPTZ | Creation time                                |
| updated_at| TIMESTAMPTZ | Last update time                             |

> Each user can have multiple profiles (e.g., girlfriend, date, friend).
> Profiles are used to personalize LLM prompts with context about the chat partner.

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

Create a new anonymous user with default subscription.

**Request**
```bash
curl -X POST "http://127.0.0.1:8000/auth/anonymous" \
  -H "Content-Type: application/json"
```

**Response**
```json
{
  "user_id": "cdcbad1a-d960-48f3-961a-5b08ae87ad60",
  "is_premium": false
}
```

- Always creates a **new** `User` row
- Creates a corresponding `Subscription` row with `is_premium=false`
- For existing users, use `GET /auth/me/subscription` instead

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

After premium activation:
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

### 5) `POST /rizz/analyze-image` – Image-Based Message Generation (Profile-based) ✅ Updated

Generate reply suggestions by extracting text from a chat screenshot using **Naver Clova OCR** and applying **Profile information** for personalized responses.

**Request (multipart/form-data)**
```bash
curl -X POST "http://127.0.0.1:8000/rizz/analyze-image" \
  -F "image=@screenshot.png" \
  -F "user_id=c65116c4-7703-434e-a859-320961b6320b" \
  -F "profile_id=c148fba1-7da1-43f0-a334-51be9c96ccef" \
  -F "num_suggestions=3"
```

**Parameters:**
- `image`: Chat screenshot (required)
- `user_id`: User ID (required)
- `profile_id`: Chat partner's profile ID (required) ✅ **NEW**
- `num_suggestions`: Number of suggestions (default: 3, range: 1-5)

**Response**
```json
{
  "suggestions": [
    "집에 오니 편안하죠? 요즘 서울에서 가장 가보고 싶은 곳 있어요?",
    "프리한 시간 보내고 있다니 부럽네요! 주로 어떤 취미로 시간을 보내세요?",
    "저녁 먹고 집에 오면 하루가 마무리된 느낌인데, 밍밍님은 하루 중 가장 좋아하는 시간이 언제인가요?"
  ],
  "usage_info": {
    "remaining": 4,
    "limit": 5,
    "is_premium": false
  }
}
```

**Usage Info:**
- `remaining`: 오늘 남은 사용 횟수 (-1: 무제한)
- `limit`: 일일 제한 횟수 (-1: 무제한)
- `is_premium`: 프리미엄 여부
```

### 6) Profile CRUD APIs 

#### a) `POST /profiles` – Create Profile

Create a new profile for a user.

**Request**
```bash
curl -X POST "http://127.0.0.1:8000/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "name": "여자친구",
    "age": 25,
    "gender": "여성",
    "memo": "영화 좋아함, 유머 센스 있음"
  }'
```

**Response**
```json
{
  "id": "profile-456",
  "user_id": "user-123",
  "name": "여자친구",
  "age": 25,
  "gender": "여성",
  "memo": "영화 좋아함, 유머 센스 있음",
  "created_at": "2025-12-25T...",
  "updated_at": "2025-12-25T..."
}
```

---

#### b) `GET /profiles?user_id=xxx` – List Profiles

Get all profiles for a user (sorted by newest first).

**Request**
```bash
curl "http://127.0.0.1:8000/profiles?user_id=user-123"
```

**Response**
```json
{
  "profiles": [
    {
      "id": "profile-456",
      "name": "여자친구",
      ...
    },
    {
      "id": "profile-789",
      "name": "소개팅 상대",
      ...
    }
  ]
}
```

---

#### c) `GET /profiles/{profile_id}` – Get Profile

Retrieve a specific profile by ID.

**Request**
```bash
curl "http://127.0.0.1:8000/profiles/profile-456"
```

**Response**
```json
{
  "id": "profile-456",
  "user_id": "user-123",
  "name": "여자친구",
  ...
}
```

---

#### d) `PUT /profiles/{profile_id}` – Update Profile

Update specific fields of a profile (partial update supported).

**Request**
```bash
curl -X PUT "http://127.0.0.1:8000/profiles/profile-456" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 26,
    "memo": "영화와 음악 좋아함"
  }'
```

**Response**
```json
{
  "id": "profile-456",
  "name": "여자친구",
  "age": 26,
  "memo": "영화와 음악 좋아함",
  "updated_at": "2025-12-25T..." // ✅ auto-updated
}
```

---

#### e) `DELETE /profiles/{profile_id}` – Delete Profile

Delete a profile (returns 204 No Content).

**Request**
```bash
curl -X DELETE "http://127.0.0.1:8000/profiles/profile-456"
```

**Response**
```
(No content, 204 status)
```

---

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

- Anonymous user provisioning (`POST /auth/anonymous`) ✅ Simplified
- Subscription lookup (`GET /auth/me/subscription`)
- Premium upgrade - MVP implementation (`POST /billing/subscribe`)
- **Daily usage limit** (5/day free, unlimited premium) ✅ **NEW**
- **Text-based message generation** (`POST /rizz/generate`)
- **Image-based message generation with Profile** (`POST /rizz/analyze-image`)
- **Profile CRUD** (`/profiles` endpoints)
- **Prompt separation** (`app/prompts/rizz.py`)
- **Usage info in response** (remaining, limit, is_premium) ✅ **NEW**
- Database schema ready for future message history
- CORS enabled for development
- Dockerized Postgres with persistent volume
- **OCR service with Protocol pattern**

This is sufficient for:

- **Free tier**
  - 5 requests/day with usage tracking ✅ **NEW**
  - Ads controlled by frontend via `is_premium=false`
  - Standard LLM model (gpt-4o-mini)
  - OCR-powered screenshot analysis
  - Multiple profiles per user
  - Usage info returned in every response
- **Premium tier**
  - Unlimited requests (`remaining: -1`) ✅ **NEW**
  - Ads removed (frontend responsibility)
  - Premium LLM model (gpt-4o)
  - All free tier features

Future work:

- ~~**Profile-based personalization in `/rizz/analyze-image`**~~ ✅ **Completed**
- Persist message history into `message_history` in `/rizz/generate`
- Free-tier daily limits based on history/usage
- Real payment integration and receipt validation
- Production-grade CORS origin restrictions
- Prompt A/B testing and optimization

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