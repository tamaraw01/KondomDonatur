from __future__ import annotations

from itertools import cycle

import pandas as pd

from src.config import SAMPLE_DATA_PATH, ensure_project_dirs
from src.feature_engineering import build_text_for_model


BENIGN_MESSAGES = [
    "Semangat bang",
    "Semangat bang 😺🐳",
    "GG mainnya",
    "Sehat selalu",
    "Request lagu dong",
    "Lanjut bang seru banget",
    "Mantap gameplay-nya",
    "Terima kasih sudah live",
    "Bang jangan lupa makan",
    "Nice clutch tadi",
    "Support kecil dari aku",
]

SPAM_MESSAGES = [
    "Follow IG aku ya",
    "Subscribe channel aku",
    "Jual akun murah",
    "Promo skincare murah",
    "Cek toko aku",
    "Diskon produk hari ini",
    "Subrek channel baru aku",
    "Mampir ke lapak aku",
    "Promo produk lokal",
    "Cek link bio aku",
]

SUSPICIOUS_MESSAGES = [
    "jam gacor malam ini",
    "pola admin terbaru",
    "rtp tinggi",
    "gas sekarang",
    "bocoran admin hari ini",
    "cuan cepat malam ini",
    "info maxwin terbaru",
    "pola scatter katanya bagus",
    "admin kasih bocoran",
    "depo kecil bisa cuan",
    "pola terbaik malam ini",
    "info pola admin terbaru",
    "jam gacor paling ramai",
]

EXPLICIT_MESSAGES = [
    "slot gacor rtp 98%",
    "deposit sekarang bonus new member",
    "situs88 dot com gacor",
    "bola88 maxwin malam ini",
    "scatter hitam auto wd",
    "sl0t g4c0r rtp 98%",
    "m4xw1n malam ini",
    "s l o t g a c o r",
    "ｓｌｏｔ ｇａｃｏｒ",
    "gÃcÖr m4xw1n",
    "bocoran adm1n h4ri ini",
    "provider88 dot com bonus rtp 97%",
    "🅿🅾🅻🅰 🆃🅴🆁🅱🅰🅸🅺 🅷🅰🅽🆈🅰 🅳🅸 🅽🅴🆃888",
    "🆂🅻🅾🆃 🅶🅰🅲🅾🆁 🆁🆃🅿 98%",
    "🅱🅾🅲🅾🆁🅰🅽 🅰🅳🅼🅸🅽 🆅🅸🅿777",
    "p-o-l-a terbaik hanya di n-e-t888",
    "s.l.o.t g.a.c.o.r r.t.p 99%",
    "😺🐳 ᵖㄖｌⓐ tＥŘ๒ΔƗк ĦⒶ几𝐘𝔸 ᗪⒾ ηᵉ𝓽➇８❽ 🐻🐼",
    "ᵖㄖｌⓐ terbaik hanya di ηᵉ𝓽➇８❽",
]

SENDER_NAMES = [
    "Budi",
    "Ayu",
    "Raka",
    "Nina",
    "DemoUser",
    "kantorbola88",
    "situs88info",
    "viewer_setia",
    "PromoAkun",
    "max88team",
]


def generate_sample_dataset(force: bool = False) -> pd.DataFrame:
    ensure_project_dirs()
    if SAMPLE_DATA_PATH.exists() and not force:
        return pd.read_csv(SAMPLE_DATA_PATH)

    rows = []
    groups = [
        ("benign", BENIGN_MESSAGES),
        ("spam_non_judol", SPAM_MESSAGES),
        ("suspicious_judol", SUSPICIOUS_MESSAGES),
        ("explicit_judol", EXPLICIT_MESSAGES),
    ]
    sender_cycle = cycle(SENDER_NAMES)

    for label, messages in groups:
        for index in range(50):
            message = messages[index % len(messages)]
            sender = next(sender_cycle)
            if label == "benign":
                sender = ["Budi", "Ayu", "Raka", "Nina", "ViewerBaik"][index % 5]
            elif label == "spam_non_judol":
                sender = ["TokoAyu", "PromoUser", "LapakMurah", "SubrekAku", "JualCepat"][index % 5]
            elif label == "suspicious_judol":
                sender = ["admininfo", "polaUpdate", "cuanMalam", "viewer88", "bocoranNow"][index % 5]
            else:
                sender = ["kantorbola88", "situs88info", "max88team", "slot88news", "provider88"][index % 5]

            rows.append(
                {
                    "donation_id": f"sample_{label}_{index:03d}",
                    "sender_name_raw": sender,
                    "sender_email_raw": f"user{index}@example.com",
                    "amount": 10000 + (index % 10) * 5000,
                    "payment_method": "QRIS",
                    "platform": "Saweria",
                    "message_raw": message,
                    "label_multiclass": label,
                    "text_for_model": build_text_for_model(sender, message),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(SAMPLE_DATA_PATH, index=False)
    return df


if __name__ == "__main__":
    data = generate_sample_dataset(force=True)
    print(f"Generated {len(data)} rows at {SAMPLE_DATA_PATH}")
