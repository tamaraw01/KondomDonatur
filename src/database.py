from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine, Row, RowMapping

from src.config import (
    DATABASE_URL,
    DEFAULT_FILTER_MODE,
    DEFAULT_STREAMER_ID,
    DEFAULT_STREAMER_NAME,
    SCHEMA_PATH,
    ensure_project_dirs,
)


_ENGINE: Engine | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if database_url.startswith("postgresql://") and "+psycopg2" not in database_url:
        return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return database_url


def is_sqlite_url(database_url: str | None = None) -> bool:
    return (database_url or DATABASE_URL).startswith("sqlite")


def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        ensure_project_dirs()
        database_url = normalize_database_url(DATABASE_URL)
        connect_args = {"check_same_thread": False} if is_sqlite_url(database_url) else {}
        _ENGINE = create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)
    return _ENGINE


@contextmanager
def db_connection() -> Iterator[Connection]:
    with get_engine().begin() as conn:
        yield conn


def _split_sql_statements(sql: str) -> list[str]:
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def migrate_database() -> None:
    ensure_project_dirs()
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with db_connection() as conn:
        for statement in _split_sql_statements(schema):
            conn.execute(text(statement))


def init_db() -> None:
    migrate_database()
    with db_connection() as conn:
        seed_default_settings(conn)


def fetch_one(conn: Connection, query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    row = conn.execute(text(query), params or {}).mappings().fetchone()
    return row_to_dict(row)


def fetch_all(conn: Connection, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = conn.execute(text(query), params or {}).mappings().fetchall()
    return [dict(row) for row in rows]


def seed_default_settings(conn: Connection) -> None:
    existing = fetch_one(
        conn,
        "SELECT streamer_id FROM streamer_settings WHERE streamer_id = :streamer_id",
        {"streamer_id": DEFAULT_STREAMER_ID},
    )
    if existing:
        return
    conn.execute(
        text(
            """
            INSERT INTO streamer_settings (
                streamer_id,
                streamer_name,
                filter_mode,
                risk_threshold_review,
                risk_threshold_mask,
                risk_threshold_block,
                auto_mask_enabled,
                auto_block_enabled
            ) VALUES (
                :streamer_id,
                :streamer_name,
                :filter_mode,
                :risk_threshold_review,
                :risk_threshold_mask,
                :risk_threshold_block,
                :auto_mask_enabled,
                :auto_block_enabled
            )
            """
        ),
        {
            "streamer_id": DEFAULT_STREAMER_ID,
            "streamer_name": DEFAULT_STREAMER_NAME,
            "filter_mode": DEFAULT_FILTER_MODE,
            "risk_threshold_review": 35,
            "risk_threshold_mask": 60,
            "risk_threshold_block": 80,
            "auto_mask_enabled": 1,
            "auto_block_enabled": 1,
        },
    )


def row_to_dict(row: Row[Any] | RowMapping | dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    if hasattr(row, "_mapping"):
        return dict(row._mapping)
    return dict(row)


def fetch_settings(streamer_id: str = DEFAULT_STREAMER_ID) -> dict[str, Any]:
    init_db()
    with db_connection() as conn:
        row = fetch_one(
            conn,
            "SELECT * FROM streamer_settings WHERE streamer_id = :streamer_id",
            {"streamer_id": streamer_id},
        )
        if row is None:
            seed_default_settings(conn)
            row = fetch_one(
                conn,
                "SELECT * FROM streamer_settings WHERE streamer_id = :streamer_id",
                {"streamer_id": streamer_id},
            )
        return row or {}


def update_filter_mode(streamer_id: str, filter_mode: str) -> dict[str, Any]:
    if filter_mode not in {"sensor", "block"}:
        raise ValueError("filter_mode must be 'sensor' or 'block'")
    init_db()
    with db_connection() as conn:
        seed_default_settings(conn)
        conn.execute(
            text("UPDATE streamer_settings SET filter_mode = :filter_mode WHERE streamer_id = :streamer_id"),
            {"filter_mode": filter_mode, "streamer_id": streamer_id},
        )
        return fetch_one(
            conn,
            "SELECT * FROM streamer_settings WHERE streamer_id = :streamer_id",
            {"streamer_id": streamer_id},
        ) or {}


def insert_raw_donation(conn: Connection, row: dict[str, Any]) -> None:
    conn.execute(
        text(
            """
            INSERT INTO donations_raw (
                donation_id, timestamp, platform, sender_name_raw, sender_email_raw,
                amount, payment_method, message_raw, streamer_filter_mode, created_at
            ) VALUES (
                :donation_id, :timestamp, :platform, :sender_name_raw,
                :sender_email_raw, :amount, :payment_method, :message_raw,
                :streamer_filter_mode, :created_at
            )
            """
        ),
        row,
    )


def insert_processed_donation(conn: Connection, row: dict[str, Any]) -> None:
    conn.execute(
        text(
            """
            INSERT INTO donations_processed (
                donation_id, sender_name_nfkc, message_nfkc, sender_name_ascii_fold,
                message_ascii_fold, sender_name_deobfuscated, message_deobfuscated,
                email_localpart, email_domain, contains_url, contains_obfuscated_url,
                contains_gambling_keyword, contains_provider_keyword, contains_game_keyword,
                contains_rtp_pattern, contains_percentage_claim, unicode_symbol_ratio,
                digit_ratio, obfuscation_score
            ) VALUES (
                :donation_id, :sender_name_nfkc, :message_nfkc, :sender_name_ascii_fold,
                :message_ascii_fold, :sender_name_deobfuscated, :message_deobfuscated,
                :email_localpart, :email_domain, :contains_url, :contains_obfuscated_url,
                :contains_gambling_keyword, :contains_provider_keyword, :contains_game_keyword,
                :contains_rtp_pattern, :contains_percentage_claim, :unicode_symbol_ratio,
                :digit_ratio, :obfuscation_score
            )
            """
        ),
        row,
    )


def insert_moderation_result(conn: Connection, row: dict[str, Any]) -> None:
    conn.execute(
        text(
            """
            INSERT INTO moderation_results (
                donation_id, label_binary, label_multiclass, risk_score, confidence,
                action_label, moderation_status, payment_status, overlay_displayed,
                display_sender_name, display_message, explanation, created_at
            ) VALUES (
                :donation_id, :label_binary, :label_multiclass, :risk_score, :confidence,
                :action_label, :moderation_status, :payment_status, :overlay_displayed,
                :display_sender_name, :display_message, :explanation, :created_at
            )
            """
        ),
        row,
    )
