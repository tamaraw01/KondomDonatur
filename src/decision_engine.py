from typing import Any
from uuid import uuid4

from src.model import predict_label
from src.risk_scoring import calculate_risk_score
from src.rule_detector import extract_rule_features, rule_based_label


MASKED_SENDER = "someone"
MASKED_MESSAGE = "pesan ini telah disembunyikan oleh AI"
REJECTION_MESSAGE = "Donasi gagal diproses karena pesan terindikasi melanggar kebijakan."
LABEL_SEVERITY = {
    "benign": 0,
    "spam_non_judol": 1,
    "suspicious_judol": 2,
    "explicit_judol": 3,
}


def _stronger_label(model_label: str, rule_label: str) -> str:
    if LABEL_SEVERITY.get(rule_label, 0) >= LABEL_SEVERITY.get(model_label, 0):
        return rule_label
    return model_label


def build_explanation(features: dict[str, Any], label: str) -> str:
    reasons: list[str] = []
    if features.get("contains_gambling_keyword"):
        reasons.append("Teks mengandung keyword promosi judol setelah normalisasi")
    if features.get("contains_provider_keyword"):
        reasons.append("Nama pengirim mengandung pola situs/provider")
    if features.get("contains_rtp_pattern") or features.get("contains_percentage_claim"):
        reasons.append("Ditemukan pola RTP atau klaim persentase")
    if float(features.get("obfuscation_score") or 0) >= 0.45:
        reasons.append("Teks memiliki obfuscation score tinggi")
    if float(features.get("suspicious_text_char_ratio") or 0) >= 0.15:
        reasons.append("Teks memakai huruf/angka hias non-standar untuk menyamarkan pesan")
    if features.get("contains_url") or features.get("contains_obfuscated_url"):
        reasons.append("Ditemukan URL atau domain tersamarkan")
    if label == "spam_non_judol":
        reasons.append("Teks menyerupai promosi spam non-judol")
    if not reasons:
        reasons.append("Tidak ditemukan indikasi pelanggaran utama")
    return "; ".join(reasons)


def make_decision(input_data: dict[str, Any], filter_mode: str = "sensor") -> dict[str, Any]:
    donation_id = input_data.get("donation_id") or f"don_{uuid4().hex[:12]}"
    sender_name_raw = input_data.get("sender_name_raw", "")
    sender_email_raw = input_data.get("sender_email_raw", "")
    amount = input_data.get("amount", 0) or 0
    payment_method = input_data.get("payment_method", "")
    message_raw = input_data.get("message_raw", "")

    features = extract_rule_features(sender_name_raw, message_raw, sender_email_raw)
    rule_label = rule_based_label(features)
    model_result = predict_label(sender_name_raw, message_raw, sender_email_raw)
    label = _stronger_label(model_result.get("label_multiclass", "benign"), rule_label)
    risk = calculate_risk_score(model_result, rule_label, features, amount, payment_method)
    risk_score = risk["risk_score"]

    action_label = "allow"
    moderation_status = "clean"
    payment_status = "success"
    overlay_displayed = True
    display_sender_name = str(sender_name_raw or "")
    display_message = str(message_raw or "")

    if filter_mode == "sensor":
        if label == "spam_non_judol":
            action_label = "review"
            moderation_status = "review"
        elif label in {"suspicious_judol", "explicit_judol"}:
            action_label = "mask"
            moderation_status = "flagged"
            display_sender_name = MASKED_SENDER
            display_message = MASKED_MESSAGE
    elif filter_mode == "block":
        if label == "spam_non_judol":
            action_label = "review"
            moderation_status = "review"
        elif label == "suspicious_judol":
            if risk_score < 70:
                action_label = "review"
                payment_status = "pending"
                moderation_status = "review"
                overlay_displayed = False
                display_sender_name = ""
                display_message = ""
            else:
                action_label = "block"
                payment_status = "rejected"
                moderation_status = "blocked"
                overlay_displayed = False
                display_sender_name = ""
                display_message = ""
        elif label == "explicit_judol":
            action_label = "block"
            payment_status = "rejected"
            moderation_status = "blocked"
            overlay_displayed = False
            display_sender_name = ""
            display_message = ""
    else:
        raise ValueError("filter_mode must be 'sensor' or 'block'")

    return {
        "donation_id": donation_id,
        "label_binary": int(label in {"suspicious_judol", "explicit_judol"}),
        "label_multiclass": label,
        "risk_score": risk_score,
        "risk_level": risk["risk_level"],
        "confidence": round(float(model_result.get("confidence") or 0), 4),
        "action_label": action_label,
        "moderation_status": moderation_status,
        "payment_status": payment_status,
        "overlay_displayed": overlay_displayed,
        "display_sender_name": display_sender_name,
        "display_message": display_message,
        "donor_message": REJECTION_MESSAGE if payment_status == "rejected" else "",
        "explanation": build_explanation(features, label),
    }
