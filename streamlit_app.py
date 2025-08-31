# streamlit_app.py

import streamlit as st
import os
import sqlite3
from sqlalchemy import create_engine
import pandas as pd
import re
import io
import contextlib
from datetime import date

# LangChain Imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_experimental.tools import PythonREPLTool

# --- Konfigurasi Aplikasi Streamlit ---
st.set_page_config(
    page_title="Dashboard Agen AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar untuk Konfigurasi ---
st.sidebar.title("⚙️ Konfigurasi")

# Coba ambil API key dari st.secrets.
try:
    openai_api_key = st.secrets["openai"]["api_key"]
    st.sidebar.success("API Key berhasil dimuat.", icon="✅")
except (KeyError, FileNotFoundError):
    st.sidebar.error("API Key tidak ditemukan di st.secrets. Mohon tambahkan key Anda.", icon="🚨")
    openai_api_key = None

# Simpan API key di session state untuk digunakan di seluruh aplikasi.
st.session_state["openai_api_key"] = openai_api_key

# --- Bagian utama aplikasi ---
st.title("Aplikasi Chatbot dengan Streamlit")
st.write("Aplikasi ini menggunakan OpenAI API key yang sudah disediakan.")

# Contoh penggunaan API key (misalnya untuk memanggil model)
if st.session_state["openai_api_key"]:
    st.write("API key siap digunakan untuk berinteraksi dengan model OpenAI.")
    # Kode untuk interaksi dengan OpenAI bisa diletakkan di sini
else:
    st.write("Silakan konfigurasi API key di `st.secrets` untuk menggunakan aplikasi ini.")


# --- Fungsi Caching untuk Setup Mahal ---
@st.cache_resource
def _setup_database():
    """
    Sets up a file-based SQLite database, creates tables, and populates them with sample data.
    Returns a SQLAlchemy engine connected to the database.
    """
    conn = sqlite3.connect("business_data.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    if cursor.fetchone() is None:
        cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT,
            price REAL, stock_quantity INTEGER
        );""")
        cursor.execute("""
        CREATE TABLE sales (
            sale_id INTEGER PRIMARY KEY, product_id INTEGER, quantity_sold INTEGER,
            sale_date TEXT, channel TEXT, FOREIGN KEY (product_id) REFERENCES products (product_id)
        );""")
        products_data = [
            (1, 'Dell XPS 15', 'Laptop performa tinggi dengan layar OLED 4K.', 28500000, 30),
            (2, 'Apple MacBook Pro 14', 'Ditenagai chip M3 Pro, ideal untuk developer.', 35000000, 25),
            (3, 'Lenovo ThinkPad X1 Carbon', 'Laptop bisnis ultra-ringan dengan keyboard legendaris.', 25000000, 50),
            (4, 'Asus ROG Zephyrus G15', 'Laptop gaming dengan GPU RTX 4070.', 31000000, 20),
            (5, 'Acer Swift 3', 'Laptop tipis dan ringan untuk mahasiswa.', 12500000, 80),
            (6, 'HP Spectre x360', 'Laptop 2-in-1 konvertibel dengan desain premium.', 23500000, 40)
        ]
        sales_data = [
            (101, 1, 1, '2025-07-01', 'Online'), (102, 3, 2, '2025-07-01', 'In-Store'),
            (103, 5, 5, '2025-07-02', 'Online'), (104, 2, 1, '2025-07-03', 'In-Store'),
            (105, 4, 1, '2025-07-03', 'Online'), (106, 1, 1, '2025-07-04', 'In-Store'),
            (107, 6, 2, '2025-07-05', 'Online'), (108, 3, 1, '2025-07-05', 'Online'),
            (109, 5, 3, '2025-07-06', 'In-Store'), (110, 2, 1, '2025-07-07', 'Online')
        ]
        cursor.executemany("INSERT INTO products VALUES (?,?,?,?,?);", products_data)
        cursor.executemany("INSERT INTO sales VALUES (?,?,?,?,?);", sales_data)
        conn.commit()
    engine = create_engine("sqlite:///business_data.db", creator=lambda: conn, pool_recycle=3600, connect_args={'check_same_thread': False})
    return engine

@st.cache_resource
def setup_vector_stores(_openai_api_key):
    """
    Creates FAISS vector stores and returns RAG tools.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=_openai_api_key)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    internal_info_docs_raw = [
        Document(page_content="Kebijakan Pengembalian Produk: Pelanggan dapat mengembalikan produk dalam waktu 14 hari..."),
        Document(page_content="Informasi Garansi: Semua laptop memiliki garansi resmi pabrikan 1 tahun..."),
        Document(page_content="Panduan Memilih Laptop: Untuk desain grafis, pilih GPU dedicated dan RAM 16GB..."),
        Document(page_content="Metode Pembayaran: Kami menerima transfer bank, kartu kredit, dan dompet digital.")
    ]
    internal_info_vs = FAISS.from_documents(text_splitter.split_documents(internal_info_docs_raw), embeddings)
    conversation_history_docs_raw = [
        Document(page_content="Pelanggan (7 Juli 2025): 'Stok MacBook Pro 14 habis...'"),
        Document(page_content="Pelanggan (6 Juli 2025): 'Rekomendasi laptop untuk programmer...'"),
        Document(page_content="Pelanggan (5 Juli 2025): 'Laptop gaming Asus cepat panas...'"),
        Document(page_content="Pelanggan (4 Juli 2025): 'Budget 12 jutaan untuk mahasiswa IT...'")
    ]
    conversation_history_vs = FAISS.from_documents(text_splitter.split_documents(conversation_history_docs_raw), embeddings)
    return [
        Tool(name="product_and_faq_retriever", func=internal_info_vs.as_retriever().invoke, description="Mencari info produk, spesifikasi, kebijakan perusahaan, dan FAQ."),
        Tool(name="conversation_history_analyzer", func=conversation_history_vs.as_retriever().invoke, description="Menganalisis riwayat percakapan pelanggan untuk wawasan kualitatif.")
    ]

