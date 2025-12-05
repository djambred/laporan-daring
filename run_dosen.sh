#!/bin/bash
# Script untuk menjalankan Aplikasi Dosen saja

echo "🚀 Memulai Aplikasi Dosen..."
echo ""
echo "📝 Aplikasi akan berjalan di: http://localhost:8501"
echo "💡 Tekan Ctrl+C untuk menghentikan"
echo ""

streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
