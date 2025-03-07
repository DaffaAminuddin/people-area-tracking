import cv2  # Pastikan OpenCV diimpor
import numpy as np
from ultralytics.solutions.solutions import BaseSolution
from ultralytics.utils.plotting import Annotator, colors
from datetime import datetime
from pymongo import MongoClient
import time

BaseSolution(verbose=False)

# Koneksi ke MongoDB Atlas
cluster = "mongodb+srv://meynerbilly:FsCVEMNCKP9IOFUI@test.svekd.mongodb.net/?retryWrites=true&w=majority&appName=test"
client = MongoClient(cluster)
db = client.detection  # Ganti dengan nama database yang sesuai
people = db.people  # Ganti dengan nama koleksi yang sesuai
counter  = db.counter

class ObjectCounter(BaseSolution):

    def __init__(self, **kwargs):
        """Initializes the ObjectCounter class for real-time object counting in video streams."""
        super().__init__(**kwargs)

        self.in_count = 0  # Counter for objects moving inward
        self.out_count = 0  # Counter for objects moving outward
        self.counted_ids = []  # List of IDs of objects that have been counted
        self.saved_ids = []  # List of IDs already saved to CSV
        self.classwise_counts = {}  # Dictionary for counts, categorized by object class
        self.region_initialized = False  # Bool variable for region initialization

        self.show_in = self.CFG.get("show_in", True)
        self.show_out = self.CFG.get("show_out", True)
        self.last_check_time = time.time()  # Catat waktu terakhir untuk pemeriksaan
        self.check_interval = 1.0  # Interval pemeriksaan (dalam detik)

    def save_label_to_mongodb(self, track_id, label, action):
        try:
            # Mendapatkan waktu saat ini
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Data untuk koleksi 'people'
            data = {
                "track_id": track_id,
                "label": label,
                "action": action,
                "date": current_time.split()[0],
                "time": current_time.split()[1]
            }

            # Menghitung jumlah inside
            inside_count = max(0, self.in_count - self.out_count)

            # Data untuk koleksi 'counter'
            counter_data = {
                "polygon_coords": self.region,  # Gunakan koordinat poligon
                "inside_count": inside_count,
                "in_count": self.in_count,
                "out_count": self.out_count,
                "timestamp": current_time  # Tambahkan waktu untuk tracking
            }

            # Menyimpan data ke MongoDB
            people.insert_one(data)  # Koleksi 'people'
            counter.insert_one(counter_data)  # Koleksi 'counter'

            # Tandai setiap aksi untuk debugging
            print(f"Data berhasil disimpan ke MongoDB (people): {data}")
            print(f"Data berhasil disimpan ke MongoDB (counter): {counter_data}")
        except Exception as e:
            # Print untuk menangkap kesalahan
            print(f"Terjadi kesalahan saat menyimpan ke MongoDB: {e}")

    def count_objects(self, current_centroid, track_id, prev_position, cls):
        """
        Counts objects entering, exiting, and ensures inside count is accurate.
        """
        if prev_position is None:
            return

        action = None
        polygon = self.Polygon(self.region)

        # Periksa apakah centroid saat ini berada di dalam poligon
        if polygon.contains(self.Point(current_centroid)):
            if track_id not in self.counted_ids:
                self.in_count += 1  # Tambahkan jumlah masuk
                action = "IN"
                self.counted_ids.append(track_id)
        # Periksa jika centroid sebelumnya berada di dalam dan sekarang keluar
        elif track_id in self.counted_ids and not polygon.contains(self.Point(current_centroid)):
            self.out_count += 1  # Tambahkan jumlah keluar
            action = "OUT"
            self.counted_ids.remove(track_id)

        # Simpan ke MongoDB atau tampilkan log
        if action:
            label = f"{self.names[cls]} ID: {track_id}"
            self.save_label_to_mongodb(track_id, label, action)

    def store_classwise_counts(self, cls):
        """Initialize class-wise counts for a specific object class if not already present."""
        if self.names[cls] not in self.classwise_counts:
            self.classwise_counts[self.names[cls]] = {"IN": 0, "OUT": 0}

    def display_counts(self, im0):
        """
        Displays object counts (IN, OUT, and INSIDE) on the frame.
        """
        # Hitung jumlah INSIDE
        inside_count = max(0, self.in_count - self.out_count)

        # Buat label untuk tampilan
        labels_dict = {
            "Inside": f"{inside_count}",
            "IN": f"{self.in_count}",
            "OUT": f"{self.out_count}"
        }

        # Tampilkan data pada frame
        self.annotator.display_analytics(im0, labels_dict, (104, 31, 17), (255, 255, 255), 10)

        # Beri label untuk objek yang berada di dalam
        for track_id in self.track_ids:
            if track_id in self.counted_ids:
                label = f"ID:{track_id} (Inside)"
                self.annotator.box_label(self.boxes[self.track_ids.index(track_id)], label=label, color=(255, 255, 0))

    def count(self, im0):
        """Processes input frames, tracks objects, and calculates IN, OUT, and INSIDE counts."""
        if not self.region_initialized:
            self.initialize_region()
            self.region_initialized = True

        self.annotator = Annotator(im0, line_width=self.line_width)
        self.extract_tracks(im0)
        self.annotator.draw_region(reg_pts=self.region, color=(104, 0, 123), thickness=self.line_width * 2)

        # Proses setiap objek yang terdeteksi
        for box, track_id, cls in zip(self.boxes, self.track_ids, self.clss):
            self.store_tracking_history(track_id, box)
            self.store_classwise_counts(cls)

            label = f"{self.names[cls]} ID: {track_id}"
            self.annotator.box_label(box, label=label, color=colors(cls, True))

            current_centroid = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
            prev_position = self.track_history[track_id][-2] if len(self.track_history[track_id]) > 1 else None
            self.count_objects(current_centroid, track_id, prev_position, cls)

        # Cek apakah interval waktu sudah terpenuhi untuk memvalidasi objek di dalam poligon
        current_time = time.time()
        if current_time - self.last_check_time >= self.check_interval:
            self.last_check_time = current_time  # Perbarui waktu terakhir pemeriksaan

            # Hitung ulang jumlah objek di dalam poligon
            inside_ids = [track_id for track_id in self.counted_ids if any(
                self.Polygon(self.region).contains(self.Point(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)))
                for box in self.boxes if track_id in self.track_ids
            )]

            if not inside_ids:  # Jika tidak ada objek di dalam poligon
                self.in_count = self.out_count  # Set INSIDE = 0

        self.display_counts(im0)
        self.display_output(im0)

        return im0



