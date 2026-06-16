"""
MediBot - Chatbot Informasi RSU Kota XYZ
Streamlit + Groq API (OpenAI-compatible endpoint)

Cara menjalankan lokal:
    1. pip install -r requirements.txt
    2. Set GROQ_API_KEY
       Linux/Mac:          export GROQ_API_KEY="gsk_your_key_here"
       Windows PowerShell: $env:GROQ_API_KEY="gsk_your_key_here"
       Windows CMD:        set GROQ_API_KEY=gsk_your_key_here
    3. streamlit run app.py
"""

from __future__ import annotations

import os
from typing import Iterable

import streamlit as st
from openai import OpenAI


# =========================
# Konfigurasi aplikasi
# =========================
APP_TITLE = "MediBot — RSU Kota XYZ"
APP_ICON = "🏥"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="expanded",
)


# =========================
# Knowledge base / system prompt
# =========================
SYSTEM_PROMPT = """Kamu adalah MediBot, asisten virtual ramah untuk RSU Kota XYZ, rumah sakit umum modern di Indonesia.

Tugasmu memberi informasi yang jelas, hangat, dan akurat tentang:

**Layanan & Poliklinik**
- IGD 24 jam (selalu buka)
- Poli Umum: Senin–Sabtu 08:00–20:00
- Poli Anak: Senin–Jumat 08:00–14:00 & 16:00–20:00, Sabtu 08:00–12:00
- Poli Kandungan & Kebidanan: Senin–Sabtu 09:00–17:00
- Poli Jantung: Senin, Rabu, Jumat 09:00–15:00
- Poli Gigi: Senin–Sabtu 09:00–17:00
- Poli Mata, THT, Kulit, Saraf, Penyakit Dalam, Bedah, Ortopedi
- Medical Check Up, Fisioterapi, Hemodialisa
- Laboratorium & Radiologi (Rontgen, USG, CT Scan, MRI) 24 jam

**Dokter Praktek (contoh)**
- dr. Andi Pratama, Sp.JP — Jantung (Sen/Rab/Jum, 09–15)
- dr. Sinta Wijaya, Sp.A — Anak (Sen–Jum)
- dr. Budi Hartono, Sp.OG — Kandungan
- dr. Maya Lestari, Sp.PD — Penyakit Dalam
- drg. Rama Saputra — Gigi Umum

**Pendaftaran**
- Online via website/aplikasi RSU Kota XYZ, Call Center (021) 150890 , atau langsung di loket.
- Bawa: KTP, kartu BPJS/asuransi (jika ada), rujukan dari Faskes 1 (untuk BPJS non-emergensi).

**Pembayaran & Asuransi**
- Tunai, debit, kartu kredit, QRIS.
- BPJS Kesehatan, Mandiri Inhealth, Allianz, AXA, Prudential, Cigna, dan asuransi lain (konfirmasi ke admisi).

**Fasilitas**
- IGD 24 jam, ICU, NICU, PICU, ruang operasi, kamar VIP/Kelas 1/2/3, apotek 24 jam, kantin, parkir luas, ambulans 24 jam.

**Kontak**
- Alamat: Jl. Raya Pajajaran Kota XYZ
- Telp: (021) 150890
- WhatsApp: 0811-2345-678
- Email: info@rsukotaxyz.go.id
- Website: www.rsukotaxyz.go.id

**Aturan Penting:**
1. Jawab dalam Bahasa Indonesia yang ramah dan profesional. Gunakan markdown agar mudah dibaca.
2. Untuk keluhan medis: JANGAN memberi diagnosis atau resep. Sarankan konsultasi langsung ke dokter atau IGD jika darurat.
3. Untuk keadaan darurat seperti nyeri dada hebat, sesak berat, kecelakaan, pendarahan, atau gejala stroke, arahkan segera ke IGD 24 jam atau telepon (021) 555-7890.
4. Jika ditanya hal di luar info RS, jawab singkat lalu tawarkan bantuan terkait layanan RS.
5. Jika info tidak diketahui pasti, jujur katakan dan sarankan menghubungi (021) 555-7890.
"""

SUGGESTIONS = [
    "Jam praktek poli anak hari ini?",
    "Cara daftar pakai BPJS",
    "Jadwal dokter spesialis jantung",
    "Alamat dan kontak IGD",
]