@st.cache_resource
def load_agent_executor(_openai_api_key):
    """
    Sets up all components and returns the main agent executor.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=_openai_api_key, streaming=True)
    db_engine = _setup_database()
    db = SQLDatabase(engine=db_engine)
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    rag_tools = setup_vector_stores(_openai_api_key)
    python_tool = Tool(name="python_code_interpreter", func=PythonREPLTool().run, description="Shell Python untuk eksekusi kode analisis data atau kalkulasi.")
    all_tools = sql_toolkit.get_tools() + rag_tools + [python_tool]
    
    prompt_template = hub.pull("hwchase17/react-chat")
    prompt_template.template = """
Anda adalah asisten AI ahli yang dirancang untuk membantu pengguna dengan pertanyaan terkait bisnis, analisis data, dan wawasan strategis. Anda harus beroperasi secara ketat menggunakan kerangka ReAct.

Selalu ikuti format ini:
Thought: Anda harus selalu berpikir tentang apa yang harus dilakukan.
Action: Tindakan yang harus diambil, salah satu dari [{tool_names}].
Action Input: Input untuk tindakan tersebut.
Observation: Hasil dari tindakan tersebut.
... (Siklus Thought/Action/Observation ini dapat berulang)
Thought: Saya sekarang memiliki cukup informasi untuk memberikan jawaban akhir.
Final Answer: Jawaban akhir untuk pertanyaan asli.

