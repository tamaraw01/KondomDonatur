from functools import lru_cache
from typing import Any

import joblib

from src.config import MODEL_PATH
from src.feature_engineering import build_text_for_model
from src.rule_detector import extract_rule_features, rule_based_label


LABELS = ["benign", "spam_non_judol", "suspicious_judol", "explicit_judol"]


@lru_cache(maxsize=1)
def load_model() -> Any | None:
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def _fallback_prediction(sender_name_raw: object, message_raw: object, sender_email_raw: object = "") -> dict[str, Any]:
    features = extract_rule_features(sender_name_raw, message_raw, sender_email_raw)
    label = rule_based_label(features)
    probabilities = {item: 0.0 for item in LABELS}
    probabilities[label] = 0.86 if label != "benign" else 0.78
    return {
        "label_multiclass": label,
        "confidence": probabilities[label],
        "class_probabilities": probabilities,
        "model_available": False,
    }


def predict_label(
    sender_name_raw: object,
    message_raw: object,
    sender_email_raw: object = "",
) -> dict[str, Any]:
    model = load_model()
    if model is None:
        return _fallback_prediction(sender_name_raw, message_raw, sender_email_raw)

    text = build_text_for_model(sender_name_raw, message_raw)
    try:
        label = str(model.predict([text])[0])
        if hasattr(model, "predict_proba"):
            probabilities_raw = model.predict_proba([text])[0]
            classes = list(model.classes_)
            probabilities = {
                str(class_name): round(float(prob), 4)
                for class_name, prob in zip(classes, probabilities_raw)
            }
            confidence = float(max(probabilities.values())) if probabilities else 0.0
        else:
            probabilities = {item: 0.0 for item in LABELS}
            probabilities[label] = 0.7
            confidence = 0.7
        for known_label in LABELS:
            probabilities.setdefault(known_label, 0.0)
        return {
            "label_multiclass": label,
            "confidence": round(confidence, 4),
            "class_probabilities": probabilities,
            "model_available": True,
        }
    except Exception:
        return _fallback_prediction(sender_name_raw, message_raw, sender_email_raw)

