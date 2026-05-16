from typing import Any

from src.rule_detector import extract_rule_features
from src.preprocessing import deobfuscate_text


def build_text_for_model(sender_name_raw: object, message_raw: object) -> str:
    parts = [
        str(sender_name_raw or ""),
        str(message_raw or ""),
        deobfuscate_text(sender_name_raw),
        deobfuscate_text(message_raw),
    ]
    return " ".join(part for part in parts if part).strip()


def build_structured_features(
    sender_name_raw: object,
    message_raw: object,
    sender_email_raw: object = "",
    amount: int | float = 0,
) -> dict[str, Any]:
    rule_features = extract_rule_features(sender_name_raw, message_raw, sender_email_raw)
    return {
        "amount": amount or 0,
        "message_length": len(str(message_raw or "")),
        "sender_name_length": len(str(sender_name_raw or "")),
        "contains_url": rule_features["contains_url"],
        "contains_obfuscated_url": rule_features["contains_obfuscated_url"],
        "contains_gambling_keyword": rule_features["contains_gambling_keyword"],
        "contains_provider_keyword": rule_features["contains_provider_keyword"],
        "contains_rtp_pattern": rule_features["contains_rtp_pattern"],
        "contains_percentage_claim": rule_features["contains_percentage_claim"],
        "unicode_symbol_ratio": rule_features["unicode_symbol_ratio"],
        "digit_ratio": rule_features["digit_ratio"],
        "obfuscation_score": rule_features["obfuscation_score"],
    }

