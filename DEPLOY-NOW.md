# Deploy now (copy-paste checklist)

Repo: **https://github.com/kashifmayar/creditdesk** (config on `main` includes Groq + Render blueprint).

You create three free accounts; secrets stay in their dashboards only (never in Git).

---

## 1. Neon (database) — ~3 min

1. https://neon.tech → new project → copy connection string.
2. Convert to async format:

   `postgresql+asyncpg://USER:PASS@HOST/DB?ssl=require`

3. SQL editor:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

## 2. Render (API) — ~5 min

1. Open: https://dashboard.render.com/blueprint/new?repo=https://github.com/kashifmayar/creditdesk  
2. Connect GitHub → apply blueprint → service **creditdesk-api**.
3. When prompted, set:

   | Variable | Value |
   |----------|--------|
   | `DATABASE_URL` | Neon string from step 1 |
   | `GROQ_API_KEY` | Your `gsk_…` key |
   | `CORS_ORIGINS` | `https://YOUR-SITE.netlify.app` (update after step 3) |

   `SECRET_KEY` is auto-generated. `AI_PROVIDER` / `GROQ_MODEL` come from `render.yaml`.

4. Deploy → copy API URL, e.g. `https://creditdesk-api.onrender.com`.
5. Test: `https://YOUR-API.onrender.com/health` → `{"status":"ok"}`.

---

## 3. Netlify (UI) — ~5 min

1. Open: https://app.netlify.com/start/deploy?repository=https://github.com/kashifmayar/creditdesk  
2. Connect repo (build settings come from `netlify.toml`).
3. **Site settings → Environment variables:**

   | Key | Value |
   |-----|--------|
   | `VITE_API_BASE_URL` | `https://YOUR-API.onrender.com` (no trailing slash) |

4. **Trigger deploy** (Deploys → Trigger deploy).
5. Copy site URL, e.g. `https://something.netlify.app`.

---

## 4. Link CORS

1. Render → **creditdesk-api** → Environment → set `CORS_ORIGINS` to your exact Netlify URL.
2. **Manual Deploy** on Render.

---

## 5. Smoke test

- URL: your Netlify site  
- Login: `analyst@bank.pk` / `analyst123`  
- Upload CPM PDF → ask a policy question  

First API call after idle may take **30–60s** (Render free tier wake-up).

---

Full notes: [DEPLOY-FREE.md](./DEPLOY-FREE.md)