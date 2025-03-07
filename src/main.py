import os
import sys
import subprocess
from flask import Flask, Response, jsonify, request
import cv2
import numpy as np
from pymongo import MongoClient
from tracker1 import ObjectCounter  # Gunakan tracker yang sudah ada


# Koneksi ke MongoDB Atlas
cluster = "mongodb+srv://meynerbilly:FsCVEMNCKP9IOFUI@test.svekd.mongodb.net/?retryWrites=true&w=majority&appName=test"
client = MongoClient(cluster)
db = client.detection
people = db.people
counterdb  = db.counter
area_collection = db.area

app = Flask(__name__)

# Fungsi untuk mengambil koordinat polygon terbaru dari MongoDB
def get_latest_polygon_coords():
    try:
        # Cari dokumen dengan ID terbaru (dokumen terakhir yang diinput ke MongoDB)
        area_data = area_collection.find_one(sort=[("_id", -1)])  # Urutkan berdasarkan _id terbaru
        if area_data and "polygon_coords" in area_data:
            return area_data["polygon_coords"]
        else:
            raise ValueError("Polygon coordinates not found in the latest document.")
    except Exception as e:
        print(f"Error retrieving polygon coordinates: {e}")
        return None

# Ambil koordinat poligon terbaru
polygon_coords = get_latest_polygon_coords()

# Pastikan koordinat tidak kosong sebelum melanjutkan
if not polygon_coords:
    raise ValueError("Polygon coordinates could not be loaded. Check your MongoDB collection.")


# URL Stream M3U8 dari CCTV Jogja
stream_url = "https://cctvjss.jogjakota.go.id/malioboro/Malioboro_4_Depan_DPRD.stream/playlist.m3u8"
# stream_url = "dprd.mp4"


# Inisialisasi ObjectCounter
# polygon_coords = [(547, 235), (705, 226), (734, 305), (571, 325)]
# polygon_coords = [(767,287), (902, 299), (878, 374), (732,355)] # default
counter = ObjectCounter(
    region=polygon_coords,
    model="yolo11m.pt",
    classes=[0],  # Deteksi hanya orang
    show_in=True,
    show_out=True,
    line_width=2,
)

def generate_frames():
    cap = cv2.VideoCapture(stream_url)
    polygon_np = np.array(polygon_coords, np.int32).reshape((-1, 1, 2))  # Format OpenCV
    polygon_color = (120, 200, 255)  # Warna poligon
    opacity = 0.5  # Transparansi

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Resize frame untuk ditampilkan
        frame = cv2.resize(frame, (1020, 500))

        # Tambahkan overlay transparan untuk poligon
        overlay = frame.copy()
        cv2.fillPoly(overlay, [polygon_np], polygon_color)
        frame = cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0)

        # Tambahkan garis pada poligon
        cv2.polylines(frame, [polygon_np], isClosed=True, color=(0, 255, 0), thickness=2)

        # Proses frame dengan ObjectCounter
        frame = counter.count(frame)

        # Tampilkan jumlah orang di dalam poligon
        inside_count = counter.in_count - counter.out_count  # Hitung jumlah di dalam poligon
        text = f"Inside: {max(0, inside_count)}"
        cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Encode frame ke format JPG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats/', methods=['GET'])
def get_stats():
    """
    Endpoint untuk mendapatkan jumlah orang masuk (IN) dan keluar (OUT) dari area poligon.
    """
    try:
        latest_data = counterdb.find_one(
            sort=[('_id', -1)],
            projection={"in_count": 1, "out_count": 1}
        )

        response = {
            "in_count": latest_data.get("in_count", 0) if latest_data else 0,
            "out_count": latest_data.get("out_count", 0) if latest_data else 0
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500


@app.route('/api/stats/live', methods=['GET'])
def get_live_stats():
    """
    Endpoint untuk mendapatkan jumlah orang di dalam area poligon (inside_count).
    """
    try:
        # Pastikan `counter` adalah koleksi MongoDB
        latest_data = counterdb.find_one(sort=[('_id', -1)])  # Ambil data terbaru berdasarkan ID
        people_data = people.find_one(sort=[('_id', -1)])
        if latest_data:
            response = {
                "timestamp": latest_data.get("timestamp", 0),
                "inside_count": latest_data.get("inside_count", 0),
                "track_id": people_data.get("track_id", 0),
                "action": people_data.get("action", 0),
                "time": people_data.get("time", 0)
            }
        else:
            response = {
                "inside_count": 0
            }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

# Endpoint untuk menyimpan data poligon ke MongoDB
@app.route('/api/save_polygon', methods=['POST'])
def save_polygon():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging

        area_name = data.get("area_name")
        polygon_coords = data.get("polygon_coords")

        if not area_name or not polygon_coords:
            return jsonify({"error": "Invalid data. Ensure 'area_name' and 'polygon_coords' are provided."}), 400

        # Save data to MongoDB
        area_data = {
            "area_name": area_name,
            "polygon_coords": polygon_coords
        }
        area_collection.insert_one(area_data)

        print("Polygon data saved successfully. Restarting server...")

        # Restart server
        restart_server()

        return jsonify({"message": "Polygon data saved successfully"}), 200
    except Exception as e:
        print(f"Error saving polygon: {e}")  # Cetak error ke terminal
        return jsonify({"error": "Failed to save polygon data"}), 500


def restart_server():
    """Matikan server lalu jalankan ulang dengan python main.py"""
    print("Stopping server...")

    # Jalankan ulang backend dalam proses baru
    subprocess.Popen(["python", "./src/main.py"])

    # Matikan proses yang sedang berjalan
    os._exit(0)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