Pedoman Operasional:
1.  **Evaluasi Hasil (PENTING):** Setelah setiap `Observation`, evaluasi apakah informasi tersebut sudah cukup untuk menjawab pertanyaan pengguna. Jika tidak, jangan langsung memberikan jawaban. Pikirkan (`Thought`) kembali dan gunakan tool lain yang lebih sesuai untuk melengkapi informasi.
2.  **User Flow (Hirarki Tool):**
    * Untuk pertanyaan spesifik tentang **stok, harga, atau data numerik** dari produk, **selalu prioritaskan** penggunaan tool `sql_db_query`.
    * Untuk pertanyaan tentang **kebijakan (garansi, retur), panduan umum, atau deskripsi fitur**, gunakan `product_and_faq_retriever`.
    * **Jika `product_and_faq_retriever` tidak memberikan jawaban yang spesifik (misalnya tentang ketersediaan stok), Anda HARUS mencoba `sql_db_query` pada langkah berikutnya untuk mendapatkan jawaban definitif.**
3.  **Admin Flow:** Untuk analisis (rata-rata, total), gunakan `sql_db_query` untuk mengambil data, lalu `python_code_interpreter` untuk menghitung.
4.  **Daily Recap Flow:** Gunakan `sql_db_query` untuk data penjualan kuantitatif dan `conversation_history_analyzer` untuk wawasan kualitatif dari interaksi pelanggan. Sintesiskan keduanya untuk laporan yang komprehensif.

Mulai!

Pertanyaan: {input}

