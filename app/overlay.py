import os
import time

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="KondomDonatur - Overlay", page_icon="KD", layout="centered")

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; max-width: 780px; }
    .overlay-card {
        border: 1px solid #d7dde8;
        border-radius: 8px;
        padding: 28px;
        background: #ffffff;
        box-shadow: 0 12px 30px rgba(23, 37, 84, 0.12);
    }
    .amount { font-size: 32px; font-weight: 800; color: #111827; }
    .message { font-size: 24px; margin-top: 14px; color: #374151; }
    </style>
    """,
    unsafe_allow_html=True,
)

top = st.columns([1, 1])
top[0].title("Overlay Donasi")
auto_refresh = top[1].toggle("Auto refresh", value=False)

if auto_refresh:
    time.sleep(3)
    st.rerun()

if st.button("Refresh"):
    st.rerun()

try:
    response = requests.get(f"{API_BASE_URL}/api/overlay", timeout=10)
    response.raise_for_status()
    donations = response.json()
except requests.RequestException as exc:
    st.error("API belum berjalan. Jalankan: uvicorn api.main:app --reload --port 8000")
    st.code(str(exc))
    st.stop()

if not donations:
    st.info("Belum ada donasi yang tampil di overlay.")
    st.stop()

latest = donations[0]
amount = f"IDR{int(latest['amount']):,}".replace(",", ".")
sender = latest["display_sender_name"]
message = latest["display_message"]

st.markdown(
    f"""
    <div class="overlay-card">
        <div class="amount">{amount} dari {sender}</div>
        <div class="message">{message}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Riwayat overlay terbaru"):
    for donation in donations[1:]:
        amount_item = f"IDR{int(donation['amount']):,}".replace(",", ".")
        st.write(f"{amount_item} dari {donation['display_sender_name']}: {donation['display_message']}")
