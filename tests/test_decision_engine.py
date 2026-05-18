from src.decision_engine import make_decision


EXPLICIT_INPUT = {
    "sender_name_raw": "kantorbola88",
    "sender_email_raw": "demo@example.com",
    "amount": 100000,
    "payment_method": "QRIS",
    "platform": "Saweria",
    "message_raw": "slot gacor rtp 98%",
}


def test_sensor_explicit_judol_masks_but_payment_success():
    decision = make_decision(EXPLICIT_INPUT, "sensor")
    assert decision["action_label"] == "mask"
    assert decision["payment_status"] == "success"
    assert decision["overlay_displayed"] is True
    assert decision["display_sender_name"] == "someone"


def test_block_explicit_judol_rejects_and_hides_overlay():
    decision = make_decision(EXPLICIT_INPUT, "block")
    assert decision["action_label"] == "block"
    assert decision["payment_status"] == "rejected"
    assert decision["overlay_displayed"] is False


def test_benign_allows():
    decision = make_decision(
        {
            "sender_name_raw": "Budi",
            "sender_email_raw": "budi@example.com",
            "amount": 25000,
            "payment_method": "QRIS",
            "platform": "Saweria",
            "message_raw": "Semangat bang",
        },
        "sensor",
    )
    assert decision["label_multiclass"] == "benign"
    assert decision["action_label"] == "allow"
    assert decision["payment_status"] == "success"


def test_benign_emoji_message_keeps_original_display():
    decision = make_decision(
        {
            "sender_name_raw": "Budi",
            "sender_email_raw": "budi@example.com",
            "amount": 25000,
            "payment_method": "QRIS",
            "platform": "Saweria",
            "message_raw": "Semangat bang 😺🐳",
        },
        "sensor",
    )
    assert decision["label_multiclass"] == "benign"
    assert decision["display_message"] == "Semangat bang 😺🐳"


def test_gaul_benign_chat_does_not_get_masked():
    decision = make_decision(
        {
            "sender_name_raw": "ngabSantuy",
            "sender_email_raw": "viewer@example.com",
            "amount": 20000,
            "payment_method": "QRIS",
            "platform": "Kondomatur",
            "message_raw": "ggwp bang no debat, gaskeun mabar lagi ygy",
        },
        "sensor",
    )
    assert decision["label_multiclass"] == "benign"
    assert decision["action_label"] == "allow"
    assert decision["display_message"] == "ggwp bang no debat, gaskeun mabar lagi ygy"


def test_gaul_non_judol_promo_goes_to_review_not_mask():
    decision = make_decision(
        {
            "sender_name_raw": "LapakMurah",
            "sender_email_raw": "seller@example.com",
            "amount": 20000,
            "payment_method": "QRIS",
            "platform": "Kondomatur",
            "message_raw": "spill katalog baru cuy gercep ya",
        },
        "sensor",
    )
    assert decision["label_multiclass"] == "spam_non_judol"
    assert decision["action_label"] == "review"
    assert decision["display_message"] == "spill katalog baru cuy gercep ya"


def test_real_youtube_judol_terms_are_explicit_high_risk():
    decision = make_decision(
        {
            "sender_name_raw": "viewer",
            "sender_email_raw": "viewer@example.com",
            "amount": 20000,
            "payment_method": "QRIS",
            "platform": "YouTube Live",
            "message_raw": "ketik di googlewisdomtoto",
        },
        "sensor",
    )
    assert decision["label_multiclass"] == "explicit_judol"
    assert decision["risk_score"] >= 80
    assert decision["action_label"] == "mask"