# =========================
# Helper konfigurasi
# =========================
def get_config_value(name: str, default: str | None = None) -> str | None:
    """Ambil konfigurasi dari Streamlit secrets terlebih dahulu, lalu environment variable."""
    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass

    return os.getenv(name, default)


@st.cache_resource(show_spinner=False)
def get_groq_client() -> tuple[OpenAI | None, str | None]:
    """Buat client Groq menggunakan OpenAI-compatible SDK."""
    api_key = get_config_value("GROQ_API_KEY")
    model = get_config_value("GROQ_MODEL", DEFAULT_GROQ_MODEL)

    if not api_key:
        return None, None

    return OpenAI(api_key=api_key, base_url=GROQ_BASE_URL), model


def build_messages(history: list[dict[str, str]]) -> list[dict[str, str]]:
    """Gabungkan system prompt dan riwayat chat untuk dikirim ke model."""
    return [{"role": "system", "content": SYSTEM_PROMPT}, *history]


def stream_reply(client: OpenAI, model: str, messages: list[dict[str, str]]) -> Iterable[str]:
    """Stream balasan AI token-per-token."""
    stream = client.chat.completions.create(
        model=model,
        messages=build_messages(messages),
        stream=True,
        temperature=0.4,
    )

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def reset_chat() -> None:
    """Hapus riwayat chat di session saat ini."""
    st.session_state.messages = []
    st.rerun()


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("### 🏥 RSU Kota XYZ")
    st.caption("Asisten Informasi 24/7")
    st.divider()

    st.markdown("**Kontak Cepat**")
    st.markdown(
        """
- 🚑 **IGD 24 jam**: (021) 150890
- 💬 **WhatsApp**: (021) 150890
- 📍 Jl. Raya Pajajaran
- 🌐 www.rsukotaxyz.go.id
        """
    )
    st.divider()

    st.button("🗑️ Bersihkan percakapan", use_container_width=True, on_click=reset_chat)

    st.caption(
        "ℹ️ Informasi umum, bukan pengganti konsultasi medis. "
        "Untuk keadaan darurat, segera hubungi IGD."
    )


# =========================
# Header
# =========================
col1, col2 = st.columns([1, 6])
with col1:
    st.markdown("<div style='font-size:48px;text-align:center'>🏥</div>", unsafe_allow_html=True)
with col2:
    st.markdown("## MediBot")
    st.caption("Asisten Informasi RSU Kota XYZ · Online 24/7")

st.divider()


# =========================
# State & client
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

client, model = get_groq_client()

if client is None or model is None:
    st.error(
        "❌ **GROQ_API_KEY belum diset.** Buat API key di Groq Console, lalu set `GROQ_API_KEY`.\n\n"
        "**Linux/Mac:**\n"
        "```bash\nexport GROQ_API_KEY=\"gsk_your_key_here\"\nstreamlit run app.py\n```\n"
        "**Windows PowerShell:**\n"
        "```powershell\n$env:GROQ_API_KEY=\"gsk_your_key_here\"\nstreamlit run app.py\n```\n"
        "**Streamlit Cloud:** tambahkan `GROQ_API_KEY` di **App settings → Secrets**."
    )
    st.stop()


# =========================
# Empty state + saran pertanyaan
# =========================
if not st.session_state.messages:
    st.info(
        "👋 Halo, saya **MediBot**. Tanyakan apa saja tentang layanan, jadwal dokter, "
        "pendaftaran, atau kontak RSU Kota XYZ."
    )
    st.markdown("**Coba tanyakan:**")

    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        if cols[i % 2].button(suggestion, key=f"suggestion_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestion})
            st.rerun()


# =========================
# Render riwayat chat
# =========================
for message in st.session_state.messages:
    avatar = "🧑" if message["role"] == "user" else "🩺"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# =========================
# Generate balasan setelah user mengirim pesan
# =========================
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🩺"):
        try:
            reply = st.write_stream(stream_reply(client, model, st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as exc:
            st.error(f"Gagal terhubung ke Groq API: {exc}")


# =========================
# Input chat
# =========================
prompt = st.chat_input("Tanyakan jadwal dokter, layanan, atau cara daftar…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
