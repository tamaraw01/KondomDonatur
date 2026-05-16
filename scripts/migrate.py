import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DATABASE_URL
from src.database import migrate_database


def main() -> None:
    migrate_database()
    print("Database migration completed.")
    print(f"Using DATABASE_URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")


if __name__ == "__main__":
    main()

