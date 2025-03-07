# Gunakan image Python 3.11 sebagai dasar
FROM python:3.11

# Set direktori kerja dalam container
WORKDIR /app

# Salin file requirements ke container
COPY requirements.txt .

# Install dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi folder `scr` ke dalam container
COPY src/ ./src/

# Buka port untuk Flask (5000) dan Streamlit (8501)
EXPOSE 5000 8501

# Jalankan Flask dan Streamlit secara bersamaan
CMD ["bash", "-c", "python src/main.py & streamlit run src/dashboard.py --server.port=8501 --server.address=0.0.0.0"]
