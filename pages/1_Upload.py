import streamlit as st, time
from datetime import datetime
from pathlib import Path
from db import insert_letter
from utils.ocr import ocr_space_file
from utils.ai import analyse_text_with_groq

st.title("📥 Upload Surat Masuk")

if "role" not in st.session_state:
    st.warning("Silakan login di halaman utama.")
    st.stop()

uploader = st.session_state.get("role","")  # kita simpan nama user di username juga boleh
division_user = st.session_state.get("division","Umum")

with st.form("upload_form"):
    penerima_nama = st.text_input("Nama Penerima (Bagian Umum / staf):", value="")
    file = st.file_uploader("File Surat (PDF/JPG/PNG)", type=["pdf","jpg","jpeg","png"])
    submitted = st.form_submit_button("Upload & Proses")

if submitted:
    if not file:
        st.error("Pilih file dulu.")
        st.stop()

    # simpan file ke data/letters
    folder = Path("data/letters"); folder.mkdir(parents=True, exist_ok=True)
    save_path = folder / f"{int(time.time())}_{file.name}"
    with open(save_path, "wb") as f:
        f.write(file.read())

    st.info("🔍 OCR in progress…")
    try:
        text = ocr_space_file(str(save_path), api_key=st.secrets["OCR_SPACE_KEY"], language="eng")
        st.success("OCR selesai.")
    except Exception as e:
        st.error(f"OCR gagal: {e}")
        text = ""

    ai_nomor = ai_maksud = ai_rekom = None
    status = "Pending"
    if text:
        st.info("🤖 Analisa AI (Groq)…")
        try:
            out = analyse_text_with_groq(text)
            ai_nomor = out["nomor_surat_pengirim"]
            ai_maksud = out["maksud_surat"]
            ai_rekom = out["rekomendasi_divisi"]
            status = "Analisa Selesai"
            st.success("Analisa AI selesai.")
        except Exception as e:
            st.warning(f"Analisa AI gagal: {e}")
            status = "OCR Selesai"

    nomor_internal = datetime.now().strftime("%Y/%m/") + f"{int(time.time())%1000:03d}"

    letter_id = insert_letter(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        uploader=username if (username:=st.session_state.get("username")) else "user",
        division=division_user,
        filename=file.name,
        file_path=str(save_path),
        ocr_text=text,
        ai_nomor_pengirim=ai_nomor,
        ai_maksud=ai_maksud,
        ai_rekomendasi=ai_rekom,
        nomor_internal=nomor_internal,
        status=status
    )

    st.success(f"Sukses simpan surat ID #{letter_id} — Nomor Internal: {nomor_internal}")
    st.link_button("Lihat Dashboard", "/2_Dashboard")
