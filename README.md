# Credit Analyst AI Workspace

Production-ready full-stack application for credit analysts:

1. **Policy Q&A** — RAG-powered chat over your credit policy manual with section citations
2. **Payment Reminders** — Bulk AI-generated WhatsApp/SMS reminders for due and overdue borrowers

> **Desktop app:** see [`desktop/`](./desktop/README.md) for the Electron version —
> same functionality, local SQLite storage, upgraded RAG (heading-aware chunking,
> page citations, hybrid retrieval, conversation history).

## Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS, Zustand, TanStack Query
- **Backend:** FastAPI, SQLAlchemy (async), PostgreSQL + pgvector
- **AI (testing):** Google Gemini free tier — chat + embeddings (one API key)
- **AI (production):** Claude + OpenAI — switch via `AI_PROVIDER` / `EMBEDDING_PROVIDER`
- **Notifications:** Twilio WhatsApp/SMS

## Quick Start (Docker)

```bash
cp .env.example .env
# Add your free GEMINI_API_KEY from https://aistudio.google.com/apikey

docker compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| analyst@bank.pk | analyst123 | analyst |
| admin@bank.pk | admin123 | admin |

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Requires PostgreSQL with pgvector on localhost:5432
set DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/credit_analyst
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Features

### Policy Assistant
- Ask questions about the credit policy document
- Retrieves relevant chunks via pgvector cosine similarity
- Gemini (testing) or Claude/OpenAI (production) generates answers with section citations

### Payment Reminders
- Dashboard of borrowers due today, soon (≤3 days), or overdue
- AI-generated bilingual (Urdu-English) reminder messages
- Bulk send via Twilio (simulated when credentials are not configured)
- Per-borrower send progress tracking

### Policy Upload (Admin)
- Upload PDF to replace and re-embed the policy manual

## Environment Variables

See `.env.example` for all required variables.

### Testing (free — default)

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Free key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `AI_PROVIDER` | `gemini` (default) |
| `EMBEDDING_PROVIDER` | `gemini` (default) |

One Gemini key powers policy Q&A, reminder text generation, and RAG embeddings.

### Production (paid)

```env
AI_PROVIDER=anthropic
EMBEDDING_PROVIDER=openai
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### Optional
- Twilio credentials — Optional; reminders are simulated without them

## Production

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

## Online demo (4–5 users, free)

Use **Neon + Render + Netlify** (see [DEPLOY-FREE.md](./DEPLOY-FREE.md)).

1. Push to GitHub (CI runs on every push via `.github/workflows/ci.yml`)
2. Neon: Postgres + `CREATE EXTENSION vector`
3. Render: deploy `backend/` with env vars from `.env.example`
4. Netlify: deploy `frontend/` with `VITE_API_BASE_URL` and `VITE_DEMO_MODE=false`
5. Set Render `CORS_ORIGINS` to your Netlify URL

## Policy PDF storage

- Upload PDF in **Policy** tab → **Replace PDF**
- File bytes are stored in `policy_documents`
- Text is chunked into `policy_chunks` with embeddings for retrieval
- Chat answers use RAG over the active document

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/login | Sign in |
| POST | /policy/ask | Policy Q&A |
| POST | /policy/upload | Upload policy PDF (admin) |
| GET | /borrowers/due | Due/overdue borrowers |
| POST | /reminders/preview | Preview reminder message |
| POST | /reminders/send | Send bulk reminders |
| GET | /health | Health check |

## License

Proprietary — internal use.