{agent_scratchpad}
"""
    agent = create_react_agent(llm, all_tools, prompt_template)
    return AgentExecutor(agent=agent, tools=all_tools, verbose=True, max_iterations=7, handle_parsing_errors=True)

# --- Fungsi Halaman ---

def handle_chat_interaction(prompt, page_key, agent_executor):
    """Handles the agent streaming and UI updates for a chat interaction."""
    st.session_state[page_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        thinking_process = ""
        thinking_expander = st.expander("Lihat Alur Berpikir Agen (Real-time)", expanded=True)
        thinking_placeholder = thinking_expander.empty()
        answer_placeholder = st.empty()
        answer_placeholder.markdown("▌")

        full_response = ""
        try:
            for chunk in agent_executor.stream({"input": prompt}):
                if "actions" in chunk:
                    for action in chunk["actions"]:
                        thinking_process += f"**Thought:** {action.log.strip().split('Action:')[0]}\n"
                        thinking_process += f"**Action:** `{action.tool}`\n"
                        thinking_process += f"**Action Input:** `{action.tool_input}`\n\n"
                        thinking_placeholder.code(thinking_process, language="markdown")
                elif "steps" in chunk:
                    for step in chunk["steps"]:
                        thinking_process += f"**Observation:**\n```\n{step.observation}\n```\n\n"
                        thinking_placeholder.code(thinking_process, language="markdown")
                elif "output" in chunk:
                    full_response = chunk["output"]
                    answer_placeholder.markdown(full_response)
                else:
                    thinking_process += f"---\n{str(chunk)}\n---\n"
                    thinking_placeholder.code(thinking_process, language="markdown")
        except Exception as e:
            full_response = f"Terjadi error: {e}"
            answer_placeholder.error(full_response)

    st.session_state[page_key].append({
        "role": "assistant", 
        "content": full_response,
        "thinking": thinking_process
    })

def chat_page(page_title, session_state_key, agent_executor):
    st.header(f"💬 {page_title}")
    st.caption("Ajukan pertanyaan Anda. Alur berpikir agen akan ditampilkan secara real-time.")
    
    if session_state_key not in st.session_state:
        st.session_state[session_state_key] = []

    for message in st.session_state[session_state_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "thinking" in message and message["thinking"]:
                with st.expander("Lihat Alur Berpikir Agen"):
                    st.code(message["thinking"], language="markdown")

    if prompt := st.chat_input("Tulis pertanyaan Anda di sini..."):
        handle_chat_interaction(prompt, session_state_key, agent_executor)


def daily_insight_page(agent_executor):
    st.header("📈 Daily Insight Generator")
    st.caption("Pilih tanggal untuk membuat ringkasan penjualan dan interaksi pelanggan.")
    
    today = date.today()
    selected_date = st.date_input("Pilih Tanggal", value=today, max_value=today)

    if st.button("Buat Laporan Insight Harian", type="primary"):
        query = (
            f"Buatkan saya ringkasan insight harian untuk tanggal {selected_date.strftime('%Y-%m-%d')}. "
            "Gunakan data penjualan untuk tren kuantitatif dan riwayat percakapan untuk wawasan kualitatif. "
            "Sajikan dalam format laporan yang jelas."
        )
        st.info(f"**Menganalisis data untuk tanggal:** {selected_date.strftime('%Y-%m-%d')}")
        
        with st.container(border=True):
            thinking_process = ""
            thinking_expander = st.expander("Lihat Alur Berpikir Agen (Real-time)", expanded=True)
            thinking_placeholder = thinking_expander.empty()
            answer_placeholder = st.empty()
            answer_placeholder.markdown("▌")

            try:
                for chunk in agent_executor.stream({"input": query}):
                    if "actions" in chunk:
                        for action in chunk["actions"]:
                            thinking_process += f"**Thought:** {action.log.strip().split('Action:')[0]}\n**Action:** `{action.tool}`\n**Action Input:** `{action.tool_input}`\n\n"
                            thinking_placeholder.code(thinking_process, language="markdown")
                    elif "steps" in chunk:
                        for step in chunk["steps"]:
                            thinking_process += f"**Observation:**\n```\n{step.observation}\n```\n\n"
                            thinking_placeholder.code(thinking_process, language="markdown")
                    elif "output" in chunk:
                        answer_placeholder.markdown(chunk["output"])
            except Exception as e:
                answer_placeholder.error(f"Terjadi error: {e}")

def edit_data_page():
    """Page for editing data in the database tables."""
    st.header("✏️ Edit Data Database")
    st.caption("Ubah data secara langsung di tabel di bawah ini dan klik 'Simpan Perubahan'.")

    conn = sqlite3.connect("business_data.db", check_same_thread=False)
    
    if 'products_df' not in st.session_state:
        st.session_state.products_df = pd.read_sql("SELECT * FROM products", conn)
    if 'sales_df' not in st.session_state:
        st.session_state.sales_df = pd.read_sql("SELECT * FROM sales", conn)

    st.subheader("Tabel Produk")
    edited_products = st.data_editor(st.session_state.products_df, num_rows="dynamic", key="products_editor")
    st.subheader("Tabel Penjualan")
    edited_sales = st.data_editor(st.session_state.sales_df, num_rows="dynamic", key="sales_editor")

    if st.button("Simpan Perubahan", type="primary"):
        try:
            edited_products.to_sql("products", conn, if_exists="replace", index=False)
            edited_sales.to_sql("sales", conn, if_exists="replace", index=False)
            st.session_state.products_df = edited_products
            st.session_state.sales_df = edited_sales
            st.success("Perubahan berhasil disimpan ke database!")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal menyimpan perubahan: {e}")
        finally:
            conn.close()


# --- Main App Logic ---
# Aplikasi utama hanya berjalan jika API key sudah tersedia.
if not st.session_state.get("openai_api_key"):
    st.info("Harap masukkan OpenAI API Key Anda di sidebar untuk memulai.")
    st.stop()

try:
    agent_executor = load_agent_executor(st.session_state.openai_api_key)
except Exception as e:
    st.error(f"Gagal memuat agen. Pastikan API Key Anda valid. Error: {e}")
    st.stop()

st.sidebar.title("🤖 Navigasi Dashboard")
st.sidebar.markdown("Pilih halaman untuk berinteraksi dengan agen AI.")
page = st.sidebar.radio(
    "Pilih Halaman:",
    ("User Flow", "Admin Flow", "Daily Insight", "Edit Data"),
    captions=["Tanya jawab umum.", "Analisis data mendalam.", "Laporan harian otomatis.", "Ubah data tabel."]
)

if page == "User Flow":
    chat_page("User Flow", "messages_user", agent_executor)
elif page == "Admin Flow":
    chat_page("Admin Flow", "messages_admin", agent_executor)
elif page == "Daily Insight":
    daily_insight_page(agent_executor)
elif page == "Edit Data":
    edit_data_page()
