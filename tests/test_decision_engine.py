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
