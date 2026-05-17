# Deployment Kondomatur

Panduan ini menyiapkan backend FastAPI di Render/Railway, database Supabase PostgreSQL, dan frontend demo statis di Vercel.

## Environment Variables Backend

Set variable berikut di Render/Railway:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/postgres
FRONTEND_URL=https://your-vercel-app.vercel.app
CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:8501,http://localhost:8502,http://localhost:8503
MODEL_PATH=models/judol_detector.pkl
DEFAULT_STREAMER_ID=streamer_001
DEFAULT_FILTER_MODE=sensor
```

Jangan commit credential Supabase. Ambil `DATABASE_URL` dari Supabase Project Settings, bagian database connection string.

## Deploy Backend ke Render

1. Push repo ke GitHub.
2. Buat Web Service baru di Render.
3. Pilih repo Kondomatur.
4. Build command:

```bash
pip install -r requirements.txt && python scripts/migrate.py && python scripts/seed_db.py
```

5. Start command:

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

6. Set semua environment variable backend.
7. Deploy, lalu buka:

```text
https://your-render-app.onrender.com/health
https://your-render-app.onrender.com/docs
```

## Deploy Backend ke Railway

1. Buat project Railway dari GitHub repo.
2. Set environment variable yang sama.
3. Pastikan start command memakai:

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

4. Jalankan migration dan seed dari Railway shell atau job:

```bash
python scripts/migrate.py
python scripts/seed_db.py
```

## Supabase PostgreSQL

1. Buat project Supabase.
2. Copy PostgreSQL connection string.
3. Set sebagai `DATABASE_URL` di backend.
4. Jalankan:

```bash
python scripts/migrate.py
python scripts/seed_db.py
```

Script bersifat idempotent dan aman dijalankan berulang.

## Deploy Frontend ke Vercel

Frontend statis ada di folder `web/`.

1. Buat project Vercel dari repo ini.
2. Set Root Directory ke `web`.
3. Framework preset: `Other`.
4. Build command kosongkan.
5. Output directory kosongkan atau gunakan default.
6. Deploy.
7. Di halaman web, isi field `Backend API URL` dengan URL Render/Railway, misalnya:

```text
https://your-render-app.onrender.com
```

Tambahkan URL Vercel ke `CORS_ORIGINS` backend.

## Demo Lokal

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/migrate.py
python scripts/seed_db.py
python scripts/train_model.py
uvicorn api.main:app --reload --port 8000
```

Streamlit lokal:

```bash
streamlit run app/donor_form.py --server.port 8501
streamlit run app/streamer_dashboard.py --server.port 8502
streamlit run app/overlay.py --server.port 8503
```

## Testing

Health:

```bash
curl https://your-backend-url/health
```

Docs:

```text
https://your-backend-url/docs
```

Expected `/health`:

```json
{
  "status": "ok",
  "app": "Kondomatur",
  "environment": "production",
  "model_available": true
}
```

