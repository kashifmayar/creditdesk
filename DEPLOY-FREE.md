# Free deployment guide (test / demo)

Deploy the app for **$0** using free tiers:

| Service | Role | Free tier |
|---------|------|-----------|
| [Neon](https://neon.tech) | PostgreSQL + pgvector | 0.5 GB storage |
| [Render](https://render.com) | FastAPI backend | Free web service |
| [Netlify](https://netlify.com) | React frontend | Free static hosting |

Total time: ~15 minutes.

---

## Step 1: Database (Neon)

1. Sign up at https://neon.tech
2. Create a project → copy the **connection string**
3. Convert it for this app:

```
postgresql+asyncpg://USER:PASSWORD@HOST/DBNAME?ssl=require
```

Replace `postgresql://` with `postgresql+asyncpg://` and add `?ssl=require` at the end.

4. In Neon SQL editor, run (optional — app also runs this on startup):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Step 2: Backend (Render)

1. Sign up at https://render.com
2. **New → Blueprint** → connect GitHub repo `kashifmayar/creditdesk`
3. Or **New → Web Service** manually:
   - Root directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

4. Set environment variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Neon URL (`postgresql+asyncpg://...?ssl=require`) |
| `GEMINI_API_KEY` | From https://aistudio.google.com/apikey |
| `SECRET_KEY` | Any long random string |
| `AI_PROVIDER` | `gemini` |
| `EMBEDDING_PROVIDER` | `gemini` |
| `CORS_ORIGINS` | `https://YOUR-SITE.netlify.app` (set after Step 3) |

5. Deploy and wait ~5 min. Note your API URL, e.g.:

```
https://creditdesk-api.onrender.com
```

6. Test: `https://creditdesk-api.onrender.com/health` → `{"status":"ok"}`

> Free Render services **sleep after 15 min** — first load may take 30–60 seconds.

---

## Step 3: Frontend (Netlify)

1. Sign up at https://netlify.com
2. **Add new site → Import from Git** → select `kashifmayar/creditdesk`
3. Build settings (auto-detected from `netlify.toml`):
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`

4. **Environment variables** (Site settings → Environment variables):

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://creditdesk-api.onrender.com` (your Render URL) |

5. Deploy. Note your site URL, e.g.:

```
https://creditdesk.netlify.app
```

6. Go back to **Render** → update `CORS_ORIGINS` to your Netlify URL and redeploy.

---

## Step 4: Test the app

1. Open your Netlify URL
2. Login: `analyst@bank.pk` / `analyst123`
3. Try **Policy Assistant** and **Payment Reminders**

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Login fails / CORS error | Set `CORS_ORIGINS` on Render to exact Netlify URL (no trailing slash) |
| API slow on first visit | Render free tier woke from sleep — wait ~1 min |
| AI not working | Check `GEMINI_API_KEY` on Render |
| DB connection error | Use `postgresql+asyncpg://` + `?ssl=require` for Neon |

---

## When you're done testing

- Upgrade Render to paid ($7/mo) to avoid sleep
- Add a custom domain
- Switch to paid AI (`AI_PROVIDER=anthropic`) for production
