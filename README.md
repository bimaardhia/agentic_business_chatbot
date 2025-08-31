# Dashboard Agen AI untuk Analisis Bisnis Cerdas

## Abstrak

Proyek ini menghadirkan sebuah aplikasi web interaktif yang berfungsi sebagai **Dashboard Agen AI** untuk analisis bisnis. Dibangun dengan Streamlit dan ditenagai oleh LangChain dan model bahasa dari OpenAI, aplikasi ini mengubah cara interaksi dengan data bisnis. Alih-alih menggunakan dashboard statis, pengguna dapat berkomunikasi langsung dengan agen AI melalui antarmuka chat untuk menanyakan data, meminta analisis, hingga menghasilkan laporan harian secara dinamis. Aplikasi ini dirancang untuk menjembatani kesenjangan antara data teknis dan pengambilan keputusan bisnis yang strategis.

## Latar Belakang

Dalam lingkungan bisnis yang serba cepat, akses cepat dan tepat terhadap data menjadi krusial. Namun, sering kali manajer bisnis atau pemangku kepentingan non-teknis kesulitan untuk mendapatkan wawasan dari database tanpa bantuan seorang analis data. Proses query data yang manual, pembuatan laporan yang memakan waktu, dan dashboard BI (Business Intelligence) yang kaku menjadi penghambat. Proyek ini lahir dari kebutuhan untuk mendemokratisasi akses data, memungkinkan siapa saja di dalam organisasi untuk "berbicara" dengan data mereka dan mendapatkan jawaban secara instan.

## Tujuan Proyek

- **Memberikan Akses Intuitif ke Data**: Menyediakan antarmuka percakapan (chat) sebagai cara utama untuk berinteraksi dengan database bisnis, menghilangkan kebutuhan akan keahlian SQL atau analisis data yang kompleks.
- **Mempercepat Pengambilan Keputusan**: Memungkinkan pengguna untuk mendapatkan analisis data, tren penjualan, dan wawasan pelanggan secara real-time untuk mendukung keputusan yang lebih cepat dan berbasis data.
- **Mengotomatisasi Pelaporan**: Menyediakan fitur untuk menghasilkan ringkasan dan laporan harian secara otomatis, menghemat waktu dan sumber daya.
- **Menyediakan Platform Terpusat**: Menggabungkan kemampuan analisis, visualisasi, dan manajemen data dalam satu aplikasi yang mudah digunakan.

## Fitur dan Kemampuan

Aplikasi ini memiliki beberapa halaman dengan fungsi yang spesifik:

### 1. User Flow
- **Untuk Siapa**: Pengguna umum, seperti tim penjualan atau customer service.
- **Kemampuan**: Dapat menjawab pertanyaan umum seputar produk, kebijakan perusahaan, dan pertanyaan yang sering diajukan (FAQ). Contohnya:
  - *"Apa saja metode pembayaran yang diterima?"*
  - *"Berapa lama garansi untuk laptop Dell XPS 15?"*
  - *"Bagaimana cara memilih laptop untuk desain grafis?"*

### 2. Admin Flow
- **Untuk Siapa**: Manajer, analis, atau pemilik bisnis.
- **Kemampuan**: Mampu melakukan analisis data yang lebih kompleks, menggabungkan data, dan melakukan perhitungan. Agen AI di halaman ini dapat menerjemahkan pertanyaan menjadi query SQL dan bahkan menjalankan kode Python untuk analisis lebih lanjut. Contohnya:
  - *"Berapa total pendapatan dari penjualan online bulan ini?"*
  - *"Tampilkan produk terlaris berdasarkan kuantitas penjualan."
  - *"Hitung rata-rata harga jual semua produk."

### 3. Daily Insight Generator
- **Untuk Siapa**: Tim manajemen dan strategi.
- **Kemampuan**: Secara otomatis menghasilkan laporan harian dengan memilih tanggal. Laporan ini menggabungkan:
  - **Analisis Kuantitatif**: Data penjualan dari database (misalnya, total penjualan, produk terlaris hari itu).
  - **Analisis Kualitatif**: Wawasan dari riwayat percakapan pelanggan (misalnya, keluhan umum, produk yang sering ditanyakan).

### 4. Edit Data
- **Untuk Siapa**: Administrator database atau manajer produk.
- **Kemampuan**: Menyediakan antarmuka seperti spreadsheet untuk mengelola data di dalam database. Pengguna dapat menambah, mengubah, atau menghapus data pada tabel `products` dan `sales` secara langsung dan menyimpannya kembali ke database.

## Arsitektur dan Teknologi

- **Frontend**: Streamlit
- **Orkestrasi AI**: LangChain (menggunakan ReAct Agent)
- **Model Bahasa**: OpenAI (GPT-4o)
- **Database**: SQLite (untuk data produk dan penjualan)
- **Analisis Data**: Pandas
- **Vector Store**: FAISS (untuk RAG pada data tekstual seperti FAQ dan kebijakan)

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
    > **Catatan:** File `requirements.txt` tidak dapat dibaca dengan benar. Daftar di bawah ini dibuat berdasarkan analisis kode. Anda mungkin perlu menyesuaikannya.
    ```bash
    pip install streamlit sqlalchemy pandas langchain-openai langchain-community langchain-core langchain langchain-text-splitters langchain-experimental faiss-cpu
    ```

## Konfigurasi

Aplikasi ini memerlukan kunci API dari OpenAI untuk berfungsi. Kunci ini harus disimpan di dalam **Streamlit Secrets**.

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

Aplikasi akan terbuka secara otomatis di browser web Anda.