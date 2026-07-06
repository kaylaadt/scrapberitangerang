import os
os.system("playwright install")

import streamlit as st
import asyncio
import pandas as pd
from datetime import date
from io import BytesIO
import base64

from scraping_api import jalankan_scraping

st.set_page_config(
    page_title="Scraping Berita Kabupaten Tangerang",
    page_icon="📰",
    layout="wide"
)

with open("logo_bps.png", "rb") as f:
    logo = base64.b64encode(f.read()).decode()

st.markdown("""
<style>


/* Mengurangi jarak atas */
.block-container{
    padding-top:0.7rem;
}
            
/* Garis bawah header */
hr{
    border: none !important;
    height: 6px !important;
    background: linear-gradient(90deg,#0072BC,#00AEEF,#F7941D) !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)

col_logo, col_title, col_kosong = st.columns([1.5, 4, 0.7])

with col_logo:
    st.image("logo_bps.png", use_container_width=True)

with col_title:
    st.markdown("""
    <h1 style="
        text-align:center;
        color:white;
        font-size:42px;
        margin-top:20px;
        margin-bottom:0px;">
        Scraping Berita Kabupaten Tangerang
    </h1>
    """, unsafe_allow_html=True)

with col_kosong:
    st.empty()

st.markdown("<hr>", unsafe_allow_html=True)

# ============================
# INPUT
# ============================

sumber = st.radio(
    "Pilih Sumber Berita",
    ["TangerangKab", "TangerangNews"]
)

keyword = st.text_input(
    "Keyword",
    placeholder="Contoh: banjir"
)

col1, col2 = st.columns(2)

with col1:
    tanggal_mulai = st.date_input(
        "Tanggal Mulai",
        value=date.today()
    )

with col2:
    tanggal_akhir = st.date_input(
        "Tanggal Akhir",
        value=date.today()
    )

if sumber == "TangerangKab":
    jumlah = st.number_input(
        "Klik 'Muat Berita Lainnya' berapa kali?",
        min_value=0,
        value=1,
        step=1
    )
else:
    jumlah = st.number_input(
        "Ambil sampai halaman berapa?",
        min_value=1,
        value=1,
        step=1
    )

# ============================
# BUTTON
# ============================

if st.button("🔍 Cari Berita"):

    if keyword.strip() == "":
        st.warning("Masukkan keyword terlebih dahulu.")
        st.stop()

    with st.spinner("Sedang melakukan scraping..."):

        df = asyncio.run(
            jalankan_scraping(
                sumber=sumber,
                keyword=keyword,
                tanggal_mulai=pd.to_datetime(tanggal_mulai),
                tanggal_akhir=pd.to_datetime(tanggal_akhir),
                jumlah=int(jumlah)
            )
        )

    st.success(f"Berhasil menemukan {len(df)} berita")

    df_tampil = df.copy()
    df_tampil.insert(0, "No", range(1, len(df_tampil) + 1))
    
    st.dataframe(
        df_tampil,
        use_container_width=True,
        hide_index=True
    )

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Hasil Scraping"
        )

    st.download_button(
        label="📥 Download Excel",
        data=output.getvalue(),
        file_name=f"hasil_{sumber}_{keyword}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ============================
# FOOTER
# ============================

st.markdown("""
<div style="
    text-align:center;
    color:#9E9E9E;
    font-size:13px;
    margin-top:60px;
    margin-bottom:10px;">
    Dibuat dengan ❤️ oleh
    <span style="color:#8A2BE2;font-weight:600;">
        Kayla Tsabithah
    </span>
</div>
""", unsafe_allow_html=True)
