import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from db import add_disposition

DB_PATH = "data/tirtaflow.db"

st.title("📄 Detail Surat & Disposisi")

if "role" not in st.session_state:
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

role = st.session_state["role"]
division = st.session_state["division"]
username = st.session_state.get("username", "unknown")

# ---------- helper baca surat & riwayat ----------
def get_letter(letter_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM letters WHERE id = ?", (letter_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_disposition_history(letter_id: int) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM dispositions WHERE letter_id = ? ORDER BY created_at",
        conn,
        params=(letter_id,),
    )
    conn.close()
    return df

# ---------- input ID surat ----------
default_id = st.session_state.get("selected_letter_id", 1)
letter_id = st.number_input(
    "Masukkan ID Surat",
    min_value=1,
    step=1,
    value=int(default_id),
)

col_a, col_b = st.columns(2)
with col_a:
    go = st.button("Tampilkan")
with col_b:
    if st.button("Bersihkan pilihan ID"):
        st.session_state.pop("selected_letter_id", None)

# Kalau datang dari Dashboard (selected_letter_id ada), auto-tampilkan
auto_show = "selected_letter_id" in st.session_state

if not go and not auto_show:
    st.stop()

# ---------- dari sini ke bawah: pakai letter_id yang sudah dipilih ----------
letter = get_letter(int(letter_id))
if not letter:
    st.error(f"Surat dengan ID {letter_id} tidak ditemukan.")
    st.stop()

# (lanjutan file: Info Surat, Riwayat Disposisi, Form Disposisi)
