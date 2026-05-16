from typing import Any


LABEL_RISK_PRIOR = {
    "benign": 0.05,
    "spam_non_judol": 0.18,
    "suspicious_judol": 0.72,
    "explicit_judol": 0.95,
}


def risk_level_from_score(score: float) -> str:
    if score <= 30:
        return "low"
    if score <= 60:
        return "medium"
    if score <= 80:
        return "high"
    return "critical"


def calculate_risk_score(
    model_result: dict[str, Any],
    rule_label: str,
    features: dict[str, Any],
    amount: int | float = 0,
    payment_method: str = "",
) -> dict[str, Any]:
    probabilities = model_result.get("class_probabilities") or {}
    if probabilities:
        model_judol_probability = float(probabilities.get("suspicious_judol", 0)) + float(
            probabilities.get("explicit_judol", 0)
        )
    else:
        model_judol_probability = LABEL_RISK_PRIOR.get(rule_label, 0.1)

    if not model_result.get("model_available"):
        model_judol_probability = max(model_judol_probability, LABEL_RISK_PRIOR.get(rule_label, 0.1))

    keyword_score = 1.0 if features.get("contains_gambling_keyword") else 0.0
    provider_score = 1.0 if features.get("contains_provider_keyword") else 0.0
    url_score = 1.0 if features.get("contains_url") or features.get("contains_obfuscated_url") else 0.0
    sender_name_risk = 1.0 if features.get("contains_provider_keyword") else 0.0
    if features.get("sender_name_deobfuscated") and any(
        word in features["sender_name_deobfuscated"]
        for word in ["slot", "bet", "bola", "win", "jackpot", "situs"]
    ):
        sender_name_risk = max(sender_name_risk, 0.7)

    transaction_context_score = 0.0
    if amount and float(amount) >= 100000:
        transaction_context_score += 0.4
    if str(payment_method or "").lower() in {"crypto", "voucher", "unknown"}:
        transaction_context_score += 0.3
    transaction_context_score = min(transaction_context_score, 1.0)

    score = (
        0.35 * min(model_judol_probability, 1.0)
        + 0.20 * float(features.get("obfuscation_score") or 0)
        + 0.15 * keyword_score
        + 0.10 * provider_score
        + 0.10 * url_score
        + 0.05 * sender_name_risk
        + 0.05 * transaction_context_score
    ) * 100

    if rule_label == "explicit_judol":
        score = max(score, 82.0)
    elif rule_label == "suspicious_judol":
        score = max(score, 62.0)
    elif rule_label == "spam_non_judol":
        score = max(score, 32.0)

    score = round(max(0.0, min(score, 100.0)), 2)
    return {"risk_score": score, "risk_level": risk_level_from_score(score)}

