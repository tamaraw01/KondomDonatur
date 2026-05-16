import re
from typing import Any

from src.preprocessing import (
    ascii_fold,
    compute_digit_ratio,
    compute_obfuscation_score,
    compute_suspicious_text_char_ratio,
    compute_unicode_symbol_ratio,
    deobfuscate_text,
    normalize_nfkc,
)


GAMBLING_KEYWORDS = {
    "judi",
    "judol",
    "slot",
    "casino",
    "togel",
    "bet",
    "taruhan",
    "gacor",
    "maxwin",
    "scatter",
    "rtp",
    "depo",
    "deposit",
    "wd",
    "withdraw",
    "bonus",
    "admin",
    "bocoran",
    "pola",
    "cuan",
}

GAME_PROVIDER_KEYWORDS = {
    "provider88",
    "situs88",
    "bola88",
    "slot88",
    "max88",
    "win88",
    "jackpot88",
    "spin88",
    "net888",
    "net88",
    "vip88",
    "vip777",
    "play88",
    "play777",
    "game88",
    "bet88",
    "bet777",
}

GAME_KEYWORDS = {"slot", "casino", "togel", "scatter", "spin", "jackpot"}

SPAM_NON_JUDOL_PATTERNS = {
    "follow",
    "subscribe",
    "subrek",
    "jual",
    "promo produk",
    "promo skincare",
    "cek toko",
    "diskon",
}

URL_REGEX = re.compile(r"(https?://|www\.|[a-z0-9-]+\.(?:com|net|org|id)\b)", re.I)
OBFUSCATED_URL_REGEX = re.compile(
    r"(\bdot\s*(?:com|net|org|id)\b|\[\s*dot\s*\]|\(\s*dot\s*\)|\bd0t\b|"
    r"\b[a-z0-9-]+\s*(?:dot|\[dot\]|\(dot\)|d0t)\s*(?:com|net|org|id)\b)",
    re.I,
)
RTP_REGEX = re.compile(r"\br\s*t\s*p\b|\brtp\s*(?:tinggi|[0-9]{2,3})?", re.I)
PERCENTAGE_REGEX = re.compile(r"(\b(?:rtp|winrate|rate|menang)\s*)?\b\d{2,3}\s*%", re.I)
PROVIDER_NUMBER_REGEX = re.compile(
    r"\b(?:net|vip|play|game|spin|slot|bola|bet|max|win|jackpot|situs|provider)\s*(?:88|888|77|777|99|999)\b",
    re.I,
)
PROMO_PHRASE_REGEX = re.compile(
    r"\b(?:pola\s+(?:terbaik|admin|gacor)|hanya\s+di|auto\s+wd|jam\s+gacor|bonus\s+new\s+member)\b",
    re.I,
)


def _combined_text(*texts: object) -> str:
    return " ".join(deobfuscate_text(text) for text in texts if text is not None).strip()


def contains_any_keyword(text: object, keywords: set[str] | list[str] | tuple[str, ...]) -> bool:
    value = deobfuscate_text(text)
    for keyword in keywords:
        normalized = deobfuscate_text(keyword)
        if re.search(rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])", value):
            return True
    return False


def contains_url(text: object) -> bool:
    value = str(text or "")
    return bool(URL_REGEX.search(value) or URL_REGEX.search(deobfuscate_text(value)))


def contains_obfuscated_url(text: object) -> bool:
    value = str(text or "")
    deobfuscated = deobfuscate_text(value)
    return bool(OBFUSCATED_URL_REGEX.search(value) or OBFUSCATED_URL_REGEX.search(deobfuscated))


def contains_rtp_pattern(text: object) -> bool:
    value = deobfuscate_text(text)
    return bool(RTP_REGEX.search(value))


def contains_percentage_claim(text: object) -> bool:
    value = deobfuscate_text(text)
    return bool(PERCENTAGE_REGEX.search(value) or re.search(r"\b(?:rtp|winrate)\s*\d{2,3}\b", value))


def contains_provider_number_pattern(text: object) -> bool:
    value = deobfuscate_text(text)
    compact = re.sub(r"[^a-z0-9]", "", value)
    return bool(PROVIDER_NUMBER_REGEX.search(value) or PROVIDER_NUMBER_REGEX.search(compact))


def contains_promo_phrase(text: object) -> bool:
    return bool(PROMO_PHRASE_REGEX.search(deobfuscate_text(text)))


def split_email(sender_email_raw: object) -> tuple[str, str]:
    value = str(sender_email_raw or "").strip().lower()
    if "@" not in value:
        return value, ""
    localpart, domain = value.split("@", 1)
    return localpart, domain


