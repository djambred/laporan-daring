# Optimized Dockerfile untuk Streamlit App
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables untuk Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements terlebih dahulu untuk better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy aplikasi Streamlit
COPY streamlit_app.py .
COPY utils.py .

# Copy environment jika ada
COPY .env* ./

# Create temp directory untuk file sementara
RUN mkdir -p /tmp/laporan_temp /root/.streamlit

# Expose Streamlit port
EXPOSE 8501

# Health check untuk Streamlit
HEALTHCHECK --interval=30s --timeout=5s --start-period=3s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
