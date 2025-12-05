#!/bin/bash
# Script untuk menjalankan Aplikasi Mahasiswa saja

echo "🚀 Memulai Aplikasi Mahasiswa..."
echo ""
echo "✍️ Aplikasi akan berjalan di: http://localhost:8502"
echo "💡 Tekan Ctrl+C untuk menghentikan"
echo ""

streamlit run mahasiswa_app.py --server.port=8502 --server.address=0.0.0.0