def extract_rule_features(
    sender_name_raw: object,
    message_raw: object,
    sender_email_raw: object = "",
) -> dict[str, Any]:
    sender_deobfuscated = deobfuscate_text(sender_name_raw)
    message_deobfuscated = deobfuscate_text(message_raw)
    email_localpart, email_domain = split_email(sender_email_raw)
    combined = " ".join(
        [
            sender_deobfuscated,
            message_deobfuscated,
            deobfuscate_text(email_localpart),
            deobfuscate_text(email_domain),
        ]
    )
    raw_combined = " ".join(
        str(part or "") for part in [sender_name_raw, message_raw, sender_email_raw]
    )
    raw_public_text = " ".join(str(part or "") for part in [sender_name_raw, message_raw])

    promo_phrase = contains_promo_phrase(combined)
    contains_gambling = contains_any_keyword(combined, GAMBLING_KEYWORDS) or promo_phrase
    contains_provider = contains_any_keyword(combined, GAME_PROVIDER_KEYWORDS) or any(
        deobfuscate_text(keyword) in combined for keyword in GAME_PROVIDER_KEYWORDS
    ) or contains_provider_number_pattern(combined)
    contains_game = contains_any_keyword(combined, GAME_KEYWORDS)
    has_url = contains_url(raw_public_text)
    has_obfuscated_url = contains_obfuscated_url(raw_public_text)
    has_rtp = contains_rtp_pattern(combined)
    has_percentage = contains_percentage_claim(combined)
    unicode_ratio = compute_unicode_symbol_ratio(raw_combined)
    suspicious_text_ratio = compute_suspicious_text_char_ratio(raw_public_text)
    digit_ratio = compute_digit_ratio(raw_combined)
    obfuscation = max(
        compute_obfuscation_score(sender_name_raw, sender_deobfuscated),
        compute_obfuscation_score(message_raw, message_deobfuscated),
        compute_obfuscation_score(raw_combined, combined),
    )

    return {
        "sender_name_deobfuscated": sender_deobfuscated,
        "message_deobfuscated": message_deobfuscated,
        "email_localpart": email_localpart,
        "email_domain": email_domain,
        "contains_url": int(has_url),
        "contains_obfuscated_url": int(has_obfuscated_url),
        "contains_gambling_keyword": int(contains_gambling),
        "contains_provider_keyword": int(contains_provider),
        "contains_game_keyword": int(contains_game),
        "contains_rtp_pattern": int(has_rtp),
        "contains_percentage_claim": int(has_percentage),
        "contains_provider_number_pattern": int(contains_provider_number_pattern(combined)),
        "contains_promo_phrase": int(promo_phrase),
        "unicode_symbol_ratio": unicode_ratio,
        "suspicious_text_char_ratio": suspicious_text_ratio,
        "contains_suspicious_text_char": int(suspicious_text_ratio > 0),
        "digit_ratio": digit_ratio,
        "obfuscation_score": obfuscation,
    }


def build_processed_record(donation_id: str, sender_name_raw: object, message_raw: object, sender_email_raw: object) -> dict[str, Any]:
    features = extract_rule_features(sender_name_raw, message_raw, sender_email_raw)
    return {
        "donation_id": donation_id,
        "sender_name_nfkc": normalize_nfkc(sender_name_raw),
        "message_nfkc": normalize_nfkc(message_raw),
        "sender_name_ascii_fold": ascii_fold(normalize_nfkc(sender_name_raw)),
        "message_ascii_fold": ascii_fold(normalize_nfkc(message_raw)),
        **features,
    }


def rule_based_label(features: dict[str, Any]) -> str:
    combined_message = f"{features.get('sender_name_deobfuscated', '')} {features.get('message_deobfuscated', '')}"
    contains_provider = bool(features.get("contains_provider_keyword"))
    contains_url_flag = bool(features.get("contains_url") or features.get("contains_obfuscated_url"))
    contains_gambling = bool(features.get("contains_gambling_keyword"))
    contains_rtp = bool(features.get("contains_rtp_pattern") or features.get("contains_percentage_claim"))
    obfuscation_score = float(features.get("obfuscation_score") or 0)
    suspicious_text_ratio = float(features.get("suspicious_text_char_ratio") or 0)

    if contains_provider and (contains_gambling or obfuscation_score > 0.4 or suspicious_text_ratio > 0.15):
        return "explicit_judol"
    if contains_provider and contains_url_flag:
        return "explicit_judol"
    if contains_gambling and contains_rtp:
        return "explicit_judol"
    if contains_gambling and suspicious_text_ratio > 0.15:
        return "explicit_judol"
    if contains_gambling and obfuscation_score > 0.5:
        return "suspicious_judol"
    if suspicious_text_ratio > 0.35 and obfuscation_score > 0.35:
        return "suspicious_judol"
    if contains_provider:
        return "suspicious_judol"
    if contains_gambling:
        return "suspicious_judol"
    if contains_any_keyword(combined_message, SPAM_NON_JUDOL_PATTERNS):
        return "spam_non_judol"
    return "benign"
