CREATE TABLE IF NOT EXISTS donations_raw (
    donation_id TEXT PRIMARY KEY,
    timestamp TEXT,
    platform TEXT,
    sender_name_raw TEXT,
    sender_email_raw TEXT,
    amount INTEGER,
    payment_method TEXT,
    message_raw TEXT,
    streamer_filter_mode TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS donations_processed (
    donation_id TEXT PRIMARY KEY,
    sender_name_nfkc TEXT,
    message_nfkc TEXT,
    sender_name_ascii_fold TEXT,
    message_ascii_fold TEXT,
    sender_name_deobfuscated TEXT,
    message_deobfuscated TEXT,
    email_localpart TEXT,
    email_domain TEXT,
    contains_url INTEGER,
    contains_obfuscated_url INTEGER,
    contains_gambling_keyword INTEGER,
    contains_provider_keyword INTEGER,
    contains_game_keyword INTEGER,
    contains_rtp_pattern INTEGER,
    contains_percentage_claim INTEGER,
    unicode_symbol_ratio REAL,
    digit_ratio REAL,
    obfuscation_score REAL
);

CREATE TABLE IF NOT EXISTS moderation_results (
    donation_id TEXT PRIMARY KEY,
    label_binary INTEGER,
    label_multiclass TEXT,
    risk_score REAL,
    confidence REAL,
    action_label TEXT,
    moderation_status TEXT,
    payment_status TEXT,
    overlay_displayed INTEGER,
    display_sender_name TEXT,
    display_message TEXT,
    explanation TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS streamer_settings (
    streamer_id TEXT PRIMARY KEY,
    streamer_name TEXT,
    filter_mode TEXT,
    risk_threshold_review REAL,
    risk_threshold_mask REAL,
    risk_threshold_block REAL,
    auto_mask_enabled INTEGER,
    auto_block_enabled INTEGER
);

