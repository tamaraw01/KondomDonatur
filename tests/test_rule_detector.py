from src.rule_detector import extract_rule_features, rule_based_label


def label_for(sender: str, message: str) -> str:
    return rule_based_label(extract_rule_features(sender, message, "demo@example.com"))


def test_rtp_gacor_detected_as_judol():
    assert label_for("viewer", "rtp tinggi gacor") in {"suspicious_judol", "explicit_judol"}


def test_benign_message():
    assert label_for("Budi", "Semangat bang") == "benign"


def test_spam_non_judol_message():
    assert label_for("Ayu", "follow IG aku") == "spam_non_judol"


def test_provider_dot_com_detected():
    assert label_for("situs88", "situs88 dot com") in {"suspicious_judol", "explicit_judol"}


def test_decorative_unicode_provider_pattern_is_explicit_judol():
    message = "🅿🅾🅻🅰 🆃🅴🆁🅱🅰🅸🅺 🅷🅰🅽🆈🅰 🅳🅸 🅽🅴🆃888"
    assert label_for("viewer", message) == "explicit_judol"


def test_plain_terbaik_without_judol_context_stays_benign():
    assert label_for("Budi", "stream terbaik malam ini") == "benign"


def test_mixed_emoji_confusable_text_provider_pattern_is_explicit_judol():
    message = "😺🐳 ᵖㄖｌⓐ tＥŘ๒ΔƗк ĦⒶ几𝐘𝔸 ᗪⒾ ηᵉ𝓽➇８❽ 🐻🐼"
    assert label_for("viewer", message) == "explicit_judol"


def test_plain_emoji_can_remain_benign():
    assert label_for("Budi", "Semangat bang 😺🐳") == "benign"
