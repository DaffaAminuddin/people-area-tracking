# People Detection & Tracking System

## 📌 Overview
sistem deteksi dan pelacakan orang menggunakan **YOLO** yang dikembangkan dengan **Flask** sebagai backend dan **Streamlit** sebagai frontend. Sistem ini juga menyimpan area deteksi ke **MongoDB Atlas** untuk integrasi API.

---

## ⚙️ System Architecture

1. **Backend (Flask - `main.py`)**
   - Menyediakan API untuk streaming video dengan deteksi objek.
   - Menyimpan dan mengambil area deteksi dari MongoDB Atlas.
   - Menghitung statistik orang masuk, keluar, dan yang berada di dalam area.

2. **Frontend (Streamlit - `dashboard.py`)**
   - Menampilkan video streaming dari backend.
   - Memvisualisasikan statistik deteksi orang.
   - Memungkinkan pengguna menggambar area deteksi dan menyimpannya ke database.

3. **Database (MongoDB Atlas - NoSQL)**
   - **Collection `area`**: Menyimpan koordinat poligon untuk area deteksi.
   - **Collection `people`**: Menyimpan `track_id` orang dan aksi (`IN` atau `OUT`).
   - **Collection `counter`**: Menyimpan data terbaru dari `inside_count`, `in_count`, dan `out_count`.

---

## 📂 Folder Structure

```
/project-root
│── scr/
│   │── main.py             # Flask Backend
│   │── tracker1.py         # Tracking Logic
│   │── dashboard.py        # Streamlit Frontend
│   │── yolo11l.pt          # Model YOLO
│   │── best-1.pt           # Model YOLO alternatif
│   │── best-2.pt           # Model YOLO alternatif kedua
│   │── dprd.mp4            # Sample Video
│── requirements.txt        # Dependencies
│── Dockerfile              # Docker Build Config
│── docker-compose.yml      # Docker Compose Config
```

---

## 🚀 Deployment dengan Docker
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
- Flask (Backend): [http://localhost:5000](http://localhost:5000)
- Streamlit (Frontend): [http://localhost:8501](http://localhost:8501)

---

## 🛠 Installation
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

## 🎯 Features
✔ **YOLO-Based People Detection**  
✔ **Real-time Tracking**  
✔ **Custom Detection Area (Polygon)**  
✔ **MongoDB Atlas Integration**  
✔ **Web Dashboard with Streamlit**  
✔ **Containerized with Docker**  

---

## 📌 Notes
- Pastikan Anda memiliki akses ke **MongoDB Atlas** sebelum menjalankan aplikasi. (Sudah saya buka akses untuk siapapun)
- Gunakan **Docker Compose** untuk mempermudah deployment.
- Model YOLO (`yolo11l.pt`, `best-1.pt`, dan `best-2.pt`) sudah harus ada di folder `src/` sebelum dijalankan.

---

## ✨ Credits
Developed by **Daffa Aminuddin** 🚀

