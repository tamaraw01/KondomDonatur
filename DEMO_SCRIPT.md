# Demo Script Kondomatur

Gunakan `/streamer` untuk memilih mode, lalu buka link `/donate/{streamer_id}`. Setelah form donasi dikirim, lanjutkan ke `/checkout/{payment_intent_id}` untuk menekan tombol bayar sandbox.

## 1. Donasi Normal

- Nama: `Budi`
- Email: `budi@example.com`
- Nominal: `25000`
- Mode: `sensor` atau `block`
- Pesan: `Semangat bang, lanjut mainnya!`

Expected:

- `label_multiclass = benign`
- `action_label = allow`
- payment intent dibuat
- sebelum checkout paid: `payment_status = pending`, overlay hidden
- setelah checkout paid: `payment_status = success`, overlay tampil normal dengan nama dan pesan asli

## 2. Judol Mode Sensor

- Nama: `kantorbola88`
- Email: `demo@example.com`
- Nominal: `100000`
- Mode: `sensor`
- Pesan: `RTP tinggi malam ini, gas sekarang!`

Expected:

- `label_multiclass = explicit_judol` atau `suspicious_judol`
- `action_label = mask`
- `moderation_status = flagged`
- payment intent dibuat
- sebelum checkout paid: `payment_status = pending`, overlay hidden
- setelah checkout paid: `payment_status = success`, overlay menampilkan `someone` dan `pesan ini telah disembunyikan oleh AI`

## 3. Judol Mode Blokir

- Nama: `kantorbola88`
- Email: `demo@example.com`
- Nominal: `100000`
- Mode: `block`
- Pesan: `RTP tinggi malam ini, gas sekarang!`

Expected:

- `action_label = block`
- payment intent tidak dibuat
- `payment_status = rejected`
- `moderation_status = blocked`
- `overlay_displayed = false`
- Donor mendapat pesan: `Donasi gagal diproses karena pesan terindikasi melanggar kebijakan.`

## 4. Fancy Unicode Judol

- Nama: `๑۞๑ ϰꍏ♫☂⊙☈♭ꍏ↳↳88 ๑۞๑`
- Email: `demo@example.com`
- Nominal: `88000`
- Mode: `sensor`
- Pesan: `ｓｌｏｔ ｇａｃｏｒ rtp 98%`

Expected:

- Teks terdeteksi setelah normalisasi/deobfuscation.
- `action_label = mask`
- payment intent dibuat
- setelah checkout paid, overlay tampil tersensor.

## 5. Huruf Hias Provider

- Nama: `viewer`
- Email: `demo@example.com`
- Nominal: `88000`
- Mode: `sensor` lalu ulangi di `block`
- Pesan: `🅿🅾🅻🅰 🆃🅴🆁🅱🅰🅸🅺 🅷🅰🅽🆈🅰 🅳🅸 🅽🅴🆃888`

Expected:

- Normalisasi menjadi `pola terbaik hanya di net888`.
- `label_multiclass = explicit_judol`.
- Mode Sensor: payment intent dibuat, overlay tersensor setelah paid.
- Mode Blokir: payment intent tidak dibuat dan overlay hidden.

## 6. Emoji + Huruf Hias Campuran

- Nama: `viewer`
- Email: `demo@example.com`
- Nominal: `88000`
- Mode: `sensor` lalu ulangi di `block`
- Pesan: `😺🐳 ᵖㄖｌⓐ tＥŘ๒ΔƗк ĦⒶ几𝐘𝔸 ᗪⒾ ηᵉ𝓽➇８❽ 🐻🐼`

Expected:

- Emoji biasa tidak dianggap pelanggaran sendiri.
- Huruf/angka hias non-standar dinormalisasi menjadi `pola terbaik hanya di net888`.
- `label_multiclass = explicit_judol`.
- Mode Sensor: payment intent dibuat, overlay tersensor setelah paid.
- Mode Blokir: payment intent tidak dibuat dan overlay hidden.
