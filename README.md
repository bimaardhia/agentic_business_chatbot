# Dashboard Agen AI untuk Analisis Bisnis

Proyek ini adalah aplikasi web interaktif yang dibangun menggunakan Streamlit. Aplikasi ini berfungsi sebagai dashboard cerdas yang ditenagai oleh AI untuk melakukan analisis data bisnis dari database internal. Pengguna dapat berinteraksi dengan AI melalui antarmuka chat untuk mendapatkan wawasan, membuat laporan, dan bahkan mengubah data secara langsung.

##  Fitur Utama

- **User Flow**: Antarmuka chat untuk pengguna umum yang dapat menjawab pertanyaan seputar produk, kebijakan, dan FAQ menggunakan RAG (Retrieval-Augmented Generation).
- **Admin Flow**: Antarmuka chat untuk admin yang mampu melakukan analisis data mendalam, kalkulasi, dan query SQL kompleks ke database.
- **Daily Insight Generator**: Fitur untuk membuat laporan harian otomatis yang merangkum tren penjualan kuantitatif dan wawasan kualitatif dari interaksi pelanggan.
- **Edit Data**: Halaman untuk mengelola data master, memungkinkan pengguna untuk menambah, mengubah, atau menghapus data produk dan penjualan langsung dari antarmuka.

## Teknologi yang Digunakan

- **Frontend**: Streamlit
- **Orkestrasi AI**: LangChain
- **Model Bahasa**: OpenAI (GPT-4o)
- **Database**: SQLite
- **Analisis Data**: Pandas
- **Vector Store**: FAISS

## Setup dan Instalasi

1.  **Clone repositori ini:**
    ```bash
    git clone https://github.com/bimaardhia/agentic_business_chatbot.git
    cd agentic_business_chatbot
    ```

2.  **Buat dan aktifkan virtual environment:**
    ```bash
    python -m venv agent_env
    source agent_env/bin/activate  # Untuk Linux/macOS
    agent_env\Scripts\activate  # Untuk Windows
    ```

3.  **Install dependensi:**
    > **Catatan:** File `requirements.txt` tidak dapat dibaca. Daftar di bawah ini dibuat berdasarkan analisis kode. Anda mungkin perlu menyesuaikannya.
    ```bash
    pip install streamlit sqlalchemy pandas langchain-openai langchain-community langchain-core langchain langchain-text-splitters langchain-experimental faiss-cpu
    ```

## Konfigurasi

Aplikasi ini memerlukan kunci API dari OpenAI. Untuk menjalankannya, Anda harus menyimpannya di dalam fitur **Streamlit Secrets**.

1.  Buat file `.streamlit/secrets.toml` di dalam direktori proyek Anda.
2.  Tambahkan kunci API Anda ke dalam file tersebut dengan format berikut:
    ```toml
    [openai]
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```

## Cara Menjalankan Aplikasi

Setelah instalasi dan konfigurasi selesai, jalankan aplikasi dengan perintah berikut dari direktori utama proyek:

```bash
streamlit run streamlit_app.py
```

Aplikasi akan terbuka secara otomatis di browser Anda.
