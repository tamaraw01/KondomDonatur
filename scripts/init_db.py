import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DATABASE_URL
from src.database import init_db


def main() -> None:
    init_db()
    safe_database_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    print(f"Database initialized: {safe_database_url}")
    print("Default streamer setting seeded: streamer_001 / Demo Streamer / sensor")


if __name__ == "__main__":
    main()
