from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "donation_shield.db"
SCHEMA_PATH = PROJECT_ROOT / "src" / "schema.sql"
SAMPLE_DATA_PATH = PROJECT_ROOT / "data" / "sample" / "donation_sample.csv"

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8501,http://localhost:8502,http://localhost:8503",
)

_model_path_raw = os.getenv("MODEL_PATH", "models/judol_detector.pkl")
MODEL_PATH = Path(_model_path_raw)
if not MODEL_PATH.is_absolute():
    MODEL_PATH = PROJECT_ROOT / MODEL_PATH

DEFAULT_STREAMER_ID = os.getenv("DEFAULT_STREAMER_ID", "streamer_001")
DEFAULT_STREAMER_NAME = "Demo Streamer"
DEFAULT_FILTER_MODE = os.getenv("DEFAULT_FILTER_MODE", "sensor")


def get_cors_origins() -> list[str]:
    values = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]
    if FRONTEND_URL and FRONTEND_URL not in values:
        values.append(FRONTEND_URL)
    return values or ["*"]


def ensure_project_dirs() -> None:
    for path in [
        PROJECT_ROOT / "data" / "raw",
        PROJECT_ROOT / "data" / "processed",
        PROJECT_ROOT / "data" / "sample",
        PROJECT_ROOT / "models",
    ]:
        path.mkdir(parents=True, exist_ok=True)
