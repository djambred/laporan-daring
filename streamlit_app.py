#!/usr/bin/env python3
"""
Generator Laporan Kuliah Daring - Simple Version
Semua dalam 1 halaman, mobile-friendly
"""

import os
import json
import tempfile
import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd
import base64
from io import BytesIO

from utils_simple import (
    validate_laporan_data,
    generate_simple_pdf
)

# Configure
st.set_page_config(
    page_title="Laporan Kuliah",
    page_icon="📝",
    layout="wide"
)

# Data files
DATA_FILE = Path('laporan_data.json')
OUTPUT_DIR = Path('laporan_output')
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    """Load data dari JSON"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            for key in ['matkul', 'sks', 'dosen', 'prodi', 'jam', 'tanggal', 'ttd_tempat', 'ttd_tanggal', 'ttd_nama', 'link_presentasi', 'link_rekaman']:
                if key in data and data[key] is not None:
                    data[key] = str(data[key])
            return data
    return empty_data()


def empty_data():
    """Data kosong dengan default"""
    return {
        'matkul': '',
        'sks': '',
        'dosen': 'Dra. Asmawati M.Pd',
        'prodi': '',
        'jam': '',
        'tanggal': '',
        'mahasiswa': [],
        'catatan': [],
        'ttd_tempat': 'Lubuk Alung',
        'ttd_tanggal': '',
        'ttd_nama': 'Dra. Asmawati M.Pd',
        'link_presentasi': '',
        'link_rekaman': '',
        'signature': None
    }


def save_data(data):
    """Save data"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    """Main app dengan menu navigasi"""
    
    st.title("📝 Laporan Kuliah Daring")
    
    # Load data
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    
    # Menu state
    if 'menu' not in st.session_state:
        st.session_state.menu = "info"
    
    data = st.session_state.data
    
    # NAVIGATION BUTTONS - Mobile Friendly
    st.markdown("### 📋 Menu")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📚 Informasi", use_container_width=True, type="primary" if st.session_state.menu == "info" else "secondary"):
            st.session_state.menu = "info"
            st.rerun()
    
    with col2:
        if st.button("👥 Mahasiswa", use_container_width=True, type="primary" if st.session_state.menu == "mahasiswa" else "secondary"):
            st.session_state.menu = "mahasiswa"
            st.rerun()
    
    with col3:
        if st.button("✍️ Tanda Tangan", use_container_width=True, type="primary" if st.session_state.menu == "ttd" else "secondary"):
            st.session_state.menu = "ttd"
            st.rerun()
    
    with col4:
        if st.button("📥 Generate", use_container_width=True, type="primary" if st.session_state.menu == "generate" else "secondary"):
            st.session_state.menu = "generate"
            st.rerun()
    
    # ========== MENU 1: INFORMASI KULIAH ==========
    if st.session_state.menu == "info":
        st.markdown("## 📚 Informasi Kuliah")
        
        col1, col2 = st.columns(2)
        with col1:
            data['matkul'] = st.text_input("Mata Kuliah", value=data.get('matkul', ''))
            data['sks'] = st.text_input("SKS/Semester", value=data.get('sks', ''), placeholder="2 SKS / Semester 3")
            data['prodi'] = st.text_input("Program Studi", value=data.get('prodi', ''))
        
        with col2:
            data['jam'] = st.text_input("Jam", value=data.get('jam', ''), placeholder="10:00 - 12:00")
            tanggal_input = st.date_input("Tanggal")
            data['tanggal'] = tanggal_input.strftime("%d %B %Y")
            data['dosen'] = st.text_input("Dosen", value=data.get('dosen', 'Dra. Asmawati M.Pd'))
        
        st.divider()
        
        # Catatan
        st.markdown("### 📝 Catatan Perkuliahan")
        catatan = data.get('catatan', [])
        
        if catatan:
            for i, note in enumerate(catatan, 1):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"{i}. {note}")
                with col2:
                    if st.button("❌", key=f"del_{i}"):
                        catatan.pop(i-1)
                        data['catatan'] = catatan
                        st.rerun()
        
        catatan_baru = st.text_area("Tambah catatan", key="catatan_baru")
        if st.button("➕ Tambah Catatan"):
            if catatan_baru:
                catatan.append(catatan_baru)
                data['catatan'] = catatan
                st.success("✅ Catatan ditambahkan")
                st.rerun()
        
        st.divider()
        
        # Links
        st.markdown("### 🔗 Link")
        col1, col2 = st.columns(2)
        with col1:
            data['link_presentasi'] = st.text_input("Link Presentasi", value=data.get('link_presentasi', ''))
        with col2:
            data['link_rekaman'] = st.text_input("Link Rekaman", value=data.get('link_rekaman', ''))
        
        if st.button("💾 Simpan", use_container_width=True, type="primary"):
            save_data(data)
            st.success("✅ Data disimpan")
    
    # ========== MENU 2: DAFTAR HADIR MAHASISWA (READ-ONLY) ==========
    elif st.session_state.menu == "mahasiswa":
        st.markdown("## 👥 Daftar Hadir Mahasiswa")
        
        st.info("📌 Data absensi diinput oleh mahasiswa melalui **Form Absensi (Port 8502)**")
        
        mahasiswa = data.get('mahasiswa', [])
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.data = load_data()
            st.rerun()
        
        st.divider()
        
        # Stats
        if mahasiswa:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", len(mahasiswa))
            with col2:
                hadir = len([m for m in mahasiswa if m['status'] == 'Hadir'])
                st.metric("Hadir", hadir)
            with col3:
                tidak_hadir = len([m for m in mahasiswa if m['status'] == 'Tidak Hadir'])
                st.metric("Tidak Hadir", tidak_hadir)
            with col4:
                lainnya = len([m for m in mahasiswa if m['status'] in ['Izin', 'Sakit']])
                st.metric("Izin/Sakit", lainnya)
            
            st.divider()
        
        # View only - Display data
        if mahasiswa:
            # Search
            search = st.text_input("🔍 Cari mahasiswa (ketik nama)", key="search_mhs")
            
            # Filter and display
            display_list = mahasiswa
            if search:
                display_list = [m for m in mahasiswa if search.lower() in m['nama'].lower()]
            
            if display_list:
                st.write(f"📊 Menampilkan {len(display_list)} dari {len(mahasiswa)} mahasiswa")
                st.divider()
                
                # Table view
                for i, mhs in enumerate(display_list, 1):
                    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                    
                    with col1:
                        st.write(f"**{i}.**")
                    with col2:
                        st.write(f"**{mhs['nama']}**")
                    with col3:
                        st.write(f"NPM: {mhs.get('npm', '-')}")
                    with col4:
                        status_icon = "✅" if mhs['status'] == 'Hadir' else "❌" if mhs['status'] == 'Tidak Hadir' else "⚠️"
                        st.write(f"{status_icon} {mhs['status']}")
                    
                    # Show timestamp if available
                    if mhs.get('waktu_absen'):
                        st.caption(f"⏰ Absen: {mhs.get('waktu_absen')}")
                    
                    # Show keterangan if available
                    if mhs.get('keterangan'):
                        st.caption(f"💬 {mhs.get('keterangan')}")
                    
                    st.divider()
            else:
                st.info("Tidak ditemukan")
        
        else:
            st.warning("⚠️ Belum ada data absensi. Mahasiswa dapat mengisi absensi di **http://localhost:8502**")
        
        st.divider()
        
        # Option to clear all data
        with st.expander("🗑️ Hapus Semua Data Absensi"):
            st.warning("⚠️ Akan menghapus SEMUA data absensi mahasiswa!")
            if st.button("Hapus Semua Absensi", type="secondary"):
                data['mahasiswa'] = []
                save_data(data)
                st.success("✅ Data absensi dihapus")
                st.rerun()
    
    # ========== MENU 3: TANDA TANGAN ==========
    elif st.session_state.menu == "ttd":
        st.markdown("## ✍️ Tanda Tangan")
        
        col1, col2 = st.columns(2)
        with col1:
            ttd_tanggal = st.date_input("Tanggal TTD")
            data['ttd_tanggal'] = ttd_tanggal.strftime("%d %B %Y")
        with col2:
            data['ttd_tempat'] = st.text_input("Tempat", value=data.get('ttd_tempat', 'Lubuk Alung'))
        
        st.markdown("### 🖊️ Gambar Tanda Tangan")
        try:
            from streamlit_drawable_canvas import st_canvas
            
            canvas_result = st_canvas(
                stroke_width=3,
                stroke_color="rgb(0, 0, 0)",
                background_color="rgb(255, 255, 255)",
                height=250,
                width=600,
                drawing_mode="freedraw",
                key="ttd_canvas"
            )
            
            if canvas_result.image_data is not None:
                # Save signature
                from PIL import Image
                import io
                img = Image.fromarray(canvas_result.image_data.astype('uint8'))
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                data['signature'] = base64.b64encode(buffered.getvalue()).decode()
                st.success("✅ Tanda tangan tersimpan")
        except:
            st.warning("Install: pip install streamlit-drawable-canvas")
        
        if st.button("💾 Simpan", use_container_width=True, type="primary"):
            save_data(data)
            st.success("✅ Data disimpan")
    
    # ========== MENU 4: GENERATE PDF ==========
    elif st.session_state.menu == "generate":
        st.markdown("## 🎯 Generate PDF")
        
        # Preview info
        st.markdown("### 📊 Preview Data")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Mata Kuliah:** {data.get('matkul', '-')}")
            st.write(f"**Dosen:** {data.get('dosen', '-')}")
            st.write(f"**Tanggal:** {data.get('tanggal', '-')}")
        with col2:
            mahasiswa = data.get('mahasiswa', [])
            hadir = len([m for m in mahasiswa if m['status'] == 'Hadir'])
            st.write(f"**Total Mahasiswa:** {len(mahasiswa)}")
            st.write(f"**Hadir:** {hadir}")
            st.write(f"**Catatan:** {len(data.get('catatan', []))} item")
        
        st.divider()
        
        # Upload foto
        st.markdown("### 📸 Upload Foto Dokumentasi")
        st.info("📌 Upload max 8 foto (4 foto per halaman)")
        uploaded_files = st.file_uploader("Pilih foto", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} foto siap diupload")
        
        st.divider()
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Simpan Data", use_container_width=True):
                save_data(data)
                st.success("✅ Data disimpan")
        
        with col2:
            if st.button("🗑️ Hapus Semua", use_container_width=True):
                if st.session_state.get('confirm_delete'):
                    data = empty_data()
                    st.session_state.data = data
                    if DATA_FILE.exists():
                        os.unlink(DATA_FILE)
                    st.session_state.confirm_delete = False
                    st.success("✅ Data dihapus")
                    st.rerun()
                else:
                    st.session_state.confirm_delete = True
                    st.warning("⚠️ Klik sekali lagi untuk konfirmasi hapus")
        
        with col3:
            if st.button("📥 Generate PDF", use_container_width=True, type="primary"):
                # Validasi
                is_valid, msg = validate_laporan_data(data)
                if not is_valid:
                    st.error(msg)
                else:
                    with st.spinner('⏳ Generating PDF...'):
                        try:
                            # Save current data
                            save_data(data)
                            
                            # Process photos
                            photo_paths = []
                            if uploaded_files:
                                st.write("📤 Processing photos...")
                                for file in uploaded_files[:8]:  # Max 8 foto
                                    file_ext = Path(file.name).suffix.lower() or '.jpg'
                                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
                                    temp_file.write(file.getbuffer())
                                    temp_file.close()
                                    photo_paths.append(temp_file.name)
                            
                            # Generate PDF
                            st.write("📄 Creating PDF...")
                            pdf_path = generate_simple_pdf(data, photo_paths)
                            
                            # Read PDF to memory
                            with open(pdf_path, 'rb') as f:
                                pdf_data = f.read()
                            
                            # Store in session state
                            st.session_state.pdf_data = pdf_data
                            st.session_state.pdf_filename = f"Laporan_{data['matkul'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            
                            # Cleanup
                            os.unlink(pdf_path)
                            for photo in photo_paths:
                                try:
                                    os.unlink(photo)
                                except:
                                    pass
                            
                            st.success("✅ PDF berhasil dibuat!")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        # Show download button if PDF ready
        if 'pdf_data' in st.session_state and st.session_state.pdf_data:
            st.divider()
            st.download_button(
                label="⬇️ Download PDF",
                data=st.session_state.pdf_data,
                file_name=st.session_state.pdf_filename,
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )


if __name__ == "__main__":
    main()
