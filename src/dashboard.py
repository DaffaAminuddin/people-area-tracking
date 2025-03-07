import streamlit as st
from streamlit_drawable_canvas import st_canvas
from streamlit_option_menu import option_menu
import cv2
from PIL import Image
import requests
import time

# Konfigurasi agar halaman full-width
st.set_page_config(layout="wide")

# CSS untuk menghilangkan padding default Streamlit
st.markdown(
    """
    <style>
        .block-container {
            padding: 10 !important;
            margin: 0 !important;
        }
        .stApp {
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Membuat Menu di Sidebar
with st.sidebar:
    pilihan = option_menu(
        "Main Menu",  # Judul Menu
        ["Home", "Stat (API)", "Setting Area"],  # Opsi Menu
        icons=["house", "bar-chart", "gear"],  # Ikon Menu (opsional)
        menu_icon="cast",  # Ikon untuk judul menu
        default_index=0  # Indeks default
    )

# URL Flask endpoints
video_url = "http://localhost:5000/video_feed"
stats_url = "http://localhost:5000/api/stats/"
live_stats_url = "http://localhost:5000/api/stats/live"
# URL endpoint untuk menyimpan poligon
save_polygon_url = "http://localhost:5000/api/save_polygon"

# URL Video Streaming
stream_url = "https://cctvjss.jogjakota.go.id/malioboro/Malioboro_4_Depan_DPRD.stream/playlist.m3u8"

if pilihan == "Home":
    st.title("People Counting and Tracking: LIVE MALIOBORO DEPAN DPRD")

    # Menampilkan video streaming menggunakan tag HTML
    st.markdown(
        f"""
        <div style="text-align:center;">
            <iframe src="{video_url}" width="1020" height="500" frameborder="0" allowfullscreen></iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info("Saat berganti menu, Harap tunggu berberapa saat jika tidak muncul UI (video feed, Stat, dan Setting area)")

elif pilihan == "Stat (API)":
    # Placeholder untuk statistik
    st.title("Statistik")
    stats_placeholder = st.empty()  # Gunakan st.empty() untuk fleksibilitas pembaruan


    def fetch_stats():
        """
        Mengambil data statistik dari backend melalui polling.
        """
        try:
            # Mengambil data statistik jumlah IN dan OUT
            stats_response = requests.get(stats_url)
            live_stats_response = requests.get(live_stats_url)

            if stats_response.status_code == 200 and live_stats_response.status_code == 200:
                stats_data = stats_response.json()
                live_stats_data = live_stats_response.json()
                return stats_data, live_stats_data
            else:
                st.warning("Gagal mengambil data statistik. Periksa backend Anda.")
                return {}, {}
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            return {}, {}


    # Loop untuk memperbarui statistik secara periodik
    while True:
        stats_data, live_stats_data = fetch_stats()

        # Perbarui isi dalam placeholder dengan layout yang diperbarui
        with stats_placeholder.container():
            st.markdown("---")  # Garis pemisah untuk kerapihan
            st.markdown("#### 📊 **Statistik Terkini** (/api/stats/live dan /api/stats)")

            col1, col2, col3 = st.columns(3)  # Mengatur statistik dalam 3 kolom
            with col1:
                st.info(f"**Jumlah Orang di Dalam Area (INSIDE):** {live_stats_data.get('inside_count', 0)}")
            with col2:
                st.success(f"**Jumlah Orang Masuk (IN):** {stats_data.get('in_count', 0)}")
            with col3:
                st.warning(f"**Jumlah Orang Keluar (OUT):** {stats_data.get('out_count', 0)}")

            st.write(f"**Diupdate pada:** {live_stats_data.get('timestamp', 'Tidak tersedia')}")

            st.markdown("#### 🧑‍🧑‍🧒 **People Tracking**")

            kol1, kol2 = st.columns(2)  # Mengatur statistik dalam 3 kolom
            with kol1:
                st.info(f"**Last Track ID:** {live_stats_data.get('track_id', 0)}")
            with kol2:
                st.info(f"**Last Action:** {live_stats_data.get('action', 0)}")

            st.write(f"**Diupdate pada:** {live_stats_data.get('time', 'Tidak tersedia')}")
        # Tunggu 5 detik sebelum polling berikutnya
        time.sleep(5)

elif pilihan == "Setting Area":
    st.title("Atur Poligon")

    # Resolusi yang digunakan di backend
    FRAME_WIDTH = 1020
    FRAME_HEIGHT = 500

    # Fungsi untuk mengambil frame asli dari video stream dan resize agar sesuai dengan backend
    def get_frame_from_stream(url):
        cap = cv2.VideoCapture(url)
        success, frame = cap.read()
        cap.release()  # Pastikan release agar tidak terkunci
        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))  # Resize agar sesuai dengan backend
            return frame
        else:
            st.error("Gagal mengambil frame dari stream.")
            return None


    # Simpan frame di session_state agar tidak perlu diambil berulang kali
    if "frame" not in st.session_state:
        st.session_state.frame = get_frame_from_stream(stream_url)

    # Gunakan frame dari session_state
    frame = st.session_state.frame

    # Pastikan frame tersedia sebelum lanjut
    if frame is not None:
        frame_image = Image.fromarray(frame)

        st.markdown("### Gambar Poligon pada Frame")
        st.info("Buat poligon baru pada frame dibawah, Klik untuk membuat titik baru (minimal 3 titik) lalu klik kanan menutup ke titik awal, lalu simpan poligon")

        # Input nama area
        area_name = st.text_input("Masukan Nama Area disini:", value="nama_area")

        # Atur canvas agar ukurannya sama dengan backend (1020x500)
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="blue",
            background_image=frame_image,
            height=FRAME_HEIGHT,  # Gunakan tinggi sesuai backend
            width=FRAME_WIDTH,  # Gunakan lebar sesuai backend
            drawing_mode="polygon",
            key="canvas",
        )

        # Ambil koordinat poligon yang digambar
        if canvas_result.json_data is not None:
            coords = []
            for obj in canvas_result.json_data.get("objects", []):
                if obj["type"] == "path":
                    path = obj["path"]
                    valid_coords = [
                        (round(point[1]), round(point[2]))
                        for point in path if isinstance(point, list) and len(point) == 3
                    ]
                    coords.extend(valid_coords)

            st.markdown("### Koordinat Poligon")
            if coords:
                st.write("Koordinat yang digambar:", coords)
            else:
                st.write("Belum ada poligon yang digambar.")

            # Simpan koordinat ke database
            if st.button("Simpan Poligon"):
                if area_name.strip() == "":
                    st.error("Nama area tidak boleh kosong.")
                elif len(coords) < 3:
                    st.error("Poligon membutuhkan setidaknya 3 titik untuk validasi.")
                else:
                    data = {
                        "area_name": area_name,
                        "polygon_coords": coords
                    }
                    try:
                        response = requests.post(save_polygon_url, json=data)
                        if response.status_code == 200:
                            st.success("Poligon berhasil disimpan ke database!")
                        else:
                            st.error(f"Gagal menyimpan poligon: {response.text}")
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat menyimpan poligon: {e}")

    else:
        st.error("Tidak dapat menampilkan frame.")

    st.info("Saat berganti menu, Harap tunggu berberapa saat jika tidak muncul UI (video feed, Stat, dan Setting area)")

