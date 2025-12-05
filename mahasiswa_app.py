#!/usr/bin/env python3
"""
Form Absensi Mahasiswa - Port 8502
Aplikasi terpisah untuk mahasiswa input absensi
"""

import json
import streamlit as st
from pathlib import Path
from datetime import datetime

# Configure
st.set_page_config(
    page_title="Absensi Mahasiswa",
    page_icon="✍️",
    layout="centered"
)

# Data file - SAMA dengan aplikasi dosen
DATA_FILE = Path('laporan_data.json')

def load_data():
    """Load data dari JSON"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'mahasiswa': []}

def save_data(data):
    """Save data ke JSON"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    """Form absensi mahasiswa"""
    
    st.title("✍️ Form Absensi Mahasiswa")
    st.markdown("---")
    
    # Load data
    data = load_data()
    
    # Show info kuliah if available
    if data.get('matkul'):
        st.info(f"📚 **{data.get('matkul', '')}** - {data.get('dosen', '')} ({data.get('tanggal', '')})")
    
    st.markdown("### Isi Data Absensi Anda")
    
    # Form
    with st.form("form_absensi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nama = st.text_input("Nama Lengkap *", placeholder="Contoh: Budi Santoso")
        
        with col2:
            npm = st.text_input("NPM (opsional)", placeholder="Contoh: 20210001")
        
        status = st.selectbox("Status Kehadiran *", ["Hadir", "Tidak Hadir", "Izin", "Sakit"])
        
        keterangan = st.text_area("Keterangan (opsional)", placeholder="Tulis keterangan jika ada...")
        
        submitted = st.form_submit_button("✅ Kirim Absensi", use_container_width=True, type="primary")
        
        if submitted:
            if nama:
                mahasiswa = data.get('mahasiswa', [])
                
                # Check if already exists by name
                existing = next((m for m in mahasiswa if m['nama'].lower() == nama.lower()), None)
                
                if existing:
                    # Update existing
                    existing['status'] = status
                    if npm:
                        existing['npm'] = npm
                    if keterangan:
                        existing['keterangan'] = keterangan
                    existing['waktu_absen'] = datetime.now().strftime("%H:%M:%S")
                    st.success(f"✅ Absensi **{nama}** berhasil diperbarui!")
                else:
                    # Add new
                    new_entry = {
                        'nama': nama,
                        'npm': npm if npm else '-',
                        'status': status,
                        'waktu_absen': datetime.now().strftime("%H:%M:%S")
                    }
                    if keterangan:
                        new_entry['keterangan'] = keterangan
                    
                    mahasiswa.append(new_entry)
                    st.success(f"✅ Absensi **{nama}** berhasil disimpan!")
                
                data['mahasiswa'] = mahasiswa
                save_data(data)
                st.balloons()
                
            else:
                st.error("❌ Nama harus diisi!")
    
    st.markdown("---")
    
    # Show current attendance
    mahasiswa = data.get('mahasiswa', [])
    if mahasiswa:
        st.markdown("### 📋 Daftar Absensi Hari Ini")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", len(mahasiswa))
        with col2:
            hadir = len([m for m in mahasiswa if m['status'] == 'Hadir'])
            st.metric("Hadir", hadir)
        with col3:
            tidak_hadir = len([m for m in mahasiswa if m['status'] != 'Hadir'])
            st.metric("Tidak Hadir", tidak_hadir)
        
        st.markdown("---")
        
        # List
        for i, mhs in enumerate(mahasiswa, 1):
            status_icon = "✅" if mhs['status'] == 'Hadir' else "❌"
            waktu = mhs.get('waktu_absen', '-')
            st.write(f"{i}. {status_icon} **{mhs['nama']}** ({mhs.get('npm', '-')}) - {mhs['status']} - {waktu}")
    else:
        st.info("Belum ada yang absen hari ini")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "<small>Form Absensi Mahasiswa | Port 8502</small>"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
