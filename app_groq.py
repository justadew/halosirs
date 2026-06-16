"""
MediBot - Chatbot Informasi RS Sehat Sentosa (Streamlit version)

Cara menjalankan:
    1. pip install -r requirements.txt
    2. Buat API key di https://console.groq.com/keys
    3. Set environment variable GROQ_API_KEY
       Linux/Mac:  export GROQ_API_KEY="your-key-here"
       Windows:    set GROQ_API_KEY=your-key-here
    4. streamlit run app.py
"""

import os
import streamlit as st
from openai import OpenAI

# ---------- Konfigurasi halaman ----------
st.set_page_config(
    page_title="MediBot — RS Sehat Sentosa",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- Knowledge base / system prompt ----------
SYSTEM_PROMPT = """Kamu adalah MediBot, asisten virtual ramah untuk RS Sehat Sentosa, rumah sakit umum modern di Indonesia.

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
- Online via website/aplikasi RS Sehat Sentosa, WhatsApp 0811-2345-678, atau langsung di loket.
- Bawa: KTP, kartu BPJS/asuransi (jika ada), rujukan dari Faskes 1 (untuk BPJS non-emergensi).

**Pembayaran & Asuransi**
- Tunai, debit, kartu kredit, QRIS.
- BPJS Kesehatan, Mandiri Inhealth, Allianz, AXA, Prudential, Cigna, dan asuransi lain (konfirmasi ke admisi).

**Fasilitas**
- IGD 24 jam, ICU, NICU, PICU, ruang operasi, kamar VIP/Kelas 1/2/3, apotek 24 jam, kantin, parkir luas, ambulans 24 jam.

**Kontak**
- Alamat: Jl. Sehat Raya No. 123, Jakarta Selatan
- Telp: (021) 555-7890
- WhatsApp: 0811-2345-678
- Email: info@rs-sehatsentosa.co.id
- Website: www.rs-sehatsentosa.co.id

**Aturan Penting:**
1. Jawab dalam Bahasa Indonesia yang ramah dan profesional. Gunakan markdown (bullet, bold) agar mudah dibaca.
2. Untuk keluhan medis: JANGAN memberi diagnosis atau resep. Sarankan konsultasi langsung ke dokter / IGD jika darurat.
3. Untuk keadaan darurat (nyeri dada hebat, sesak berat, kecelakaan, pendarahan, stroke), arahkan segera ke IGD 24 jam atau telp (021) 555-7890.
4. Jika ditanya hal di luar info RS, jawab singkat lalu tawarkan bantuan terkait layanan RS.
5. Jika info tidak diketahui pasti, jujur katakan dan sarankan menghubungi (021) 555-7890.
"""

SUGGESTIONS = [
    "Jam praktek poli anak hari ini?",
    "Cara daftar pakai BPJS",
    "Jadwal dokter spesialis jantung",
    "Alamat dan kontak IGD",
]

# ---------- AI client ----------
def get_config_value(name: str):
    """Ambil key dari Streamlit secrets lebih dulu, lalu environment variable."""
    try:
        return st.secrets.get(name)
    except Exception:
        return os.getenv(name)


@st.cache_resource
def get_client():
    """Buat OpenAI-compatible client. Default ke Groq,
    fallback ke Lovable/OpenAI jika key lain di-set."""
    groq_key = get_config_value("GROQ_API_KEY")
    lovable_key = get_config_value("LOVABLE_API_KEY")
    openai_key = get_config_value("OPENAI_API_KEY")

    if groq_key:
        return OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
        ), "llama-3.3-70b-versatile"
    if lovable_key:
        return OpenAI(
            api_key=lovable_key,
            base_url="https://ai.gateway.lovable.dev/v1",
            default_headers={"Lovable-API-Key": lovable_key},
        ), "google/gemini-3-flash-preview"
    if openai_key:
        return OpenAI(api_key=openai_key), "gpt-4o-mini"
    return None, None


def stream_reply(client, model, messages):
    """Stream balasan AI token-per-token."""
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
        stream=True,
        temperature=0.7,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield delta


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🏥 RS Sehat Sentosa")
    st.caption("Asisten Informasi 24/7")
    st.divider()

    st.markdown("**Kontak Cepat**")
    st.markdown(
        """
- 🚑 **IGD 24 jam**: (021) 555-7890
- 💬 **WhatsApp**: 0811-2345-678
- 📍 Jl. Sehat Raya No. 123, Jakarta Selatan
- 🌐 www.rs-sehatsentosa.co.id
        """
    )
    st.divider()

    if st.button("🗑️ Bersihkan percakapan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(
        "ℹ️ Informasi umum, bukan pengganti konsultasi medis. "
        "Untuk keadaan darurat, segera hubungi IGD."
    )

# ---------- Header ----------
col1, col2 = st.columns([1, 6])
with col1:
    st.markdown("<div style='font-size:48px;text-align:center'>🏥</div>", unsafe_allow_html=True)
with col2:
    st.markdown("## MediBot")
    st.caption("Asisten Informasi RS Sehat Sentosa · Online 24/7")

st.divider()

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

client, model = get_client()

# ---------- Pesan kesalahan jika tidak ada API key ----------
if client is None:
    st.error(
        "❌ **API key belum diset.** Buat key di Groq Console, lalu set `GROQ_API_KEY`.\n\n"
        "Local Linux/Mac:\n"
        "```bash\nexport GROQ_API_KEY=\"gsk_your_key_here\"\nstreamlit run app.py\n```\n"
        "Windows PowerShell:\n"
        "```powershell\n$env:GROQ_API_KEY=\"gsk_your_key_here\"\nstreamlit run app.py\n```\n"
        "Streamlit Cloud: tambahkan `GROQ_API_KEY` di App settings → Secrets."
    )
    st.stop()

# ---------- Empty state dengan saran ----------
if not st.session_state.messages:
    st.info("👋 Halo, saya **MediBot**. Tanyakan apa saja tentang layanan, jadwal dokter, pendaftaran, atau kontak RS Sehat Sentosa.")
    st.markdown("**Coba tanyakan:**")
    cols = st.columns(2)
    for i, s in enumerate(SUGGESTIONS):
        if cols[i % 2].button(s, key=f"sug_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": s})
            st.rerun()

# ---------- Render riwayat ----------
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🩺"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------- Jika pesan terakhir dari user dan belum dijawab → stream balasan ----------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🩺"):
        try:
            reply = st.write_stream(stream_reply(client, model, st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Gagal terhubung ke AI: {e}")

# ---------- Composer ----------
prompt = st.chat_input("Tanyakan jadwal dokter, layanan, atau cara daftar…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
