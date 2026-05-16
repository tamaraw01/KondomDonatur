from src.preprocessing import (
    compute_digit_ratio,
    compute_suspicious_text_char_ratio,
    deobfuscate_text,
    normalize_nfkc,
)


def test_leetspeak_deobfuscation_contains_slot_gacor():
    assert "slot gacor" in deobfuscate_text("sl0t g4c0r")


def test_fullwidth_unicode_normalized():
    assert normalize_nfkc("ｓｌｏｔ") == "slot"
    assert "slot gacor" in deobfuscate_text("ｓｌｏｔ ｇａｃｏｒ")


def test_digit_ratio():
    assert compute_digit_ratio("ab12") == 0.5


def test_negative_squared_unicode_letters_deobfuscated():
    text = "🅿🅾🅻🅰 🆃🅴🆁🅱🅰🅸🅺 🅷🅰🅽🆈🅰 🅳🅸 🅽🅴🆃888"
    assert deobfuscate_text(text) == "pola terbaik hanya di net888"


def test_repeated_provider_digits_are_not_leetspeak_folded():
    assert "net888" in deobfuscate_text("NET888")
    assert "slot gacor" in deobfuscate_text("s.l.o.t g.a.c.o.r")


def test_mixed_emoji_confusable_text_deobfuscated_but_plain_emoji_allowed():
    text = "😺🐳 ᵖㄖｌⓐ tＥŘ๒ΔƗк ĦⒶ几𝐘𝔸 ᗪⒾ ηᵉ𝓽➇８❽ 🐻🐼"
    assert deobfuscate_text(text) == "pola terbaik hanya di net888"
    assert compute_suspicious_text_char_ratio(text) > 0.5
    assert compute_suspicious_text_char_ratio("Semangat 😺🐳") == 0.0
