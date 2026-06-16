# MediBot — Streamlit Version

Chatbot informasi RS Sehat Sentosa berbasis Streamlit + AI via Groq API. Fallback Lovable/OpenAI masih bisa dipakai jika key terkait tersedia.

## Cara Menjalankan

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API key Groq

Buat API key di [Groq Console](https://console.groq.com/keys), lalu simpan sebagai `GROQ_API_KEY`.

Linux/Mac:

```bash
export GROQ_API_KEY="gsk_..."
```

Windows PowerShell:

```powershell
$env:GROQ_API_KEY="gsk_..."
```

Windows CMD:

```cmd
set GROQ_API_KEY=gsk_...
```

Streamlit Cloud:

```toml
GROQ_API_KEY = "gsk_..."
```

### 3. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka browser ke `http://localhost:8501`.

## Fitur

- 💬 Chat streaming token-per-token
- 🏥 Knowledge base lengkap RS Sehat Sentosa (poliklinik, jadwal dokter, BPJS, kontak)
- 📝 Riwayat percakapan tersimpan selama sesi
- 🎯 Saran pertanyaan cepat
- 🗑️ Tombol bersihkan percakapan
- 📱 Responsif (desktop & mobile)

## Kustomisasi

Edit `SYSTEM_PROMPT` di `app.py` untuk mengganti info rumah sakit (nama RS, dokter, jadwal, kontak, dll.).

Ganti model dengan mengedit fungsi `get_client()`. Default Groq di file ini memakai `llama-3.3-70b-versatile`. Untuk melihat model aktif, cek endpoint `/models` Groq atau halaman Models di Groq Console.
