import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DEFAULT_FILTER_MODE, DEFAULT_STREAMER_ID
from src.database import db_connection, migrate_database, seed_default_settings


def main() -> None:
    migrate_database()
    with db_connection() as conn:
        seed_default_settings(conn)
    print(f"Seed completed for streamer_id={DEFAULT_STREAMER_ID}, filter_mode={DEFAULT_FILTER_MODE}")


if __name__ == "__main__":
    main()

