
# People Detection & Tracking System

## 🎯 Checklist Fitur
✔ **Desain Database  (Done)**  

✔ **Pengumpulan Dataset (Done)**  ket: lebih lengkap dibawah

✔ **Object Detection & Tracking (Done)**  Keterangan: Video feed Live, object detection dan tracking berjalan

✔ **Counting & Polygon Area  (Done)** Keterangan: Counting di Polygon area berfungsi, area polygon dynamis (dapat diatur user)

❌ **Prediksi (Forecasting) (X)** keterangan: Menampilkan hasil deteksi, counting kurang prediksi, kendala = waktu

✔ **Integrasi API (API/Front End) (Done)**  Ket: lebih lengkap dibawah

✔ **Deployment (Done)**  Docker

---
## 📌 Overview
Sistem deteksi dan pelacakan orang menggunakan **YOLO11** yang dikembangkan dengan **Flask** sebagai backend dan **Streamlit** sebagai frontend. Sistem ini juga menyimpan hasil deteksi dan area poligon ke **MongoDB Atlas** untuk integrasi API.

---
![dynamic polygon](https://img.mesinpintar.com/poligon2.gif)




## ⚙️ Desain

1. **Backend (Flask - `main.py`)**
   - Menyediakan API untuk streaming video dengan deteksi objek.
   - Menyimpan dan mengambil area deteksi dari MongoDB Atlas.
   - Menghitung statistik orang masuk, keluar, dan yang berada di dalam area.

2. **Frontend (Streamlit - `dashboard.py`)**
   - Menampilkan video streaming dari backend.
   - Memvisualisasikan statistik deteksi orang.
   - Memungkinkan pengguna menggambar area deteksi dan menyimpannya ke database.

3. **Desain Database (MongoDB Atlas - NoSQL)**
   - **Collection `area`**: Menyimpan koordinat poligon untuk area deteksi. Berisi`area_coords` dan `area_name`
   - **Collection `people`**: Menyimpan `track_id` orang dan aksi (`IN` atau `OUT`) serta `datetime`
   - **Collection `counter`**: Menyimpan data terbaru dari `inside_count`, `in_count`, `out_count`, dan `area_coords`

![tracking]((https://img.mesinpintar.com/tracking-compress.gif)
 
4. **Pertimbangan Desain**
Desain Sistem untuk Mengambil Input Video dan Melakukan Deteksi
Pipeline Deteksi:
  - Sistem akan menerima input berupa streaming video atau file video.
  - Gunakan framework deteksi seperti OpenCV untuk membaca frame dari video secara real-time.
 - Jalankan algoritma deteksi objek (`YOLO`) untuk mendeteksi keberadaan manusia di setiap frame.
- Setiap objek yang terdeteksi akan diberi `track_id` unik menggunakan algoritma pelacakan.

Validasi dengan Area Deteksi:           
- Setelah manusia terdeteksi, koordinat mereka (bounding box atau titik tengah) akan dibandingkan dengan koleksi area di database.
- Validasi apakah objek berada di dalam atau di luar area poligon yang telah dikonfigurasi.

Penyimpanan Hasil Deteksi:
- Simpan `track_id`, lokasi (dalam atau luar area), dan aksi (IN atau OUT) di koleksi people dalam database collection `people`.
- Perbarui data agregasi (inside_count, in_count, out_count) pada koleksi `counter` untuk memberikan statistik terbaru.

Relasi antara Tabel/`Collection` Deteksi (`people`dan`counter`) dan Tabel Konfigurasi Area Polygon/`area`:
- Relasi Langsung: Collection `area` menyimpan data konfigurasi area deteksi berupa koordinat poligon. Data ini digunakan sebagai referensi untuk memvalidasi posisi objek dari hasil deteksi.
- Proses Validasi: Setiap kali manusia terdeteksi, sistem memeriksa apakah koordinatnya berada di dalam poligon dari area. Proses ini melibatkan algoritma seperti point-in-polygon.
- Kebergantungan: Deteksi dan pelacakan manusia tidak dapat dilakukan tanpa data konfigurasi area (dari koleksi area), karena data ini menentukan apakah seseorang dianggap berada di dalam (IN) atau di luar (OUT) area pengawasan. Lalu setiap orang yang terdeteksi akan tersimpan juga bersamaan dengan `track_id`, `action` dan `  
datetime`, setiap data pada collection `counter` menyimpan `area_coords`

---


## 📂 Folder Structure

```
/project-root
│── scr/
│   │── main.py             # Flask Backend
│   │── tracker1.py         # Tracking Logic
│   │── dashboard.py        # Streamlit Frontend
│   │── yolo11l.pt          # Model YOLO
│   │── best-1.pt           # Model YOLO hasil training 1
│   │── best-2.pt           # Model YOLO hasil training 2
│── requirements.txt        # Dependencies
│── Dockerfile              # Docker Build Config
│── docker-compose.yml      # Docker Compose Config
```

---

## Deployment dengan Docker
### 1️⃣ Build dan Jalankan dengan Docker Compose
```bash
docker-compose up --build
```
Aplikasi Flask dan Streamlit akan berjalan bersamaan.

### 2️⃣ Stop Aplikasi
```bash
docker-compose down
```

Akses aplikasi di **localhost**:
- Flask (Backend): [http://localhost:5000](http://localhost:5000) (Untuk API)
- Streamlit (Frontend): [http://localhost:8501](http://localhost:8501) (Dashboard)

---

## Installation (TANPA DOCKER)
### 1️⃣ Setup MongoDB Atlas (Optional: sudah dapat dijalankan menggunakan client bawaan saya)
1. **Buat Cluster MongoDB Atlas** di [MongoDB Atlas](https://www.mongodb.com/atlas/database).
2. **Buat Database & Collection**:
   - Database: `people_tracking`
   - Collection: `area`, `people`, `counter`
3. **Dapatkan MongoDB URI** dan update di `main.py`:
   ```python
   client = pymongo.MongoClient("mongodb+srv://<username>:<password>@cluster.mongodb.net/people_tracking")
   ```

### 2️⃣ Install Dependencies (Opsional, Jika Tanpa Docker)
```bash
pip install -r requirements.txt
```

### 3️⃣ Jalankan Aplikasi (Opsional, Jika Tanpa Docker)
Jalankan Flask:
```bash
python src/main.py
```
Jalankan Streamlit:
```bash
streamlit run src/dashboard.py
```

Akses aplikasi di **localhost**:
- Flask (Backend): [http://localhost:5000](http://localhost:5000)
- Streamlit (Frontend): [http://localhost:8501](http://localhost:8501)

---

## 📌 Dataset dan Model YOLO
Model **best-1.pt** dan **best-2.pt** adalah hasil training **YOLOv11** menggunakan dataset dari **CCTV Malioboro**:
- **Sumber Data CCTV**:
  - [Nol Km Utara](https://cctvjss.jogjakota.go.id/malioboro/NolKm_Utara.stream/playlist.m3u8)
  - [Pasar Beringharjo](https://cctvjss.jogjakota.go.id/malioboro/Malioboro_30_Pasar_Beringharjo.stream/playlist.m3u8)
- **Jumlah Data**:
  - **Train**: 234 data
  - **Validation**: 45 data
  - **Test**: 11 data
- **Pengujian**: Menggunakan video feed dari **[Depan DPRD Malioboro](https://cctvjss.jogjakota.go.id/malioboro/Malioboro_4_Depan_DPRD.stream/playlist.m3u8)**

---

## 🔗 API Endpoints
| Method | Endpoint            | Description                          |
|--------|---------------------|--------------------------------------|
| GET    | `/video_feed`       | Menampilkan video streaming         |
| GET    | `/api/stats/` `/api/stats/live`        | Mendapatkan statistik deteksi       |
| POST   | `/api/save_polygon` | Menyimpan area deteksi ke MongoDB   |


---

## 📌 Notes
- Pastikan Anda memiliki akses ke **MongoDB Atlas** sebelum menjalankan aplikasi. (Sudah saya buka akses untuk siapapun)
- Gunakan **Docker Compose** untuk mempermudah deployment.
- Model YOLO (`yolo11l.pt`, `best-1.pt`, dan `best-2.pt`) sudah harus ada di folder `src/` sebelum dijalankan.

---

## ✨ Credits
Developed by **Daffa Aminuddin** 🚀

