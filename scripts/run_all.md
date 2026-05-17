# Run All

Jalankan dari root project `Kondomatur`:

```bash
python scripts/init_db.py
python scripts/migrate.py
python scripts/seed_db.py
python scripts/train_model.py
uvicorn api.main:app --reload --port 8000
streamlit run app/donor_form.py --server.port 8501
streamlit run app/streamer_dashboard.py --server.port 8502
streamlit run app/overlay.py --server.port 8503
```
