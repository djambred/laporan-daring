#!/bin/bash
# Script untuk menjalankan 2 Aplikasi Streamlit

echo "🚀 Memulai Sistem Laporan Kuliah..."
echo ""
echo "📝 Aplikasi Dosen: http://localhost:8501"
echo "✍️  Aplikasi Mahasiswa: http://localhost:8502"
echo ""
echo "💡 Tekan Ctrl+C untuk menghentikan kedua aplikasi"
echo ""

# Jalankan aplikasi dosen di background
echo "🔵 Starting Dosen App (Port 8501)..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 &
DOSEN_PID=$!

# Tunggu sebentar
sleep 2

# Jalankan aplikasi mahasiswa di background
echo "🟢 Starting Mahasiswa App (Port 8502)..."
streamlit run mahasiswa_app.py --server.port=8502 --server.address=0.0.0.0 &
MAHASISWA_PID=$!

echo ""
echo "✅ Kedua aplikasi berhasil dijalankan!"
echo ""
echo "📊 Dosen App PID: $DOSEN_PID"
echo "📋 Mahasiswa App PID: $MAHASISWA_PID"
echo ""

# Fungsi cleanup saat Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Menghentikan aplikasi..."
    kill $DOSEN_PID 2>/dev/null
    kill $MAHASISWA_PID 2>/dev/null
    echo "✅ Aplikasi dihentikan"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait
